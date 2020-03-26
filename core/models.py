from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    title = models.CharField(max_length=40)
    slug = models.SlugField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:category-list", kwargs={"slug": self.slug})

    class Meta:
        verbose_name_plural = _("Categories")


class Item(models.Model):
    valid_extensions = ['pdf', 'png', 'jpeg', 'jpg']

    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(default="Lorem")
    image_free = models.FileField(upload_to='images_free/', max_length=100,
                                  default="/static/img/animal.jpg", validators=[
                                      FileExtensionValidator(
                                          allowed_extensions=['pdf', 'png', 'jpeg', 'jpg'])
                                  ])
    image_paid = models.FileField(upload_to='images/', max_length=100,
                                  default="/static/img/animal.jpg", validators=[
                                      FileExtensionValidator(
                                          allowed_extensions=['pdf', 'png', 'jpeg', 'jpg'])
                                  ])
    slug = models.SlugField()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:detail", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={"slug": self.slug})


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.item.title


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.item.price
        return total


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)
