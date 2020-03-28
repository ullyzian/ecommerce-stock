from zipfile import ZipFile
import requests
import os
import stripe
import boto3
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import ListView, View
from django.http import JsonResponse, FileResponse, HttpResponse
from django.conf import settings

from .models import Item, Order, OrderItem, Category, Payment, UserProfile
from .forms import PaymentForm


stripe.api_key = settings.STRIPE_SECRET_KEY


def download_file(request, item_id):
    item = Item.objects.get(id=item_id)
    url = item.image_paid.url
    filename = url[url.rfind("/") + 1:].split("?")[0]
    filepath = 'media/images/' + filename
    file_response = requests.get(url)

    f1 = open(filepath, 'wb')
    f1.write(file_response.content)
    f1.close()

    response = HttpResponse(open(filepath, 'rb'),
                            content_type="application/force-download")
    response['Content-Disposition'] = f'attachment;filename="{filename}"'
    os.remove(filepath)
    return response


def home(request):
    return render(request, 'home.html')


@login_required
def saved_cards_list(request):
    userprofile = request.user.userprofile
    if userprofile.one_click_purchasing:
        cards = stripe.Customer.list_sources(
            userprofile.stripe_customer_id,
            limit=3,
            object='card'
        )
        card_list = cards['data']
        if len(card_list) > 0:
            context = {
                'card': card_list[0]
            }
    return render(request, 'account/saved_cards.html', context)


@login_required
def purchases_list(request):
    order_qs = Order.objects.filter(user=request.user, ordered=True)
    if order_qs.exists():
        order = order_qs.order_by('-id')
        return render(request, 'account/purchases.html', {'orders': order})
    return render(request, 'account/purchases.html')


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        if Order.objects.filter(user=self.request.user, ordered=False).exists():
            order = Order.objects.get(user=self.request.user, ordered=False)
            if not order.items.exists():
                return redirect('core:order-summary')
        else:
            return redirect('core:products')

        context = {
            'order': order,
        }

        userprofile = self.request.user.userprofile
        if userprofile.one_click_purchasing:
            cards = stripe.Customer.list_sources(
                userprofile.stripe_customer_id,
                limit=3,
                object='card'
            )
            card_list = cards['data']
            if len(card_list) > 0:
                context.update({
                    'card': card_list[0]
                })

        return render(self.request, 'payment.html', context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        zip_filename = f'{order.user}-{order.id}.zip'
        zip_path = 'media/zip/' + zip_filename
        s3Resource = boto3.resource('s3')

        with ZipFile(zip_path, 'w') as zipObj:
            for order_item in order.items.all():
                url = order_item.item.image_paid.url
                filename = url[url.rfind("/") + 1:].split("?")[0]
                filepath = 'media/images/' + filename
                file_response = requests.get(url)

                f1 = open(filepath, 'wb')
                f1.write(file_response.content)
                f1.close()

                zipObj.write(filepath)
                os.remove(filepath)

        s3Resource.meta.client.upload_file(
            zip_path,
            settings.AWS_STORAGE_BUCKET_NAME,
            f'zip/{zip_filename}'
        )
        order.zip = f'/zip/{zip_filename}'

        payment_method = self.request.POST.get('payment', '')
        if (payment_method == 'paypal'):
            # Assign the payment to order and order items
            for order_item in order.items.all():
                order_item.ordered = True
                order_item.save()
            order.ordered = True
            order.save()
            return render(self.request, "payment_completed.html")
        else:
            form = PaymentForm(self.request.POST)
            userprofile = UserProfile.objects.get(user=self.request.user)

            if form.is_valid():
                token = form.cleaned_data.get('stripeToken')
                save = form.cleaned_data.get('save')
                use_default = form.cleaned_data.get('use_default')

                if save:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

                amount = int(order.get_total() * 100)

            try:
                if use_default or save:
                    charge = stripe.Charge.create(
                        amount=amount,
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    charge = stripe.Charge.create(
                        amount=amount,
                        currency="usd",
                        source=token
                    )
                # Create an payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                # Assign the payment to order and order items
                for order_item in order.items.all():
                    order_item.ordered = True
                    order_item.save()
                order.ordered = True
                order.payment = payment
                order.save()

            except stripe.error.CardError as e:
                # Since it's a decline, stripe.error.CardError will be caught
                body = e.json_body
                err = body.get('error', {})
                messages.error(self.request, f"{err.get('message')}")
                return redirect("/")

            except stripe.error.RateLimitError:
                messages.error(self.request, "Rate limit error")
                return redirect("/")

            except stripe.error.InvalidRequestError:
                messages.error(self.request, "Invalid parametrs")
                return redirect("/")

            except stripe.error.AuthenticationError:
                messages.error(self.request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError:
                messages.error(self.request, "Network error")
                return redirect("/")

            except stripe.error.StripeError:
                messages.error(self.request,
                               "Something wen wrong. You were not charged.")
                return redirect("/")

            except Exception:
                messages.error(self.request, "Serious error is occured.")
                return redirect("/")
                # send email with bug

            return render(self.request, "payment_completed.html")


@login_required
def download_zip(request):
    order_qs = Order.objects.filter(user=request.user, ordered=True)
    if order_qs.exists():
        order = order_qs.order_by('-id')[0]
    url = order.zip.url
    zip_name = url[url.rfind("/") + 1:].split("?")[0]
    zip_path = 'media/zip/' + zip_name
    file_response = requests.get(url)

    f1 = open(zip_path, 'wb')
    f1.write(file_response.content)
    f1.close()

    response = HttpResponse(open(zip_path, 'rb'),
                            content_type="application/force-download")
    response['Content-Disposition'] = f'attachment;filename="{zip_name}"'
    os.remove(zip_path)
    return response


@login_required
def account_info(request):
    context = {
        'profile': UserProfile.objects.filter(user=request.user)
    }
    return render(request, 'account/account_info.html', context)


class ItemsView(ListView):
    model = Item
    paginate_by = 9
    template_name = 'items_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        if Order.objects.filter(
                user=self.request.user, ordered=False).exists():
            order = Order.objects.get(user=self.request.user, ordered=False)
        else:
            return render(self.request, 'order_summary.html')
        context = {
            'object': order.items.all(),
            'order': order,
        }
        return render(self.request, 'order_summary.html', context)


def category_list(request, slug):
    category = get_object_or_404(Category, slug=slug)
    context = {
        'object_list': Item.objects.filter(category__exact=category),
        'categories': Category.objects.all()
    }
    return render(request, 'items_list.html', context)


def filter_category(request):
    category = Category.get()
    data = {
        'filter_category': Item.category.filter(category__iexact=category)
    }
    return JsonResponse(data)


class SearchResultsView(ListView):
    model = Item
    template_name = 'items_list.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        return Item.objects.filter(
            Q(title__icontains=query) | Q(category__title__icontains=query)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


def item_detail(request, slug):
    item = get_object_or_404(Item, slug=slug)
    in_cart = False

    if request.user.is_authenticated:
        qs = Order.objects.filter(user=request.user, ordered=False)
        if qs.exists():
            order = qs[0]
            if order.items.filter(item__slug=item.slug).exists():
                in_cart = True
    context = {
        'object': item,
        'in_cart': in_cart,
    }
    return render(request, 'item_detail.html', context)

# ============================================================================


# adding item to cart. Give function a request and slug(Primary key for
# Generic views)
@login_required(redirect_field_name='/')
def add_to_cart(request, slug):

    # Getting an Item object where item slug match with requesting item slug.
    # Otherwise get a 404 error
    item = get_object_or_404(Item, slug=slug)

    # Checking if an order item exist, if not, then create.
    # (second parameter "created") added because .get_or_create method
    # returns (object, created(Boolean)) tuple.
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )

    # Querying Orders where user = requested user and where
    #  ordered item = False
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    # If any of active orders exists
    if order_qs.exists():
        # Getting first active order
        order = order_qs[0]

        # If order item already exists in order
        if order.items.filter(item__slug=item.slug).exists():
            messages.info(request, 'This item is already in cart!')
        # If order item is not in order
        else:
            # Adding an order item to order
            order.items.add(order_item)
            messages.info(request, 'This item has been added to cart!')
    # If active orders does not exists
    else:
        # Getting current date
        ordered_date = timezone.now()
        # Creating an order with parameters
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        # Adding order item to cart
        order.items.add(order_item)
        messages.info(
            request, 'Order has been created and item has been added!')

    return redirect("core:products")

# =============================================================================

# Removing item from cart. Give function a request and slug(Primary key for
# Generic views)


@login_required(redirect_field_name='/')
def remove_from_cart(request, slug):
    # Getting an Item object where item slug match with requesting item slug.
    # Otherwise get a 404 error
    item = get_object_or_404(Item, slug=slug)

    # Querying Orders where user = requested user and where
    # ordered item = False
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    # If any of active orders exists
    if order_qs.exists():
        # Getting first active order
        order = order_qs[0]
        # Checking if an order item exist, if not, then create.
        # (second parameter "created")added because .get_or_create method
        # returns (object, created(Boolean)) tuple.
        order_item = OrderItem.objects.filter(
            item=item,
            user=request.user,
            ordered=False,
        )[0]

        # If order item already exists in order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.delete()
            # order.items.remove(order_item)
            messages.info(request, 'Item removed from cart!')

        # If order item is not in order
        else:
            messages.info(request, 'Item does not in the cart to remove it!')
    # If no active orders exists
    else:
        messages.info(request, 'You do not have order to remove items!')

    return redirect("core:order-summary")

# ========================================================================


def privacy_policy(request):
    return render(request, 'privacy_policy.html')
