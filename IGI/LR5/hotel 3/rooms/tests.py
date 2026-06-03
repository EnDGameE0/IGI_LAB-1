from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase, Client as TC
from django.urls import reverse
from django.contrib.auth import get_user_model
from rooms.models import (RoomCategory, Room, Client, Booking, Review, PromoCode)
from rooms.forms import ReviewForm, ClientForm, RoomFilterForm

User = get_user_model()


def make_admin():
    u, c = User.objects.get_or_create(username='ta', defaults=dict(
        first_name='A', last_name='B', role='admin',
        birth_date=date(1985,1,1), is_staff=True, is_superuser=True))
    if c: u.set_password('pass'); u.save()
    return u

def make_emp_user():
    u, c = User.objects.get_or_create(username='te', defaults=dict(
        first_name='E', last_name='F', role='employee', birth_date=date(1990,5,10),
        phone='+375 (29) 111-11-11'))
    if c: u.set_password('pass'); u.save()
    return u

def make_client_user():
    u, c = User.objects.get_or_create(username='tc', defaults=dict(
        first_name='C', last_name='D', role='client', birth_date=date(1995,3,20)))
    if c: u.set_password('pass'); u.save()
    return u

def make_category(name='Стандарт'):
    return RoomCategory.objects.get_or_create(name=name, defaults={'comfort': 'standard'})[0]

def make_room(price=80, available=True):
    cat = make_category()
    return Room.objects.create(
        number=f'R{Room.objects.count()+1}',
        category=cat, capacity=2,
        price_per_night=Decimal(str(price)),
        floor=1, is_available=available)

def make_client():
    return Client.objects.get_or_create(last_name='Тест', first_name='Клиент', defaults={
        'phone': '+375 (29) 200-00-01', 'email': 'test@test.by'})[0]


# ─── Модели ──────────────────────────────────────

class RoomCategoryTest(TestCase):
    def test_str(self):
        c = RoomCategory(name='Люкс', comfort='lux')
        self.assertIn('Люкс', str(c))

class RoomModelTest(TestCase):
    def test_str_has_number(self):
        r = make_room()
        self.assertIn(r.number, str(r))
    def test_default_available(self):
        self.assertTrue(make_room().is_available)

class ClientModelTest(TestCase):
    def test_full_name(self):
        c = Client(last_name='Иванов', first_name='Иван', middle_name='Иванович')
        self.assertEqual(c.full_name, 'Иванов Иван Иванович')
    def test_str(self): self.assertIn('Тест', str(make_client()))

class BookingModelTest(TestCase):
    def test_nights(self):
        room = make_room()
        cl = make_client()
        b = Booking.objects.create(
            room=room, client=cl,
            check_in=date.today(), check_out=date.today()+timedelta(days=3),
            status='pending', total_price=Decimal('240'))
        self.assertEqual(b.nights, 3)
    def test_str(self):
        room = make_room(); cl = make_client()
        b = Booking.objects.create(room=room, client=cl,
            check_in=date.today(), check_out=date.today()+timedelta(days=2),
            status='pending', total_price=Decimal('160'))
        self.assertIn(str(b.pk), str(b))

class PromoCodeModelTest(TestCase):
    def test_is_current_active(self):
        today = date.today()
        p = PromoCode(code='T', discount_percent=10,
                      valid_from=today, valid_to=today+timedelta(days=10), is_active=True)
        self.assertTrue(p.is_current)
    def test_is_current_expired(self):
        p = PromoCode(code='T2', discount_percent=10,
                      valid_from=date(2020,1,1), valid_to=date(2020,12,31), is_active=True)
        self.assertFalse(p.is_current)

class UserModelTest(TestCase):
    def test_is_employee(self): self.assertTrue(User(username='e', role='employee').is_employee())
    def test_is_client(self): self.assertTrue(User(username='c', role='client').is_client())
    def test_str(self):
        u = User(username='x', first_name='А', last_name='Б', role='client')
        self.assertIn('Клиент', str(u))


# ─── Формы ───────────────────────────────────────

class ReviewFormTest(TestCase):
    def test_valid(self):
        f = ReviewForm({'name':'Тест','rating':5,'text':'Отличная гостиница, очень доволен!'})
        self.assertTrue(f.is_valid())
    def test_short_text(self):
        f = ReviewForm({'name':'Тест','rating':4,'text':'Норм'})
        self.assertFalse(f.is_valid())
    def test_no_rating(self):
        f = ReviewForm({'name':'Тест','text':'Достаточно длинный текст отзыва.'})
        self.assertFalse(f.is_valid())

class ClientFormTest(TestCase):
    VALID = {'first_name':'Иван','last_name':'Тест','phone':'+375 (29) 123-45-67','email':'i@t.by'}
    def test_valid(self): self.assertTrue(ClientForm(self.VALID).is_valid())
    def test_bad_phone(self):
        f = ClientForm({**self.VALID, 'phone': '80291234567'})
        self.assertFalse(f.is_valid())

class RoomFilterFormTest(TestCase):
    def test_empty_valid(self): self.assertTrue(RoomFilterForm({}).is_valid())
    def test_with_params(self):
        f = RoomFilterForm({'price_min':'50','price_max':'200'})
        self.assertTrue(f.is_valid())


# ─── Публичные страницы ──────────────────────────

class PublicViewsTest(TestCase):
    def setUp(self):
        self.tc = TC()
        self.room = make_room()

    def _200(self, url): self.assertEqual(self.tc.get(url).status_code, 200)

    def test_home(self):     self._200(reverse('rooms:home'))
    def test_rooms(self):    self._200(reverse('rooms:room_list'))
    def test_detail(self):   self._200(reverse('rooms:room_detail', args=[self.room.pk]))
    def test_about(self):    self._200(reverse('rooms:about'))
    def test_news(self):     self._200(reverse('rooms:news'))
    def test_glossary(self): self._200(reverse('rooms:glossary'))
    def test_contacts(self): self._200(reverse('rooms:contacts'))
    def test_privacy(self):  self._200(reverse('rooms:privacy'))
    def test_vacancies(self):self._200(reverse('rooms:vacancies'))
    def test_reviews(self):  self._200(reverse('rooms:reviews'))
    def test_promos(self):   self._200(reverse('rooms:promos'))

    def test_list_search(self):
        self._200(reverse('rooms:room_list') + '?search=стандарт')
    def test_list_price_filter(self):
        self._200(reverse('rooms:room_list') + '?price_min=50&price_max=200')
    def test_list_sort(self):
        self._200(reverse('rooms:room_list') + '?sort=price_per_night')


# ─── Авторизованные страницы ─────────────────────

class AuthViewsTest(TestCase):
    def setUp(self):
        self.tc = TC()
        self.admin = make_admin()
        self.emp_u = make_emp_user()
        from rooms.models import Employee
        self.emp, _ = Employee.objects.get_or_create(user=self.emp_u, defaults=dict(
            position='admin', hire_date=date(2020,1,1), salary=Decimal('1000')))
        self.room = make_room()

    def test_create_requires_login(self):
        self.assertEqual(self.tc.get(reverse('rooms:room_create')).status_code, 302)

    def test_create_as_employee(self):
        self.tc.login(username='te', password='pass')
        self.assertEqual(self.tc.get(reverse('rooms:room_create')).status_code, 200)

    def test_create_as_client_redirects(self):
        make_client_user()
        self.tc.login(username='tc', password='pass')
        r = self.tc.get(reverse('rooms:room_create'))
        self.assertEqual(r.status_code, 302)

    def test_statistics_requires_login(self):
        self.assertEqual(self.tc.get(reverse('rooms:statistics')).status_code, 302)

    def test_statistics_as_admin(self):
        self.tc.login(username='ta', password='pass')
        self.assertEqual(self.tc.get(reverse('rooms:statistics')).status_code, 200)

    def test_delete_as_admin(self):
        self.tc.login(username='ta', password='pass')
        r2 = make_room()
        self.tc.post(reverse('rooms:room_delete', args=[r2.pk]))
        self.assertFalse(Room.objects.filter(pk=r2.pk).exists())

    def test_client_list_as_employee(self):
        self.tc.login(username='te', password='pass')
        self.assertEqual(self.tc.get(reverse('rooms:client_list')).status_code, 200)


# ─── Auth ────────────────────────────────────────

class UserAuthTest(TestCase):
    def setUp(self): self.tc = TC()

    def test_register_200(self):
        self.assertEqual(self.tc.get(reverse('users:register')).status_code, 200)
    def test_login_200(self):
        self.assertEqual(self.tc.get(reverse('users:login')).status_code, 200)
    def test_register_creates_user(self):
        self.tc.post(reverse('users:register'), {
            'username':'newu88','first_name':'Новый','last_name':'Юзер',
            'email':'n@t.by','password1':'SecurePass123!','password2':'SecurePass123!'})
        self.assertTrue(User.objects.filter(username='newu88').exists())
    def test_profile_requires_login(self):
        self.assertEqual(self.tc.get(reverse('users:profile')).status_code, 302)


# ─── Валидация ───────────────────────────────────

class ValidationTest(TestCase):
    def test_phone_valid(self):
        from users.models import validate_phone
        for p in ['+375 (29) 123-45-67','+375 (33) 987-65-43']:
            validate_phone(p)

    def test_phone_invalid(self):
        from users.models import validate_phone
        from django.core.exceptions import ValidationError
        for p in ['80291234567','+375291234567']:
            with self.assertRaises(ValidationError): validate_phone(p)

    def test_age_under_18(self):
        from users.models import validate_age_18
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            validate_age_18(date.today()-timedelta(days=365*16))

    def test_age_over_18(self):
        from users.models import validate_age_18
        validate_age_18(date.today()-timedelta(days=365*20))

    def test_booking_date_validation(self):
        from rooms.forms import BookingForm
        room = make_room()
        cl = make_client()
        f = BookingForm({'room': room.pk, 'client': cl.pk, 'status': 'pending',
                         'check_in': date.today(), 'check_out': date.today(),
                         'guests_count': 1, 'total_price': '0'})
        self.assertFalse(f.is_valid())

    def test_room_price_negative(self):
        from rooms.forms import RoomForm
        cat = make_category()
        f = RoomForm({'number': 'T999', 'category': cat.pk, 'capacity': 2,
                      'price_per_night': '-10', 'floor': 1})
        self.assertFalse(f.is_valid())


# ─── CRUD ORM ────────────────────────────────────

class RoomCRUDTest(TestCase):
    def test_create(self): self.assertIsNotNone(make_room().pk)
    def test_read(self):
        r = make_room()
        self.assertEqual(Room.objects.get(pk=r.pk).number, r.number)
    def test_update(self):
        r = make_room(); r.price_per_night = Decimal('150'); r.save()
        r.refresh_from_db()
        self.assertEqual(r.price_per_night, Decimal('150'))
    def test_delete(self):
        r = make_room(); pk = r.pk; r.delete()
        self.assertFalse(Room.objects.filter(pk=pk).exists())
    def test_filter_available(self):
        make_room(available=True)
        self.assertGreater(Room.objects.filter(is_available=True).count(), 0)
    def test_order_by_price(self):
        make_room(price=50); make_room(price=200)
        rs = list(Room.objects.order_by('price_per_night'))
        self.assertLessEqual(rs[0].price_per_night, rs[-1].price_per_night)


# ─── Связи ───────────────────────────────────────

class RelationsTest(TestCase):
    def test_room_fk_category(self):
        cat = make_category('Люкс')
        r = Room.objects.create(number='L1', category=cat, capacity=2,
                                price_per_night=Decimal('200'), floor=4)
        self.assertIn(r, cat.rooms.all())

    def test_room_m2m_tags(self):
        from rooms.models import RoomTag
        r = make_room()
        t1 = RoomTag.objects.create(name='Wi-Fi')
        t2 = RoomTag.objects.create(name='Балкон')
        r.tags.set([t1, t2])
        self.assertEqual(r.tags.count(), 2)

    def test_booking_fk_client(self):
        r = make_room(); cl = make_client()
        b = Booking.objects.create(room=r, client=cl, check_in=date.today(),
            check_out=date.today()+timedelta(days=2), status='pending', total_price=Decimal('160'))
        self.assertEqual(b.client, cl)
        self.assertIn(b, cl.bookings.all())

    def test_employee_1to1_user(self):
        from rooms.models import Employee
        eu = make_emp_user()
        emp, _ = Employee.objects.get_or_create(user=eu, defaults=dict(
            position='admin', hire_date=date(2020,1,1), salary=Decimal('1200')))
        self.assertEqual(emp.user, eu)
