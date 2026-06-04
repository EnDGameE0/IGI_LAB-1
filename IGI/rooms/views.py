import io, base64, calendar as cal_module, logging, requests, statistics as stats_lib
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
from django.utils import timezone
from .models import (Room, RoomCategory, Booking, Client, Employee,
                     Article, CompanyInfo, GlossaryTerm, Review,
                     Vacancy, PromoCode, Payment)
from .forms import RoomFilterForm, RoomForm, BookingForm, ClientForm, ReviewForm, ClientBookingForm

logger = logging.getLogger('rooms')


# ══════════════════════════ ОБЩИЕ СТРАНИЦЫ ══════════════════════════

def home(request):
    latest_article = Article.objects.filter(is_published=True).first()
    company = CompanyInfo.objects.first()
    featured_rooms = Room.objects.filter(is_available=True)[:4]
    stats = {
        'rooms': Room.objects.count(),
        'clients': Client.objects.count(),
        'bookings': Booking.objects.filter(status='checked_out').count(),
        'categories': RoomCategory.objects.count(),
    }
    # API 1: Курс валют
    exchange_data = {}
    try:
        r = requests.get('https://open.er-api.com/v6/latest/BYN', timeout=3)
        if r.status_code == 200:
            d = r.json()
            exchange_data = {
                'USD': round(1 / d['rates'].get('USD', 1), 4),
                'EUR': round(1 / d['rates'].get('EUR', 1), 4),
                'RUB': round(1 / d['rates'].get('RUB', 1), 4),
            }
    except Exception as e:
        logger.warning(f'Exchange API error: {e}')

    # API 2: Случайная шутка
    joke = ''
    try:
        r2 = requests.get('https://official-joke-api.appspot.com/random_joke', timeout=3)
        if r2.status_code == 200:
            d2 = r2.json()
            joke = f"{d2.get('setup', '')} — {d2.get('punchline', '')}"
    except Exception as e:
        logger.warning(f'Joke API error: {e}')

    now = timezone.now()
    import calendar as cal
    local_now = timezone.localtime(now)
    cal_matrix = cal.monthcalendar(local_now.year, local_now.month)
    month_name = local_now.strftime('%B %Y')

    return render(request, 'main/home.html', {
        'latest_article': latest_article,
        'company': company,
        'featured_rooms': featured_rooms,
        'stats': stats,
        'exchange_data': exchange_data,
        'joke': joke,
        'now': now,
        'local_now': local_now,
        'cal_matrix': cal_matrix,
        'month_name': month_name,
        'timezone_name': 'Europe/Minsk',
    })


def about(request):
    company = CompanyInfo.objects.first()
    employees = Employee.objects.filter(is_active=True).select_related('user')
    return render(request, 'main/about.html', {'company': company, 'employees': employees})


def news_list(request):
    articles = Article.objects.filter(is_published=True)
    paginator = Paginator(articles, 6)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/news.html', {'page_obj': page})


def news_detail(request, pk):
    article = get_object_or_404(Article, pk=pk, is_published=True)
    return render(request, 'main/news_detail.html', {'article': article})


def glossary(request):
    terms = GlossaryTerm.objects.all()
    return render(request, 'main/glossary.html', {'terms': terms})


def contacts(request):
    company = CompanyInfo.objects.first()
    employees = Employee.objects.filter(is_active=True).select_related('user')
    weather = {}
    try:
        r = requests.get('https://wttr.in/Minsk?format=j1', timeout=3)
        if r.status_code == 200:
            d = r.json()
            weather = {
                'temp': d['current_condition'][0].get('temp_C', '?'),
                'desc': d['current_condition'][0].get('weatherDesc', [{}])[0].get('value', ''),
            }
    except Exception as e:
        logger.warning(f'Weather API error: {e}')
    return render(request, 'main/contacts.html', {
        'company': company, 'employees': employees, 'weather': weather,
    })


def privacy(request):
    return render(request, 'main/privacy.html')


def vacancies(request):
    return render(request, 'main/vacancies.html',
                  {'vacancies': Vacancy.objects.filter(is_active=True)})


def reviews(request):
    all_reviews = Review.objects.filter(is_approved=True)
    form = ReviewForm()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'Войдите чтобы оставить отзыв.')
            return redirect('users:login')
        form = ReviewForm(request.POST)
        if form.is_valid():
            rv = form.save(commit=False)
            rv.author = request.user
            if not rv.name:
                rv.name = request.user.get_full_name() or request.user.username
            rv.is_approved = True
            rv.save()
            messages.success(request, 'Спасибо! Ваш отзыв опубликован.')
            return redirect('rooms:reviews')
    return render(request, 'main/reviews.html', {'reviews': all_reviews, 'form': form})


@login_required
def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)
    # Админ может редактировать любые отзывы
    if not (request.user.is_staff or review.author == request.user):
        messages.error(request, 'Нет доступа.')
        return redirect('rooms:reviews')
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            rv = form.save(commit=False)
            rv.is_approved = True
            rv.save()
            messages.success(request, 'Отзыв обновлён!')
            return redirect('rooms:reviews')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'main/review_form.html', {'form': form, 'review': review})


@login_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    # Админ может удалять любые отзывы
    if not (request.user.is_staff or review.author == request.user):
        messages.error(request, 'Нет доступа.')
        return redirect('rooms:reviews')
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Отзыв удалён.')
        return redirect('rooms:reviews')
    return render(request, 'main/review_confirm_delete.html', {'review': review})


def promo_codes(request):
    today = timezone.now().date()
    return render(request, 'main/promos.html', {
        'active_promos': PromoCode.objects.filter(is_active=True),
        'archive_promos': PromoCode.objects.filter(is_active=False),
        'today': today,
    })


# ══════════════════════════ НОМЕРА (CRUD) ══════════════════════════

def room_list(request):
    qs = Room.objects.select_related('category').prefetch_related('tags')
    form = RoomFilterForm(request.GET)
    categories = RoomCategory.objects.all()
    if form.is_valid():
        s = form.cleaned_data
        if s.get('search'):
            qs = qs.filter(Q(number__icontains=s['search']) |
                           Q(description__icontains=s['search']) |
                           Q(category__name__icontains=s['search']))
        if s.get('category'):
            qs = qs.filter(category_id=s['category'])
        if s.get('price_min') is not None:
            qs = qs.filter(price_per_night__gte=s['price_min'])
        if s.get('price_max') is not None:
            qs = qs.filter(price_per_night__lte=s['price_max'])
        if s.get('capacity'):
            qs = qs.filter(capacity__gte=s['capacity'])
        if s.get('is_available'):
            qs = qs.filter(is_available=True)
        if s.get('sort'):
            qs = qs.order_by(s['sort'])
    paginator = Paginator(qs, 9)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'rooms/room_list.html',
                  {'page_obj': page, 'form': form, 'categories': categories})


def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    similar = Room.objects.filter(category=room.category).exclude(pk=pk)[:3]
    return render(request, 'rooms/room_detail.html', {'room': room, 'similar': similar})


@login_required
def room_create(request):
    if not request.user.is_staff:
        messages.error(request, 'Нет доступа.')
        return redirect('rooms:room_list')
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save()
            messages.success(request, 'Номер добавлен!')
            return redirect('rooms:room_detail', pk=room.pk)
    else:
        form = RoomForm()
    return render(request, 'rooms/room_form.html', {'form': form, 'title': 'Добавить номер'})


@login_required
def room_update(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if not request.user.is_staff:
        messages.error(request, 'Нет доступа.')
        return redirect('rooms:room_detail', pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Номер обновлён!')
            return redirect('rooms:room_detail', pk=pk)
    else:
        form = RoomForm(instance=room)
    return render(request, 'rooms/room_form.html',
                  {'form': form, 'title': 'Редактировать номер', 'room': room})


@login_required
def room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if not request.user.is_superuser:
        messages.error(request, 'Нет доступа.')
        return redirect('rooms:room_detail', pk=pk)
    if request.method == 'POST':
        room.delete()
        messages.success(request, 'Номер удалён.')
        return redirect('rooms:room_list')
    return render(request, 'rooms/room_confirm_delete.html', {'room': room})


# ══════════════════════════ БРОНИ (CRUD) ══════════════════════════

@login_required
def booking_list(request):
    # Админ и сотрудник (is_staff) видят ВСЕ брони, клиент — только свои
    if request.user.is_staff:
        qs = Booking.objects.all().select_related('room', 'client', 'employee')
    elif hasattr(request.user, 'is_client') and request.user.is_client():
        try:
            client = request.user.client_profile
            qs = Booking.objects.filter(client=client)
        except Exception:
            qs = Booking.objects.none()
    else:
        qs = Booking.objects.none()

    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '-created_at')
    if search:
        qs = qs.filter(Q(client__last_name__icontains=search) |
                       Q(client__first_name__icontains=search) |
                       Q(room__number__icontains=search))
    qs = qs.order_by(sort)
    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'rooms/booking_list.html', {'page_obj': page, 'search': search})


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    # Проверка доступа: админ/staff или владелец-клиент
    is_owner = False
    if hasattr(request.user, 'is_client') and request.user.is_client():
        try:
            is_owner = booking.client == request.user.client_profile
        except Exception:
            pass
    if not (request.user.is_staff or is_owner):
        messages.error(request, 'Нет доступа.')
        return redirect('rooms:booking_list')
    payments = booking.payments.all()
    return render(request, 'rooms/booking_detail.html',
                  {'booking': booking, 'payments': payments})


@login_required
def booking_create(request):
    is_client = hasattr(request.user, 'is_client') and request.user.is_client()
    is_staff_or_emp = request.user.is_staff

    if not (is_staff_or_emp or is_client):
        messages.error(request, 'Нет доступа.')
        return redirect('rooms:booking_list')

    if request.method == 'POST':
        if is_staff_or_emp:
            form = BookingForm(request.POST)
        else:
            form = ClientBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.status = 'confirmed'
            if is_client:
                try:
                    booking.client = request.user.client_profile
                except Exception:
                    pass
            if booking.check_in and booking.check_out and booking.room_id:
                nights = (booking.check_out - booking.check_in).days
                if nights > 0:
                    booking.total_price = booking.room.price_per_night * nights - booking.discount_amount
            booking.save()
            if hasattr(form, 'save_m2m'):
                form.save_m2m()
            messages.success(request, f'Бронь #{booking.pk} подтверждена!')
            return redirect('rooms:booking_detail', pk=booking.pk)
    else:
        form = BookingForm() if is_staff_or_emp else ClientBookingForm()
    return render(request, 'rooms/booking_form.html', {'form': form, 'title': 'Новая бронь'})


@login_required
def booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    is_staff_or_emp = request.user.is_staff
    is_own_booking = False
    if hasattr(request.user, 'is_client') and request.user.is_client():
        try:
            is_own_booking = booking.client == request.user.client_profile
        except Exception:
            pass

    if not (is_staff_or_emp or is_own_booking):
        messages.error(request, 'Нет доступа.')
        return redirect('rooms:booking_list')

    if request.method == 'POST':
        if is_staff_or_emp:
            form = BookingForm(request.POST, instance=booking)
        else:
            form = ClientBookingForm(request.POST, instance=booking)
        if form.is_valid():
            b = form.save(commit=False)
            if b.check_in and b.check_out and b.room_id:
                nights = (b.check_out - b.check_in).days
                if nights > 0:
                    b.total_price = b.room.price_per_night * nights - b.discount_amount
            b.save()
            messages.success(request, 'Бронь обновлена!')
            return redirect('rooms:booking_detail', pk=pk)
    else:
        if is_staff_or_emp:
            form = BookingForm(instance=booking)
        else:
            form = ClientBookingForm(instance=booking)
    return render(request, 'rooms/booking_form.html',
                  {'form': form, 'title': f'Редактировать бронь #{pk}', 'booking': booking})


@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    is_staff = request.user.is_staff
    is_own_booking = False
    if hasattr(request.user, 'is_client') and request.user.is_client():
        try:
            is_own_booking = booking.client == request.user.client_profile
        except Exception:
            pass

    if not (is_staff or is_own_booking):
        messages.error(request, 'Нет доступа.')
        return redirect('rooms:booking_list')

    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Бронь удалена.')
        return redirect('rooms:booking_list')
    return render(request, 'rooms/booking_confirm_delete.html', {'booking': booking})


# ══════════════════════════ КЛИЕНТЫ (CRUD) — ДЛЯ АДМИНА И СОТРУДНИКА ══════════════════════════

@login_required
def client_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Нет доступа.')
        return redirect('rooms:room_list')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', 'last_name')
    qs = Client.objects.all()
    if search:
        qs = qs.filter(Q(last_name__icontains=search) |
                       Q(first_name__icontains=search) |
                       Q(phone__icontains=search))
    qs = qs.order_by(sort)
    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'rooms/client_list.html',
                  {'page_obj': page, 'search': search, 'sort': sort})


@login_required
def client_create(request):
    if not request.user.is_staff:
        messages.error(request, 'Нет доступа.')
        return redirect('rooms:room_list')
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Клиент добавлен!')
            return redirect('rooms:client_list')
    else:
        form = ClientForm()
    return render(request, 'rooms/client_form.html', {'form': form, 'title': 'Добавить клиента'})


@login_required
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if not request.user.is_staff:
        messages.error(request, 'Нет доступа.')
        return redirect('rooms:client_list')
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Клиент обновлён!')
            return redirect('rooms:client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'rooms/client_form.html',
                  {'form': form, 'title': 'Редактировать клиента', 'client': client})


@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if not request.user.is_superuser:
        messages.error(request, 'Нет доступа.')
        return redirect('rooms:client_list')
    if request.method == 'POST':
        client.delete()
        messages.success(request, 'Клиент удалён.')
        return redirect('rooms:client_list')
    return render(request, 'rooms/client_confirm_delete.html', {'client': client})


# ══════════════════════════ СТАТИСТИКА — ТОЛЬКО ДЛЯ АДМИНА ══════════════════════════

@login_required
def statistics(request):
    if not request.user.is_superuser:
        messages.error(request, 'Доступ только для администратора')
        return redirect('rooms:home')

    completed = Booking.objects.filter(status='checked_out')
    total_revenue = completed.aggregate(s=Sum('total_price'))['s'] or 0
    avg_booking = completed.aggregate(a=Avg('total_price'))['a'] or 0

    amounts = list(completed.values_list('total_price', flat=True))
    amounts_float = [float(a) for a in amounts]
    median_amount = stats_lib.median(amounts_float) if len(amounts_float) >= 1 else 0
    try:
        mode_amount = stats_lib.mode(amounts_float) if amounts_float else 0
    except Exception:
        mode_amount = max(set(amounts_float), key=amounts_float.count) if amounts_float else 0

    from users.models import CustomUser
    today = timezone.now().date()
    users_bd = CustomUser.objects.filter(birth_date__isnull=False)
    ages = [(today - u.birth_date).days // 365 for u in users_bd]
    avg_age = round(stats_lib.mean(ages), 1) if ages else 0
    median_age = round(stats_lib.median(ages), 1) if ages else 0

    by_category = Room.objects.values('category__name').annotate(cnt=Count('id')).order_by('-cnt')
    by_status = Booking.objects.values('status').annotate(cnt=Count('id'))
    monthly = completed.annotate(month=TruncMonth('created_at')).values('month').annotate(
        cnt=Count('id'), total=Sum('total_price')).order_by('month')
    clients_sorted = Client.objects.annotate(
        bookings_cnt=Count('bookings'), total=Sum('bookings__total_price')
    ).order_by('last_name')
    top_rooms = Room.objects.annotate(
        bookings_cnt=Count('bookings'), revenue=Sum('bookings__total_price')
    ).order_by('-bookings_cnt')[:5]

    import json
    def to_json(qs):
        result = []
        for item in qs:
            row = {}
            for k, v in item.items():
                if hasattr(v, 'strftime'):
                    row[k] = v.strftime('%m/%Y')
                else:
                    row[k] = float(v) if hasattr(v, '__float__') else v
            result.append(row)
        return json.dumps(result)

    utc_now = timezone.now()
    local_now = timezone.localtime(utc_now)
    text_calendar = cal_module.month(local_now.year, local_now.month)

    return render(request, 'rooms/statistics.html', {
        'total_revenue': total_revenue,
        'avg_booking': avg_booking,
        'median_amount': median_amount,
        'mode_amount': mode_amount,
        'avg_age': avg_age,
        'median_age': median_age,
        'ages_count': len(ages),
        'by_category': to_json(by_category),
        'by_status': to_json(by_status),
        'monthly': to_json(monthly),
        'clients_sorted': clients_sorted,
        'top_rooms': top_rooms,
        'completed_count': completed.count(),
        'utc_now': utc_now,
        'local_now': local_now,
        'text_calendar': text_calendar,
    })


@login_required
def chart_python(request):
    if not request.user.is_superuser:
        messages.error(request, 'Доступ только для администратора')
        return redirect('rooms:home')

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker

    monthly = Booking.objects.filter(status='checked_out').annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(cnt=Count('id'), total=Sum('total_price')).order_by('month')

    if monthly:
        months = [d['month'].strftime('%m/%Y') for d in monthly]
        totals = [float(d['total'] or 0) for d in monthly]
        counts = [d['cnt'] for d in monthly]
    else:
        months = ['01/2024','02/2024','03/2024','04/2024','05/2024','06/2024']
        totals = [2400, 3100, 2800, 3600, 4100, 3900]
        counts = [12, 16, 14, 18, 21, 19]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('Статистика гостиницы (Python/matplotlib)', fontsize=13, fontweight='bold')

    axes[0].bar(months, totals, color='#1565c0', alpha=0.8)
    axes[0].set_title('Выручка по месяцам (руб.)')
    axes[0].set_ylabel('Выручка (руб.)')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))

    axes[1].plot(months, counts, marker='o', color='#c49b15', linewidth=2, markersize=7)
    axes[1].fill_between(range(len(months)), counts, alpha=0.2, color='#c49b15')
    axes[1].set_title('Количество выездов')
    axes[1].set_ylabel('Кол-во')
    axes[1].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    chart1_b64 = base64.b64encode(buf.read()).decode()
    plt.close(fig)

    by_cat = Room.objects.values('category__name').annotate(cnt=Count('id')).order_by('cnt')
    cat_names = [d['category__name'] for d in by_cat] or ['Стандарт','Полулюкс','Люкс']
    cat_vals = [d['cnt'] for d in by_cat] or [8, 5, 3]

    fig2, ax = plt.subplots(figsize=(8, 4))
    colors = ['#1565c0','#1976d2','#42a5f5','#c49b15','#ffd54f']
    ax.barh(cat_names, cat_vals, color=colors[:len(cat_names)], alpha=0.85)
    ax.set_title('Номера по категориям', fontsize=12)
    ax.set_xlabel('Количество')
    plt.tight_layout()
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png', dpi=100, bbox_inches='tight')
    buf2.seek(0)
    chart2_b64 = base64.b64encode(buf2.read()).decode()
    plt.close(fig2)

    by_status = Booking.objects.values('status').annotate(cnt=Count('id'))
    STATUS_L = {'pending':'Ожидает','confirmed':'Подтверждена','checked_in':'Заселён',
                'checked_out':'Выселен','cancelled':'Отменена'}
    s_labels = [STATUS_L.get(d['status'], d['status']) for d in by_status]
    s_vals = [d['cnt'] for d in by_status]
    if not s_labels:
        s_labels = ['Выселен','Подтверждена','Ожидает']
        s_vals = [15, 8, 3]

    fig3, ax3 = plt.subplots(figsize=(6, 5))
    ax3.pie(s_vals, labels=s_labels, autopct='%1.1f%%',
            colors=colors[:len(s_labels)], startangle=90)
    ax3.set_title('Брони по статусам', fontsize=12)
    plt.tight_layout()
    buf3 = io.BytesIO()
    plt.savefig(buf3, format='png', dpi=100, bbox_inches='tight')
    buf3.seek(0)
    chart3_b64 = base64.b64encode(buf3.read()).decode()
    plt.close(fig3)

    utc_now = timezone.now()
    local_now = timezone.localtime(utc_now)
    text_calendar = cal_module.month(local_now.year, local_now.month)

    return render(request, 'rooms/chart_python.html', {
        'chart1_b64': chart1_b64,
        'chart2_b64': chart2_b64,
        'chart3_b64': chart3_b64,
        'utc_now': utc_now,
        'local_now': local_now,
        'text_calendar': text_calendar,
        'timezone': 'Europe/Minsk',
    })