import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Product, Order, OrderItem

# --- HTML PAGE VIEWS ---

def index(request):
    return render(request, 'index.html')

def auth_page(request):
    return render(request, 'auth.html')

def orders_page(request):
    return render(request, 'orders.html')


# --- PRODUCT & CHECKOUT APIs ---

def get_products(request):
    products = list(Product.objects.values('id', 'name', 'price', 'description', 'image_url'))
    return JsonResponse(products, safe=False)

@csrf_exempt
def checkout(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cart = data.get('cart', [])

        if len(cart) == 0:
            return JsonResponse({'error': 'Cart is empty'}, status=400)

        if request.user.is_authenticated:
            user = request.user
        else:
            user, created = User.objects.get_or_create(username='guest_shopper')

        order = Order.objects.create(user=user, status='Pending')

        for item in cart:
            try:
                product = Product.objects.get(id=item['id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['qty'],
                    price=product.price
                )
            except Product.DoesNotExist:
                continue

        return JsonResponse({'success': True, 'order_id': order.id})
    return JsonResponse({'error': 'Invalid request method'}, status=400)


# --- AUTHENTICATION APIs ---

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return JsonResponse({'success': True, 'username': user.username})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'username': user.username})
        else:
            return JsonResponse({'error': 'Invalid username or password'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


# --- ORDER HISTORY APIs ---

def get_my_orders(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not logged in'}, status=403)

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    orders_data = []
    for order in orders:
        items = order.items.all()
        item_data = [{'name': i.product.name, 'qty': i.quantity, 'price': str(i.price)} for i in items]
        total = sum(i.price * i.quantity for i in items)
        
        orders_data.append({
            'id': order.id,
            'status': order.status,
            'date': order.created_at.strftime('%Y-%m-%d'),
            'total': str(total),
            'items': item_data
        })
        
    return JsonResponse(orders_data, safe=False)