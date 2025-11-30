from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Seller(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='sellers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class Product(models.Model):
    Choices_UOM = [('pcs', 'Pieces'),('kg', 'Kilogram'),('litre', 'Litre'),('box', 'Box'),('pack', 'Pack'),]
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    stock = models.PositiveIntegerField(default=0)
    uom = models.CharField(max_length=20, choices=Choices_UOM, default='pcs')
    is_best_seller = models.BooleanField(default=False)
    is_best_offer = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
    
class Order(models.Model):
    ORDER_STATUS_CHOICES = [('Pending', 'Pending'),('Processing', 'Processing'),('Shipped', 'Shipped'),('Completed', 'Completed'),('Cancelled', 'Cancelled'),]
    PAYMENT_METHOD_CHOICES = [('COD', 'Cash on Delivery'),('Card', 'Card Payment'),('Online', 'Online Payment'),]
    PAYMENT_STATUS_CHOICES = [('Pending', 'Pending'),('Paid', 'Paid'),('Failed', 'Failed'),]
    
    customer_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    delivery_date = models.DateField(null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='Card')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order {self.id} by {self.customer_name}'
    
    
    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = Order.objects.get(pk=self.pk)
            if old_instance.status != "Cancelled" and self.status == "Cancelled":
                for item in self.order_details.all():
                    item.product.stock += item.quantity
                    item.product.save()
        super().save(*args, **kwargs)
    
    
class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)


    def __str__(self):
        return f'{self.quantity} of {self.product.name} in Order {self.order.id}'

    def save(self, *args, **kwargs):
        # Check if updating existing instance
        if self.pk:
            old_instance = OrderDetail.objects.get(pk=self.pk)
            diff = self.quantity - old_instance.quantity
            self.product.stock = max(self.product.stock - diff, 0)
        else:
            # New instance, subtract quantity
            self.product.stock = max(self.product.stock - self.quantity, 0)

        self.product.save()
        super().save(*args, **kwargs)
        self.update_order_total()

    def delete(self, *args, **kwargs):
        # Restore stock when deleting
        self.product.stock += self.quantity
        self.product.save()
        super().delete(*args, **kwargs)

    def update_order_total(self):
        total = sum(item.quantity * item.price for item in self.order.order_details.all())
        self.order.total = total
        self.order.save(update_fields=['total'])