from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Category, Item, Order, OrderItem, Payment, UserProfile


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    fields = (
        'title',
        'category',
        'price',
        'description',
        'image_free',
        'image_paid',
        'slug'
    )
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'ordered', 'ordered_date']
    list_filter = (
        ('items', admin.RelatedOnlyFieldListFilter),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['stripe_charge_id', 'user', 'amount']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'item', 'user', 'ordered']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['stripe_customer_id', 'user']
