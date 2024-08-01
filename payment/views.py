from django.shortcuts import render, redirect, get_object_or_404
from payment.models import ShippingAddress, Order, OrderItem
from cart.cart import Cart
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product, Profile
import datetime
from payment.forms import ShippingForm, PaymentForm


from django.utils.safestring import mark_safe
from django.urls import reverse

# Create your views here.

def cancel_order(request, pk):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=pk, user=request.user)
        # Implement cancellation logic here (e.g., update order status or delete order)
        order.delete()  # Example: Deleting the order
        
        messages.success(request, 'Order cancelled successfully')

        # Redirect to appropriate dashboard after cancellation
        if order.shipped:
            return redirect('shipped_dash')
        else:
            return redirect('user_orders')
    else:
        # Handle GET requests or other methods
        return redirect('home')  # Redirect to home if method is not POST


from django.contrib.auth.decorators import login_required

@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-date_ordered')
    return render(request, 'payment/user_orders.html', {'orders': orders})


@login_required
def orders(request, pk):
    # Get the order
    order = get_object_or_404(Order, id=pk, user=request.user)
    # Get the order items
    items = OrderItem.objects.filter(order=order)

    # Check if POST request to update shipping status
    if request.method == 'POST' and request.user.is_superuser:
        status = request.POST.get('shipping_status')
        if status == 'true':
            # Update the order as shipped
            order.shipped = True
            order.date_shipped = datetime.datetime.now()
        else:
            # Update the order as not shipped
            order.shipped = False
            order.date_shipped = None  

        order.save()
        messages.success(request, "Shipping Status Updated")
        return redirect('orders', pk=pk)

    return render(request, 'payment/orders.html', {"order": order, "items": items})

def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            # Get the order
            order = Order.objects.filter(id=num)
            # grab Date and time
            now = datetime.datetime.now()
            # update order
            order.update(shipped=True, date_shipped=now)
            # redirect
            messages.success(request, "Shipping Status Updated")
            return redirect('not_shipped_dash')

        return render(request, "payment/not_shipped_dash.html", {"orders":orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders = Order.objects.filter(shipped=True)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			# grab the order
			order = Order.objects.filter(id=num)
			# grab Date and time
			now = datetime.datetime.now()
			# update order
			order.update(shipped=False)
			# redirect
			messages.success(request, "Shipping Status Updated")
			return redirect('shipped_dash')

		return render(request, "payment/shipped_dash.html", {"orders":orders})
	else:
		messages.success(request, "Access Denied")
		return redirect('home')

def process_order(request):
    if request.POST:
        # Get the cart
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        # Get Billing Info from the last page
        payment_form = PaymentForm(request.POST or None)
        # Get Shipping Session Data
        my_shipping = request.session.get('my_shipping')

        # Gather Order Info
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        # Create Shipping Address from session info
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals

        # Create an Order
        if request.user.is_authenticated:
            # logged in
            user = request.user
            # Create Order
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # Add order items
            
            # Get the order ID
            order_id = create_order.pk
            
            # Get product Info
            for product in cart_products():
                # Get product ID
                product_id = product.id
                # Get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                # Get quantity
                for key,value in quantities().items():
                    if int(key) == product.id:
                        # Create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                        create_order_item.save()

            # Delete our cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    # Delete the key
                    del request.session[key]

            # Delete Cart from Database (old_cart field)
            current_user = Profile.objects.filter(user__id=request.user.id)
            # Delete shopping cart in database (old_cart field)
            current_user.update(old_cart="")

            invoice_url = reverse('generate_invoice', args=[create_order.pk])
            message = mark_safe(f"Order Placed! <a href='{invoice_url}' class='btn btn-primary'>Download Invoice</a>")
            messages.success(request, message)
            #messages.success(request, "Order Placed!")
            return redirect('home')

            

        else:
            # not logged in
            # Create Order
            create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # Add order items
            
            # Get the order ID
            order_id = create_order.pk
            
            # Get product Info
            for product in cart_products():
                # Get product ID
                product_id = product.id
                # Get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                # Get quantity
                for key,value in quantities().items():
                    if int(key) == product.id:
                        # Create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()

            # Delete our cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    # Delete the key
                    del request.session[key]
                
            invoice_url = reverse('generate_invoice', args=[create_order.pk])
            message = mark_safe(f"Order Placed! <a href='{invoice_url}' class='btn btn-primary'>Download Invoice</a>")
            messages.success(request, message)
            #messages.success(request, "Order Placed!")
            return redirect('home')

    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def billing_info(request):
        if request.POST:
            # Get the cart
            cart = Cart(request)
            cart_products = cart.get_prods
            quantities = cart.get_quants
            totals = cart.cart_total()

            # Create a session with Shipping Info
            my_shipping = request.POST
            request.session['my_shipping'] = my_shipping

            # Check to see if user is logged in
            if request.user.is_authenticated:
                # Get The Billing Form
                billing_form = PaymentForm()
                return render(request, "payment/billing_info.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_info":request.POST, "billing_form":billing_form})

            else:
                # Not logged in
                # Get The Billing Form
                billing_form = PaymentForm()
                return render(request, "payment/billing_info.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_info":request.POST, "billing_form":billing_form})
            
            shipping_form = request.POST
            return render(request, "payment/billing_info.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form})	
        else:
            messages.success(request, "Access Denied")
            return redirect('home')
    

def checkout(request):
    # Get the cart
	cart = Cart(request)
	cart_products = cart.get_prods
	quantities = cart.get_quants
	totals = cart.cart_total()

	if request.user.is_authenticated:
		# Checkout as logged in user
		# Shipping User
		shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
		# Shipping Form
		shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
		return render(request, "payment/checkout.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form })
	else:
		# Checkout as guest
		shipping_form = ShippingForm(request.POST or None)
		return render(request, "payment/checkout.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form})

def payment_success(request):
	return render(request, "payment/payment_success.html", {})




from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def generate_invoice(request, pk):
    if request.user.is_authenticated :
        order = Order.objects.get(id=pk)
        items = OrderItem.objects.filter(order=pk)
        template_path = 'payment/invoice.html'
        context = {
            'order': order,
            'items': items,
        }
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('We had some errors with code %s' % html)
        return response
    else:
        messages.success(request, "Access Denied")
        return redirect('home')
