from rest_framework import serializers
from .models import *

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