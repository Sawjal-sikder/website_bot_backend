from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth
from django.contrib.auth import get_user_model
from django.forms import ValidationError
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
        
        today = datetime.now().date()
        last_six_months = []
        for i in range(5,-1,-1):
            month = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
            last_six_months.append(month)
            
               
        monthly_data = Order.objects.annotate(month =TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')
        monthly_dict = {item['month'].date(): item['count'] for item in monthly_data}
        monthly_orders = {}
        for month_start in last_six_months:
            month_name = month_start.strftime('%B %Y')
            monthly_orders[month_name] = monthly_dict.get(month_start, 0)
        
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
        
        today = datetime.now().date()
        last_six_months = []
        for i in range(5,-1,-1):
            month = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
            last_six_months.append(month)
        
        monthly_data = Order.objects.filter(payment_status='Paid').annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('total')).order_by('month')
        monthly_dict = {item['month'].date(): item['total'] for item in monthly_data}
        total_earnings = {}
        for data in last_six_months:
            month_name = data.strftime('%B %Y')
            total_earnings[month_name] = monthly_dict.get(data, 0)
        
        rep['total_earnings'] = total_earnings
        return rep


class AdminOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'email', 'phone_number', 'address', 'delivery_date', 'total', 'status', 'payment_method', 'payment_status', 'notes', 'created_at', 'updated_at']
        
        
    def update(self, instance, validated_data):
        allowed = ['status']  # only allow status update
        forbidden_fields = [field for field in validated_data.keys() if field not in allowed]
        
        if forbidden_fields:
            raise ValidationError({
                "message": f"Updating the following fields is not allowed: {', '.join(forbidden_fields)}"
            })

        return super().update(instance, validated_data)