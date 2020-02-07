from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.shortcuts import reverse


class Category(models.Model):
    title = models.CharField(max_length=40)

    def __str__(self):
        return self.title

# ,dfsdjfhjsdkhfsdjfhjsdkhfsdjfhjsdkhfsdjfhjsdkhfsdjfhjsdkhfsdjfhjsdkhfsdjfhjsdkhfsdjfhjsdkhfsdjfhjsdkhf


class Item(models.Model):
    valid_extensions = ['pdf', 'png', 'jpeg', 'jpg']

    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(
        default="Lorem")
    image = models.FileField(
        upload_to='images/', max_length=100, blank=True, null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'png', 'jpeg', 'jpg'])])
    slug = models.SlugField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:detail", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={"slug": self.slug})


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
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
