import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileForm

logger = logging.getLogger('rooms')

def register(request):
    if request.user.is_authenticated:
        return redirect('rooms:home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'client'
            user.save()
            login(request, user)
            logger.info(f'New user: {user.username}')
            messages.success(request, f'Добро пожаловать, {user.first_name or user.username}!')
            return redirect('rooms:home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('rooms:home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Вы вошли как {user.username}.')
            return redirect(request.GET.get('next', 'rooms:home'))
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('rooms:home')

@login_required
def profile(request):
    user = request.user
    form = ProfileForm(request.POST or None, request.FILES or None, instance=user)
    bookings = []
    try:
        from rooms.models import Booking, Client
        if user.is_client():
            client = Client.objects.filter(user=user).first()
            if client:
                bookings = Booking.objects.filter(client=client).order_by('-created_at')[:5]
        elif user.is_employee() or user.is_staff:
            from rooms.models import Employee
            emp = Employee.objects.filter(user=user).first()
            if emp:
                bookings = Booking.objects.filter(employee=emp).order_by('-created_at')[:5]
    except Exception:
        pass
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Профиль обновлён!')
        return redirect('users:profile')
    return render(request, 'users/profile.html', {'form': form, 'bookings': bookings})
