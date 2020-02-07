from django.contrib import admin

from .models import Category, Item, Order, OrderItem

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Category)
