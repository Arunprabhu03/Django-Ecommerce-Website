from django.urls import path,include
from . import views
from .views import user_orders

urlpatterns = [
    path('payment_success', views.payment_success, name='payment_success'),
    path('checkout', views.checkout, name='checkout'),
    path('billing_info', views.billing_info, name="billing_info"),
    path('process_order', views.process_order, name="process_order"),
    path('shipped_dash', views.shipped_dash, name="shipped_dash"),
    path('not_shipped_dash', views.not_shipped_dash, name="not_shipped_dash"),
    path('orders/<int:pk>', views.orders, name='orders'),
    
    
    path('my_orders/', user_orders, name='user_orders'),
    
    path('cancel_order/<int:pk>/', views.cancel_order, name='cancel_order'),
    
    path('generate_invoice/<int:pk>', views.generate_invoice, name='generate_invoice'),
]