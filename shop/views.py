from django.http import  JsonResponse
from django.shortcuts import redirect, render
from shop.form import CustomUserForm
from . models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from shop.services.deepseek import deepseek_chatbot
from shop.models import Cart
from shop.models import Order
from shop.models import OrderItem
import json
import random
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
import requests
 
 
def home(request):
  products=Product.objects.filter(trending=1)
  return render(request,"shop/index.html",{"products":products})
 
def favviewpage(request):
  if request.user.is_authenticated:
    fav=Favourite.objects.filter(user=request.user)
    return render(request,"shop/fav.html",{"fav":fav})
  else:
    return redirect("/")
 
def remove_fav(request,fid):
  item=Favourite.objects.get(id=fid)
  item.delete()
  return redirect("/favviewpage")

#autofill checkout
 
 
 
 
def cart_page(request):
  if request.user.is_authenticated:
    cart=Cart.objects.filter(user=request.user)
    return render(request,"shop/cart.html",{"cart":cart})
  else:
    return redirect("/")
 
def remove_cart(request,cid):
  cartitem=Cart.objects.get(id=cid)
  cartitem.delete()
  return redirect("/cart")
 
def delete_cart_items(request):
    if request.user.is_authenticated:
        Cart.objects.filter(user=request.user).delete()
        return JsonResponse({'status': 'Cart cleared successfully'})
    else:
        return JsonResponse({'status': 'Login required'}, status=401)
    
def clear_cart(request):
    if request.user.is_authenticated:
        Cart.objects.filter(user=request.user).delete()
        return redirect('/cart')
    else:
        return redirect('/login')
 
 
def fav_page(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_id=data['pid']
      product_status=Product.objects.get(id=product_id)
      if product_status:
         if Favourite.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Favourite'}, status=200)
         else:
          Favourite.objects.create(user=request.user,product_id=product_id)
          return JsonResponse({'status':'Product Added to Favourite'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Favourite'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)
 
 
def add_to_cart(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_qty=int(data['product_qty'])
      product_id=data['pid']
      #print(request.user.id)
      product_status=Product.objects.get(id=product_id)
      if product_status:
        if Cart.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Cart'}, status=200)
        else:
          if product_status.quantity>=product_qty:
            Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
            return JsonResponse({'status':'Product Added to Cart'}, status=200)
          else:
            return JsonResponse({'status':'Product Stock Not Available'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Cart'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)
 
def logout_page(request):
  if request.user.is_authenticated:
    logout(request)
    messages.success(request,"Logged out Successfully")
  return redirect("/")
 
 
def login_page(request):
  if request.user.is_authenticated:
    return redirect("/")
  else:
    if request.method=='POST':
      name=request.POST.get('username')
      pwd=request.POST.get('password')
      user=authenticate(request,username=name,password=pwd)
      if user is not None:
        login(request,user)
        messages.success(request,"Logged in Successfully")
        return redirect("/")
      else:
        messages.error(request,"Invalid User Name or Password")
        return redirect("/login")
    return render(request,"shop/login.html")

 
def register(request):
  form=CustomUserForm()
  if request.method=='POST':
    form=CustomUserForm(request.POST)
    if form.is_valid():
      form.save()
      messages.success(request,"Registration Success You can Login Now..!")
      return redirect('/login')
  return render(request,"shop/register.html",{'form':form})
 
 
def collections(request):
  catagory=Catagory.objects.filter(status=0)
  return render(request,"shop/collections.html",{"catagory":catagory})
 
def collectionsview(request,name):
  if(Catagory.objects.filter(name=name,status=0)):
      products=Product.objects.filter(category__name=name)
      return render(request,"shop/products/index.html",{"products":products,"category_name":name})
  else:
    messages.warning(request,"No Such Catagory Found")
    return redirect('collections')
 
 #product details
def product_details(request,cname,pname):
    if(Catagory.objects.filter(name=cname,status=0)):
      if(Product.objects.filter(name=pname,status=0)):
        products=Product.objects.filter(name=pname,status=0).first()
        return render(request,"shop/products/product_details.html",{"products":products})
      else:
        messages.error(request,"No Such Produtct Found")
        return redirect('collections')
    else:
      messages.error(request,"No Such Catagory Found")
      return redirect('collections')
    
    #checkout

def checkout(request):
    if request.user.is_authenticated:
        cartitems = Cart.objects.filter(user=request.user)

        # Ensure product_qty is an integer and multiply correctly
        total_price = sum(item.product.selling_price * int(item.product_qty) for item in cartitems)

        return render(request, 'shop/checkout.html', {'cartitems': cartitems, 'total_price': total_price})

    return redirect('login')

#placeorder

def placeorder(request):
    if request.method == 'POST':
        # Retrieve form data
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        phone = request.POST.get('phone')

        # Get cart items
        cart = Cart.objects.filter(user=request.user)
        if not cart.exists():
            messages.error(request, "Your cart is empty!")
            return redirect("cart")

        # Calculate total price
        total_price = sum(item.product.selling_price * item.product_qty for item in cart)

        # Create a new order
        neworder = Order(
            user=request.user,
            fname=fname,
            lname=lname,
            email=email,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            phone=phone,
            total_price=total_price,  # ✅ Fix: Adding total_price
            status="Pending"
        )
        neworder.save()

        # Move cart items to OrderItem and update stock
        for item in cart:
            OrderItem.objects.create(
                order=neworder,
                product=item.product,
                price=item.product.selling_price,
                quantity=item.product_qty
            )

            # Reduce product stock
            orderproduct = Product.objects.get(id=item.product_id)
            orderproduct.quantity -= item.product_qty
            orderproduct.save()
             # Reduce product stock
            orderproduct = Product.objects.get(id=item.product_id)
            orderproduct.quantity -= item.product_qty
            orderproduct.save()

        # Clear user's cart after order placement
        cart.delete()

        return JsonResponse({
    "success": True, 
    "redirect_url": "/collections"  # Hardcoded URL
})

def razorpaycheck(request):
    cart = Cart.objects.filter(user=request.user)
    total_price = 0
    for item in cart:
        total_price = total_price + item.product.selling_price * item.product_qty

    return JsonResponse({
        'total_price': total_price
    })

#clr cart after a payment success
from django.urls import reverse

def razorpay_success(request):
    if request.method == "POST":
        cart_items = Cart.objects.filter(user=request.user)

        for item in cart_items:
            Order.objects.create(
                user=request.user,
                product=item.product,
                quantity=item.product_qty,
                total_price=item.product.selling_price * item.product_qty
            )

        cart_items.delete()  # Remove cart items after payment

        return JsonResponse({"status": "success", "redirect_url": reverse('myorders')})  # Redirect to "My Orders"
    
    return JsonResponse({"status": "failed", "message": "Invalid request"})

"""def my_orders(request):
    print("✅ my_orders view is being called!")  # Debugging print
    orders = Order.objects.filter(user=request.user).order_by('-created_at')  
    print("Orders found:", orders)  # Check if orders exist
    context = {'orders': orders}
    return render(request, 'shop/orders/my_orders.html', context)"""

#only for logged in users
@login_required
def my_orders(request):
    print("✅ my_orders view is being called!")  # Debugging print
    print("Current User:", request.user)  # Check the logged-in user

    orders = Order.objects.filter(user=request.user).order_by('-created_at')  # Filter orders by logged-in user
    print("Orders found for user:", orders)  # Debugging print to verify filtering

    context = {'orders': orders}
    return render(request, 'shop/orders/my_orders.html', context)
    
#chatbot

def chatbot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message")

        url = f"{settings.DEEPSEEK_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        }

        response = requests.post(url, headers=headers, json=payload)
        bot_response = response.json()["choices"][0]["message"]["content"]

        return JsonResponse({"response": bot_response})

    return JsonResponse({"error": "Invalid request"}, status=400)

"""def vieworder(request, t_no):
    order = Order.objects.filter(tracking_no=t_no).filter(user=request.user).first()
    orderitems = OrderItem.objects.filter(order=order)
    context = {'order': order, 'orderitems': orderitems}
    return render(request, 'shop/orders/view.html', context)"""
#only for logged in users

@login_required  # Ensures only logged-in users can view orders
def vieworder(request, t_no):
    # Get the order, but only if it belongs to the logged-in user
    order = get_object_or_404(Order, tracking_no=t_no, user=request.user)
    
    # Get all items in that order
    orderitems = OrderItem.objects.filter(order=order)

    context = {'order': order, 'orderitems': orderitems}
    return render(request, 'shop/orders/view.html', context)

