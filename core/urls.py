from django.urls import path

from .views import (
    ItemsView, OrderSummaryView, SearchResultsView, add_to_cart,
    PaymentView, home, item_detail, privacy_policy, remove_from_cart,
    category_list, account_info, download_zip, purchases_list, saved_cards_list, download_file)

app_name = 'core'

urlpatterns = [
    path('', home, name='home'),
    path('products/', ItemsView.as_view(), name='products'),
    path('detail/<slug>/', item_detail, name='detail'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>', remove_from_cart, name='remove-from-cart'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('privacy-policy/', privacy_policy, name='privacy-policy'),
    path('search/', SearchResultsView.as_view(), name='search'),
    path('category-list/<slug>/', category_list, name='category-list'),
    path('accounts/general/', account_info, name='account-info'),
    path('download/zip/', download_zip, name='download'),
    path('accounts/purchases/', purchases_list, name='purchases'),
    path('accounts/saved-cards/', saved_cards_list, name='saved-cards'),
    path('download/file/<item_id>', download_file, name='download-file')
]
