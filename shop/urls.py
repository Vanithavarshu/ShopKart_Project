from django.urls import path
from . import views
from .views import chatbot
from django.urls import path
from .views import razorpay_success
from django.contrib import admin

urlpatterns= [
    path('',views.home,name="home"),
    path('register',views.register,name="register"),
    path('login',views.login_page,name="login"),
    path('logout',views.logout_page,name="logout"),
    path('cart',views.cart_page,name="cart"),
    path('fav',views.fav_page,name="fav"),
    path('favviewpage',views.favviewpage,name="favviewpage"),
    path('remove_fav/<str:fid>',views.remove_fav,name="remove_fav"),
    path('remove_cart/<str:cid>',views.remove_cart,name="remove_cart"),
    path('delete_cart_items/', views.delete_cart_items, name="delete_cart_items"),
    path('collections',views.collections,name="collections"),
    path('collections/<str:name>',views.collectionsview,name="collections"),
    path('collections/<str:cname>/<str:pname>',views.product_details,name="product_details"),
    path('addtocart',views.add_to_cart,name="addtocart"),
    path('clear-cart/',views.clear_cart, name='clear-cart'),
    path('checkout', views.checkout, name="checkout"),
    path('placeorder', views.placeorder, name="placeorder"),
    path('proceed-to-pay/', views.razorpaycheck, name="proceed-to-pay"),
    path('my-orders/', views.my_orders, name='myorders'),
    #chatbot url
    path('chatbot/', chatbot, name='chatbot'),
    path("razorpay-success/", razorpay_success, name="razorpay_success"),#clr after payment
    path('view-order/<str:t_no>', views.vieworder, name="orderview")


]
   

