from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Order
import stripe
import os

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@shared_task
def auto_cancel_unpaid_orders():
    # 5 minutes ago
    time_limit = timezone.now() - timedelta(minutes=5)
    
    # Select unpaid orders older than 5 minutes
    orders_to_cancel = Order.objects.filter(payment_status='Pending', status='Pending', created_at__lte=time_limit)
    
    for order in orders_to_cancel:
        # Restore stock
        for item in order.order_details.all():
            item.product.stock += item.quantity
            item.product.save()
            
        if order.stripe_payment_intent:
            print( f"Attempting to cancel Stripe PaymentIntent {order.stripe_payment_intent} for Order {order.id}" )
            try:
                stripe.PaymentIntent.cancel(order.stripe_payment_intent)
                print(f"Successfully cancelled Stripe PaymentIntent {order.stripe_payment_intent} for Order {order.id}")
            except Exception as e:
                # Log the error or handle it as needed
                print(f"Error cancelling Stripe PaymentIntent {order.stripe_payment_intent}: {e}")
        
        # Cancel the order
        order.status = 'Cancelled'
        order.save()
