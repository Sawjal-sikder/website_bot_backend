from django.urls import path
from .views import *
from .payment import *

urlpatterns = [
    # seller urls
    path('sellers/', SellerView.as_view(), name='seller-list-create'),
    path('sellers/<int:pk>/', SellerDetailView.as_view(), name='seller-retrieve-update-destroy'),
    # product urls
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-retrieve-update-destroy'),
    # order urls
    path('orders/', OrderCreateView.as_view(), name='order-create'),
    # payment and webhook urls 
    path('payment/<int:orderId>/', orderPayment, name='order-payment'),
    path('webhook/', paymentWebhook, name='payment-webhook'),
    # best sellers
    path('best-seles/', BestSeleView, name='best-sellers-list'),
    path('best-sellers/', BestSellerView, name='best-sellers-sellers-list')
    

]
