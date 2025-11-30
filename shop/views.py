from django.shortcuts import render
# generic views
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from django.test import RequestFactory
from django.http import JsonResponse
from django.db.models import Sum
from django.urls import reverse
from .serializers import *
from .models import *
import random
from .payment import orderPayment
from rest_framework import status
import json


# Product Views
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = None
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        serializer.save(is_active=True)
        
        
class ProductListAdminView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        serializer.save(is_active=True)
    

class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    
    # patch method for return messages: product updated successfully
    def patch(self, request, *args, **kwargs):
        response = super().patch(request, *args, **kwargs)
        return Response({'message': 'Product updated successfully', 'data': response.data}, status=response.status_code)
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return Response({'message': 'Product deleted successfully'}, status=response.status_code)
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    
# Order Views
class OrderCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # ---- Call your existing function ----
        # it needs a DRF request object, so use RequestFactory
        factory = RequestFactory()
        fake_request = factory.post("/", {})  # dummy request
        response = orderPayment(fake_request, order.id)

        # convert JsonResponse → Python dict
        data = json.loads(response.content)

        return Response({
            "order_id": order.id,
            "payment": data
        }, status=status.HTTP_201_CREATED)
        
        
class SellerView(generics.ListCreateAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    
class SellerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return Response({'message': 'Seller deleted successfully'}, status=response.status_code)
    

class BestOfferView(generics.ListAPIView):
    serializer_class = ProductBestSeleSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Product.objects.filter(is_best_offer=True).order_by('-id')[:5]


class BestSellerView(generics.ListAPIView):
    serializer_class = ProductBestSeleSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Product.objects.filter(is_best_seller=True).order_by('-id')[:5]
    
    

class DashboardView(generics.GenericAPIView):
    serializer_class = DashboardSerializer
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance={})
        return Response(serializer.data)


class LowStockProductView(generics.ListAPIView):
    serializer_class = LowStockProductSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return Product.objects.filter(stock__lte=1).order_by('name')
    
    def list(self, request, *args, **kwargs):
        # Use ListAPIView's built-in pagination/serialization then wrap the response
        response = super().list(request, *args, **kwargs)
        return Response({'message': 'Low stock products List successfully', 'data': response.data})
    
class TotalEarningsView(generics.GenericAPIView):
    serializer_class = TotalEarningsSerializer
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance={})
        return Response(serializer.data)
    
    
class AdminOrderListView(generics.ListAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = AdminOrderSerializer
    permission_classes = [permissions.IsAdminUser]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({'message': 'Order List successfully', 'data': response.data})
    
class AdminOrderDetailsView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    
    
class AdminOrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = AdminOrderSerializer
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Order status updated successfully', 'data': serializer.data})

class AdminOrderDetailsUpdateView(generics.RetrieveUpdateAPIView):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Order detail updated successfully', 'data': serializer.data})