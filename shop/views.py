from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from .models import Product  # Импортируем модель товара

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # автоматический вход после регистрации
            return redirect('profile')
    else:
        form = UserCreationForm()
    return render(request, 'shop/signup.html', {'form': form})


def home(request):
    products = Product.objects.all()  # Берем все товары из базы
    return render(request, 'shop/home.html', {'products': products})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def profile_view(request):
    return render(request, 'shop/profile.html')


from django.shortcuts import get_object_or_404
from .models import CartItem

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if request.user.is_authenticated:
        # Авторизованный пользователь — корзина в БД
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product
        )
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
    else:
        # Неавторизованный пользователь — корзина в сессии
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            cart[str(product_id)] += quantity
        else:
            cart[str(product_id)] = quantity
        request.session['cart'] = cart

    return redirect('home')


from django.shortcuts import render, redirect
from .models import CartItem

def cart_view(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        
        total_price = 0
        for item in cart_items:
            item.total_price = item.quantity * item.product.price
            total_price += item.total_price

        context = {
            'cart_items': cart_items,
            'total_price': total_price
        }
        return render(request, 'shop/cart.html', context)
    else:
        return render(request, 'shop/message.html', {'message': 'Авторизуйтесь, чтобы просматривать корзину.'})



from .models import Order

def checkout_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        cart_items = CartItem.objects.filter(user=request.user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        order = Order.objects.create(
            user=request.user,
            total_price=total_price
        )

        # Очищаем корзину
        cart_items.delete()

        return render(request, 'shop/thank_you.html')

    return render(request, 'shop/checkout.html')

from django.shortcuts import render, redirect
from .models import CartItem

def cart_view(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        for item in cart_items:
            item.total_price = item.product.price * item.quantity  # для отображения итога по товару
        return render(request, 'shop/cart.html', {
            'cart_items': cart_items,
            'total_price': total_price,
        })
    else:
        return render(request, 'shop/message.html', {
            'message': 'Авторизуйтесь, чтобы просматривать корзину.'
        })


def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            item.quantity = quantity
            item.save()
    return redirect('cart')


def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if request.method == 'POST':
        item.delete()
    return redirect('cart')

from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    return render(request, 'shop/profile.html')
