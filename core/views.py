from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import ListView, View

from .models import Item, Order, OrderItem


def home(request):
    return render(request, 'home.html')


class ItemsView(ListView):
    model = Item
    paginate_by = 9
    template_name = 'items_list.html'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'object': order,
        }
        return render(self.request, 'order_summary.html', context)


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


class SearchResultsView(ListView):
    model = Item
    template_name = 'search.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        return Item.objects.filter(
            Q(title__icontains=query)
        )


def checkout_detail(request):
    return render(request, 'checkout_detail.html')


def privacy_policy(request):
    return render(request, 'privacy_policy.html')
