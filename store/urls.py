from django.urls import path
from . import views

urlpatterns = [
    # --- HTML Page Routes ---
    path('', views.index, name='index'), 
    path('auth/', views.auth_page, name='auth_page'),
    path('orders/', views.orders_page, name='orders_page'),

    # --- API Routes ---
    path('api/products/', views.get_products, name='get_products'), 
    path('api/checkout/', views.checkout, name='checkout'),
    
    # --- Authentication Routes ---
    path('api/register/', views.register_user, name='register'),
    path('api/login/', views.login_user, name='login'),
    path('api/logout/', views.logout_user, name='logout'),
    
    # --- Order History Route ---
    path('api/my-orders/', views.get_my_orders, name='get_my_orders'),
]