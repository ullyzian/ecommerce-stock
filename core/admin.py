from django.contrib import admin

from .models import Category, Item, Order, OrderItem, Payment


class ItemAdmin(admin.ModelAdmin):
    fields = (
        'title',
        'category',
        'price',
        'description',
        'image',
        'slug'
    )
    prepopulated_fields = {"slug": ("title",)}


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Payment)
