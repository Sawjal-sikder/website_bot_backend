from datetime import datetime
from django.db.models.functions import TruncMonth
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db.models import Count, Sum
User = get_user_model()
from .models import *

# product serializer
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        

# order serializer
class OrderDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    
    class Meta:
        model = OrderDetail
        fields = ['id', 'product', 'product_name', 'quantity', 'price',]

class OrderSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'email', 'phone_number', 'address', 'delivery_date', 'total', 'status', 'payment_method', 'payment_status', 'notes', 'created_at', 'updated_at', 'order_details']
        read_only_fields = ['id','total', 'status', 'payment_status', 'payment_method', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        order_details_data = validated_data.pop('order_details')
        order = Order.objects.create(**validated_data)
        total = 0
        for detail_data in order_details_data:
            product = detail_data['product']
            quantity = detail_data['quantity']
            price = product.price * quantity
            total += quantity * price
            OrderDetail.objects.create(order=order, product=product, quantity=quantity, price=price)
        order.total = total
        order.save()
        return order
    
    
class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'
        
        
class DashboardSerializer(serializers.Serializer):
    current_user = serializers.CharField(read_only=True)
    total_products = serializers.IntegerField(read_only=True)
    total_users = serializers.IntegerField(read_only=True)
    total_orders = serializers.IntegerField(read_only=True)
    total_completed_orders = serializers.IntegerField(read_only=True)
    total_Cancelled_orders = serializers.IntegerField(read_only=True)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['current_user'] = self.context['request'].user.full_name or "Admin User"
        rep['total_products'] = Product.objects.count()
        rep['total_users'] = User.objects.count()
        rep['total_completed_orders'] = Order.objects.filter(status='Completed').count()
        rep['total_Cancelled_orders'] = Order.objects.filter(status='Cancelled').count()
        
        monthly_data = Order.objects.annotate(month =TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')
        monthly_orders = {}
        for data in monthly_data:
            month_name = data['month'].strftime('%B %Y')
            monthly_orders[month_name] = data['count']
        
        rep['total_orders'] = monthly_orders
        return rep

class LowStockProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'stock']
        
        
class TotalEarningsSerializer(serializers.Serializer):
    total_earnings = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        
        monthly_data = Order.objects.filter(payment_status='Paid').annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('total')).order_by('month')
        total_earnings = {}
        for data in monthly_data:
            month_name = data['month'].strftime('%B %Y')
            total_earnings[month_name] = data['total']
        
        rep['total_earnings'] = total_earnings
        return rep
