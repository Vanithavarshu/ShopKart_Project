from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from shop.models import Cart, Order, OrderItem, Product, Profile
from django.contrib.auth.models import User
import random
from django.http import JsonResponse
from django.http import HttpResponse 
from django.contrib.auth import User

@login_required(login_url='/login/')
def index(request):
    rawcart = Cart.objects.filter(user=request.user)
    
    for item in rawcart:
        if item.product_qty > item.product.quantity:
            item.delete()

    cartitems = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.selling_price * item.product_qty for item in cartitems)

    userprofile = Profile.objects.get(user=request.user).first()

    context = {'cartitems': cartitems, 'total_price': total_price, 'userprofile':userprofile}
    return render(request, "shop/checkout.html", context)


@login_required(login_url='/login/')
def placeorder(request):
    if request.method == "POST":
        # Retrieve cart items and calculate total price
        cart = Cart.objects.filter(user=request.user)
        if not cart.exists():
            messages.error(request, "Your cart is empty!")
            return redirect("cart")

        cart_total_price = sum(item.product.selling_price * item.product_qty for item in cart)

        currentuser = User.objects.get(id=request.user.id).first()


#profile
        if not currentuser.first_name:
            currentuser.first_name = request.POST.get('fname')
            currentuser.last_name = request.POST.get('lname')
            currentuser.save()

        if not Profile.objects.filter(user=request.user).exists():
            userprofile = Profile.objects.create(
                user=request.user,
                phone=request.POST.get('phone'),
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                country=request.POST.get('country'),
                pincode=request.POST.get('pincode')
            )
         
        # Create a new order
        neworder = Order(
            user=request.user,
            fname=request.POST.get('fname'),
            lname=request.POST.get('lname'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            country=request.POST.get('country'),
            pincode=request.POST.get('pincode'),
            total_price=cart_total_price,  # ✅ Fix: Correct assignment
            payment_mode=request.POST.get('payment_mode'), # ✅ Fix: Added missing comma
            payment_id=request.POST.get('payment_id'),  # ✅ Fix: Added missing comma<
        )

        # Generate a unique tracking number
        trackno = 'Varsha' + str(random.randint(1111111, 9999999))
        while Order.objects.filter(tracking_no=trackno).exists():
            trackno = 'Varsha' + str(random.randint(1111111, 9999999))
        
        neworder.tracking_no = trackno
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

        # Clear user's cart after order placement
        cart.delete()
        messages.success(request, "Your order has been placed successfully!")

        payMode = request.POST.get('payment_mode')
        if payMode == "Paid by Razorpay":
            return JsonResponse({'status': "Your order has been placed successfully!"})

        return redirect('/')
@login_required(login_url='/login/')
def razorpaycheck(request):
    cart = Cart.objects.filter(user=request.user)
    total_price = 0
    for item in cart:
        total_price = total_price + item.product.selling_price * item.product_qty

    return JsonResponse({
        'total_price': total_price
    })

def orders(request):
    return HttpResponse("My orders page")
    