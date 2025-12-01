from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products/', views.products_list_view, name='products_list'),
    path('product/<uuid:product_id>/', views.product_detail_view, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<uuid:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/item/<uuid:order_item_id>/update/', views.update_cart_item_view, name='update_cart_item'),
    path('cart/item/<uuid:order_item_id>/remove/', views.remove_from_cart_view, name='remove_cart_item'),
    path('checkout/', views.checkout_view, name='checkout'),
]
