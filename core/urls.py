from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *
# path(url, view_function, url_name)
# Dynamic Routing - We pass values through routing
# Except values from route -> recive view function -> html file
# int, str, slug
# Good Morning Students -> Slug : good-morning-students
urlpatterns = [
    path('', home, name="home"),
    path('search/', search, name="search"),
    path('cart/', cart, name="cart"),
    path('bridal/', bridal, name="bridal"),
    path('collections/', collections, name="collections"),
    path('gold-jewellery/', gold_jewellery, name="gold_jewellery"),
    path('footer/', footer, name="footer"),
    path('diamond-jewellery/', diamond_jewellery, name="diamond_jewellery"),
    path('navbar/', navbar, name="navbar"),
    path('offers/', offers, name="offers"),
    path('new-arrivals/', new_arrivals, name="new_arrivals"),
    path('checkout/', checkout, name="checkout"),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
]