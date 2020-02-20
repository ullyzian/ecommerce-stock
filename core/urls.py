from django.urls import path

from .views import (
    ItemsView, OrderSummaryView, SearchResultsView, add_to_cart,
    checkout_detail, home, item_detail, privacy_policy, remove_from_cart,
    category_list)

app_name = 'core'

urlpatterns = [
    path('', home, name='home'),
    path('products/', ItemsView.as_view(), name='products'),
    path('detail/<slug>/', item_detail, name='detail'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('add-to-cart/<slug>', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>', remove_from_cart, name='remove-from-cart'),
    path('checkout/', checkout_detail, name='checkout'),
    path('privacy-policy/', privacy_policy, name='privacy-policy'),
    path('search/', SearchResultsView.as_view(), name='search'),
    path('category-list/<slug>', category_list, name='category-list'),
]
