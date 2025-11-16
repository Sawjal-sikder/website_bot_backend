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
    path('best-sellers/', BestSellerView, name='best-sellers-sellers-list'),
    
    # Admin Dashboard
    path('dashboard/', DashboardView.as_view(), name='admin-dashboard'),
    path('low-stock-products/', LowStockProductView.as_view(), name='low-stock-products'),
    path('total-earnings/', TotalEarningsView.as_view(), name='total-earnings'),
    
    # Admin Order Management
    path('admin/orders/', AdminOrderListView.as_view(), name='admin-order-list'),
    path('admin/orderdetails/<int:pk>/', AdminOrderDetailsView.as_view(), name='admin-order-detail'),
    path('admin/orders/update/<int:pk>/', AdminOrderStatusUpdateView.as_view(), name='admin-order-update'),
    

]
