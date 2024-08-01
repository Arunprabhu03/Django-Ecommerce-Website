from django.shortcuts import render,redirect, get_object_or_404
from .models import Product,Category,Profile
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from .forms import SignUpForm

from payment.forms import ShippingForm
from payment.models import ShippingAddress

from django import forms
from django.db.models import Q
import json
from cart.cart import Cart

from .models import Category, Product
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required,user_passes_test
from .forms import ProductForm,CategoryForm

#delete category by admin
@user_passes_test(lambda u: u.is_superuser)
def delete_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
    return redirect('category_summary')

#adding category and product by admin or superuser in the webpage
@staff_member_required
def add_category(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('category_summary') 
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form,'categories': categories})

@staff_member_required
def add_product(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Error adding product. Please check the form.')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form,'categories': categories})



@staff_member_required
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product', pk=pk)  
        else:
            messages.error(request, 'Error updating product. Please check the form.')
    else:
        form = ProductForm(instance=product)
    return render(request, 'update_product.html', {'form': form, 'product': product, 'categories': categories})

@staff_member_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('home')  
    return render(request, 'delete_product.html', {'product': product})



def update_info(request):
    categories = Category.objects.all()
    if request.user.is_authenticated:
        # Get Current User
        current_user = Profile.objects.get(user__id=request.user.id)

        # Get Current User's Shipping Info
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        
        # Get original User Form
        form = UserInfoForm(request.POST or None, instance=current_user)
        
        # Get User's Shipping Form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)		
        
        if form.is_valid() or shipping_form.is_valid():
            # Save original form
            form.save()
            # Save shipping form
            shipping_form.save()
            
            messages.success(request, "Your Info Has Been Updated!!")
            return redirect('home')
        
        return render(request, "update_info.html", {'form':form, 'shipping_form':shipping_form,'categories': categories})
    else:
        messages.success(request, "You Must Be Logged In To Access That Page!!")
        return redirect('home')

def update_password(request):
    categories = Category.objects.all()
    
    if request.user.is_authenticated:
        current_user = request.user
        # Did they fill out the form
        if request.method  == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            # Is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, "Your Password Has Been Updated...")
                login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, "update_password.html", {'form':form,'categories': categories})
    else:
        messages.success(request, "You Must Be Logged In To View That Page...")
        return redirect('home')

def update_user(request):
    categories = Category.objects.all()
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)
        
        if user_form.is_valid():
                user_form.save()
                login(request, current_user)
                messages.success(request, "User Has Been Updated!!")
                return redirect('home')
        return render(request, "update_user.html", {'user_form':user_form,'categories': categories})
        
    else:
        messages.success(request, "You Must Be Logged In To Access That Page!!")
        return redirect('home')

def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {"categories":categories})	

def category(request, foo):
    categories = Category.objects.all()
    # Replace hyphens with spaces
    foo = foo.replace('-', ' ')
    
    try:
        category = Category.objects.get(name__iexact=foo)  # Case-insensitive lookup
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category,'categories': categories})
    
    except Category.DoesNotExist:
        messages.success(request, "That category doesn't exist!!")
        return redirect('home')


def product(request,pk):
    product = Product.objects.get(id=pk)
    categories = Category.objects.all()
    return render(request,'product.html',{'product':product,'categories': categories})
    

def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    
    return render(request,'home.html',{'products': products, 'categories': categories})

def about(request):
    categories = Category.objects.all()
    return render(request,'about.html',{'categories': categories})



#For preventing a logged in user from accessing the login page again by using the /login url
from .decorators import anonymous_required  # Import the decorator

@anonymous_required
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            # Do some shopping cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)
            # Get their saved cart from database
            saved_cart = current_user.old_cart
            # Convert database string to python dictionary
            if saved_cart:
                # Convert to dictionary using JSON
                converted_cart = json.loads(saved_cart)
                # Add the loaded cart dictionary to our session
                # Get the cart
                cart = Cart(request)
                # Loop thru the cart and add the items from the database
                for key,value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)
            messages.success(request,("You have been logged in !!"))
            return redirect('home')
        else:
            messages.success(request,("There was an error, please try again.."))
            return redirect('login')    
    else:
        return render(request,'login.html',{})

def logout_user(request):
    logout(request)
    messages.success(request,("You have been logged out..Thanks for stopping by... "))
    return redirect('home')

def register_user(request):
	form = SignUpForm()
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			# log in user
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, ("Username Created - Please Fill Out Your User Info Below..."))
			return redirect('update_info')
		else:
			messages.success(request, ("Whoops! There was a problem Registering, please try again..."))
			return redirect('register')
	else:
		return render(request, 'register.html', {'form':form})

def search(request):
    categories = Category.objects.all()
    searched = request.POST.get('searched')
    
    if searched:
        # Query The Products DB Model
        searched = Product.objects.filter(Q(name__icontains=searched) #| Q(description__icontains=searched 
        )
        # Test for null
        if not searched:
            messages.success(request, "That Product Does Not Exist...Please try Again.")
            return render(request, "search.html", {'categories': categories})
        else:
            return render(request, "search.html", {'searched': searched, 'categories': categories})
    else:
        return render(request, "search.html", {'categories': categories})

