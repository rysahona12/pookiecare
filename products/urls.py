from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products/', views.products_list_view, name='products_list'),
    path('product/<uuid:product_id>/', views.product_detail_view, name='product_detail'),
]
