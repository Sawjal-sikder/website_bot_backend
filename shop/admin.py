from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Order, OrderDetail, Seller


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price','seller', 'stock', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock', 'is_active']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'image')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'get_total_price']
    can_delete = False
    
    def get_total_price(self, obj):
        if obj.quantity and obj.price:
            return f"${obj.quantity * obj.price:.2f}"
        return "$0.00"
    get_total_price.short_description = "Total Price"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'email', 'total', 'status', 'payment_method', 'payment_status', 'created_at', 'updated_at']
    list_filter = ['status', 'payment_method', 'payment_status', 'created_at']
    search_fields = ['customer_name', 'email', 'phone_number', 'address']
    list_editable = ['status', 'payment_status']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    inlines = [OrderDetailInline]
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'email', 'phone_number', 'address')
        }),
        ('Order Details', {
            'fields': ('total', 'status', 'delivery_date', 'notes')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_status_display(self, obj):
        colors = {
            'Pending': 'orange',
            'Processing': 'blue',
            'Shipped': 'purple',
            'Completed': 'green',
            'Cancelled': 'red'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.status
        )
    get_status_display.short_description = "Status"
    
    def get_payment_status_display(self, obj):
        colors = {
            'Pending': 'orange',
            'Paid': 'green',
            'Failed': 'red'
        }
        color = colors.get(obj.payment_status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.payment_status
        )
    get_payment_status_display.short_description = "Payment Status"


@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'get_total_price']
    list_filter = ['order__status']
    search_fields = ['order__id', 'product__name', 'order__customer_name']
    readonly_fields = ['get_total_price']
    ordering = ['-order__created_at']
    
    def get_total_price(self, obj):
        return f"${obj.quantity * obj.price:.2f}"
    get_total_price.short_description = "Total Price"
    
    fieldsets = (
        (None, {
            'fields': ('order', 'product', 'quantity', 'price')
        }),
        ('Calculated Fields', {
            'fields': ('get_total_price',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )