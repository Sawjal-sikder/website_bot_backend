from django.shortcuts import render
# generic views
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from django.http import JsonResponse
from django.db.models import Sum
from .serializers import *
from .models import *
import random

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
    
    def perform_create(self, serializer):
        serializer.save()
        
        
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
    

def BestSeleView(request):
    best_seles = (
        OrderDetail.objects
        .values('product__id', 'product__name', 'product__image')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:5]
    )

    best_seles_list = list(best_seles)
    existing_ids = [item['product__id'] for item in best_seles_list]

    # If fewer than 5, fill with products from Product table
    if len(best_seles_list) < 5:
        needed = 5 - len(best_seles_list)
        extra_products = (
            Product.objects
            .exclude(id__in=existing_ids)
            .values('id', 'name', 'image')
        )

        extra_products = random.sample(list(extra_products), min(needed, extra_products.count()))

        extra_products_data = [
            {'product__id': p['id'], 'product__name': p['name'], 'product__image': p['image']}
            for p in extra_products
        ]

        best_seles_list.extend(extra_products_data)

    return JsonResponse({'message': 'Best sellers view', 'data': best_seles_list}, status=200)


def BestSellerView(request):
    best_sellers = (
        OrderDetail.objects
        .values('product__seller__id', 'product__seller__title', 'product__seller__image')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:5]
    )
    data = list(best_sellers)
    existing_ids = [item['product__seller__id'] for item in data]
    # If fewer than 5, fill with sellers from Seller table
    if len(data) < 5:
        needed = 5 - len(data)
        extra_sellers = (
            Seller.objects
            .exclude(id__in=existing_ids)
            .values('id', 'title', 'image')
        )
        extra_sellers = random.sample(list(extra_sellers), min(needed, extra_sellers.count()))
        extra_sellers_data = [
            {'product__seller__id': s['id'], 'product__seller__title': s['title'], 'product__seller__image': s['image']}
            for s in extra_sellers
        ]
        data.extend(extra_sellers_data)
    return JsonResponse({'message': 'Best sellers view', 'data': data}, status=200)


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
