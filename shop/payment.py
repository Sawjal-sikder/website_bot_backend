from venv import logger
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from .models import Order
import stripe
import json
import os

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def orderPayment(request, orderId):
    try:
        order = Order.objects.get(id=orderId)
        amount_cents = int(order.total * 100)
        
        # Already paid
        if order.payment_status == 'Paid':
            return JsonResponse({"success": False, "error": "Order already paid"}, status=400)

        # If payment is not paid 
        if order.payment_status != 'Paid':
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'gbp',
                        'product_data': {'name': f'Order {order.id} Payment'},
                        'unit_amount': amount_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='https://www.orderwithpluto.com/',
                cancel_url='https://www.orderwithpluto.com/',
                metadata={'order_id': order.id},
            )

            # Update order
            order.payment_status = 'Pending'
            order.stripe_payment_intent = checkout_session.payment_intent
            order.save()

            return JsonResponse({
                'success': True,
                'checkout_url': checkout_session.url
            })

        # Fallback for any other cases
        return JsonResponse({"success": False, "error": "Unable to create payment"}, status=400)

    except Order.DoesNotExist:
        return JsonResponse({"success": False, "error": "Order not found"}, status=404)
    except stripe.error.StripeError as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

    
    
@csrf_exempt
def paymentWebhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)  
    except stripe.error.SignatureVerificationError: 
        return HttpResponse(status=400)  

    try:
        # Handle successful checkout session completion
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            order_id = session['metadata'].get('order_id')
            
            if order_id:
                order = Order.objects.get(id=order_id)
                order.payment_status = 'Paid'
                order.save()
            else:
                logger.error("No order_id found in session metadata")

        # Handle successful payment intent (backup for direct payment intents)
        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            
            # Try to get order_id from payment intent metadata first
            order_id = payment_intent['metadata'].get('order_id')
            
            # If not found, try to get it from the checkout session
            if not order_id and payment_intent.get('invoice'):
                try:
                    # Get the checkout session associated with this payment intent
                    sessions = stripe.checkout.Session.list(
                        payment_intent=payment_intent['id'],
                        limit=1
                    )
                    if sessions.data:
                        order_id = sessions.data[0]['metadata'].get('order_id')
                except Exception as e:
                    logger.error(f"Error fetching checkout session: {e}")
            
            if order_id:
                order = Order.objects.get(id=order_id)
                order.payment_status = 'Paid'
                order.save()
            else:
                logger.error("No order_id found in payment intent metadata")

        # Handle failed payment
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            order_id = payment_intent['metadata'].get('order_id')
            
            if order_id:
                order = Order.objects.get(id=order_id)
                order.payment_status = 'Failed'
                order.save()
            else:
                logger.error("No order_id found in failed payment intent metadata")

        else:
            logger.info(f"Unhandled event type: {event['type']}")

        return HttpResponse(status=200)

    except Order.DoesNotExist:
        logger.error(f"Order not found for order_id: {order_id}")
        return HttpResponse("Order not found", status=404)
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500)



