import logging
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from users.models import CustomUser

logger = logging.getLogger('rooms')


class RoomCategory(models.Model):
    COMFORT_CHOICES = [
        ('standard', 'Стандартный'),
        ('semi_lux', 'Полулюкс'),
        ('lux', 'Люкс'),
        ('suite', 'Апартаменты'),
    ]
    name = models.CharField(max_length=100, verbose_name='Название категории')
    comfort = models.CharField(max_length=20, choices=COMFORT_CHOICES,
                               default='standard', verbose_name='Комфортность')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='Фото')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Категория номера'
        verbose_name_plural = 'Категории номеров'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_comfort_display()})'


class Room(models.Model):
    number = models.CharField(max_length=10, unique=True, verbose_name='Номер комнаты')
    category = models.ForeignKey(RoomCategory, on_delete=models.PROTECT,
                                  related_name='rooms', verbose_name='Категория')
    capacity = models.PositiveIntegerField(default=2, verbose_name='Вместимость (чел.)')
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2,
                                           validators=[MinValueValidator(0.01)],
                                           verbose_name='Цена за сутки (руб.)')
    floor = models.PositiveIntegerField(default=1, verbose_name='Этаж')
    area = models.FloatField(blank=True, null=True, verbose_name='Площадь (м²)')
    description = models.TextField(blank=True, verbose_name='Описание')
    amenities = models.TextField(blank=True, verbose_name='Удобства')
    image = models.ImageField(upload_to='rooms/', blank=True, null=True, verbose_name='Фото')
    is_available = models.BooleanField(default=True, verbose_name='Доступен')
    tags = models.ManyToManyField('RoomTag', blank=True,
                                   related_name='rooms', verbose_name='Теги')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Номер'
        verbose_name_plural = 'Номера'
        ordering = ['number']

    def __str__(self):
        return f'Номер {self.number} — {self.category.name} ({self.price_per_night} руб./ночь)'


class RoomTag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Тег')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Employee(models.Model):
    POSITION_CHOICES = [
        ('admin', 'Администратор'),
        ('manager', 'Менеджер'),
        ('cleaner', 'Горничная'),
        ('security', 'Охрана'),
        ('concierge', 'Консьерж'),
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,
                                related_name='employee_profile', verbose_name='Пользователь')
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, verbose_name='Должность')
    hire_date = models.DateField(verbose_name='Дата найма')
    salary = models.DecimalField(max_digits=10, decimal_places=2,
                                  validators=[MinValueValidator(0)], verbose_name='Зарплата (руб.)')
    photo = models.ImageField(upload_to='employees/', blank=True, null=True, verbose_name='Фото')
    bio = models.TextField(blank=True, verbose_name='О себе')
    is_active = models.BooleanField(default=True, verbose_name='Работает')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return f'{self.full_name} — {self.get_position_display()}'

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def phone(self):
        return self.user.phone

    @property
    def email(self):
        return self.user.email


class Client(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.SET_NULL,
                                null=True, blank=True,
                                related_name='client_profile', verbose_name='Аккаунт')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=100, blank=True, verbose_name='Отчество')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    passport = models.CharField(max_length=20, blank=True, verbose_name='Паспорт')
    has_children = models.BooleanField(default=False, verbose_name='Есть дети')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'.strip()

    @property
    def bookings_count(self):
        return self.bookings.count()


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждена'),
        ('checked_in', 'Заселён'),
        ('checked_out', 'Выселен'),
        ('cancelled', 'Отменена'),
    ]
    room = models.ForeignKey(Room, on_delete=models.PROTECT,
                              related_name='bookings', verbose_name='Номер')
    client = models.ForeignKey(Client, on_delete=models.PROTECT,
                                related_name='bookings', verbose_name='Клиент')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL,
                                  null=True, blank=True,
                                  related_name='bookings', verbose_name='Сотрудник')
    check_in = models.DateField(verbose_name='Дата заезда')
    check_out = models.DateField(verbose_name='Дата выезда')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                               default='pending', verbose_name='Статус')
    promo_code = models.ForeignKey('PromoCode', on_delete=models.SET_NULL,
                                    null=True, blank=True, verbose_name='Промокод')
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2,
                                           default=0, verbose_name='Скидка (руб.)')
    total_price = models.DecimalField(max_digits=12, decimal_places=2,
                                       default=0, verbose_name='Итого (руб.)')
    guests_count = models.PositiveIntegerField(default=1, verbose_name='Кол-во гостей')
    special_requests = models.TextField(blank=True, verbose_name='Особые пожелания')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Бронь'
        verbose_name_plural = 'Брони'
        ordering = ['-created_at']

    def __str__(self):
        return f'Бронь #{self.pk} — {self.client} — {self.room}'

    @property
    def nights(self):
        return (self.check_out - self.check_in).days

    def calculate_total(self):
        nights = self.nights
        if nights > 0:
            return self.room.price_per_night * nights - self.discount_amount
        return 0


class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('card', 'Банковская карта'),
        ('online', 'Онлайн'),
        ('transfer', 'Перевод'),
    ]
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE,
                                 related_name='payments', verbose_name='Бронь')
    amount = models.DecimalField(max_digits=12, decimal_places=2,
                                  validators=[MinValueValidator(0.01)],
                                  verbose_name='Сумма (руб.)')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES,
                               default='card', verbose_name='Способ оплаты')
    paid_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата оплаты')
    comment = models.CharField(max_length=255, blank=True, verbose_name='Примечание')

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
        ordering = ['-paid_at']

    def __str__(self):
        return f'Платёж #{self.pk} — {self.amount} руб. — {self.get_method_display()}'


# ===== ОБЩИЕ СТРАНИЦЫ =====

class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    summary = models.CharField(max_length=500, verbose_name='Краткое содержание')
    content = models.TextField(verbose_name='Полный текст')
    image = models.ImageField(upload_to='articles/', blank=True, null=True, verbose_name='Фото')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CompanyInfo(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    founded_year = models.PositiveIntegerField(verbose_name='Год основания')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(verbose_name='Email')
    logo = models.ImageField(upload_to='company/', blank=True, null=True, verbose_name='Логотип')
    stars = models.PositiveIntegerField(default=4, validators=[MaxValueValidator(5)],
                                         verbose_name='Звёзды (1-5)')
    history = models.TextField(blank=True, verbose_name='История')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'О гостинице'
        verbose_name_plural = 'О гостинице'

    def __str__(self):
        return self.name


class GlossaryTerm(models.Model):
    term = models.CharField(max_length=200, verbose_name='Термин')
    definition = models.TextField(verbose_name='Определение')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Термин'
        verbose_name_plural = 'Словарь терминов'
        ordering = ['term']

    def __str__(self):
        return self.term


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,
                                null=True, blank=True, verbose_name='Автор')
    name = models.CharField(max_length=100, verbose_name='Имя')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES,
                                          validators=[MinValueValidator(1), MaxValueValidator(5)],
                                          verbose_name='Оценка')
    text = models.TextField(verbose_name='Текст отзыва')
    is_approved = models.BooleanField(default=False, verbose_name='Одобрен')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.rating}★'


class Vacancy(models.Model):
    title = models.CharField(max_length=200, verbose_name='Должность')
    description = models.TextField(verbose_name='Описание')
    requirements = models.TextField(blank=True, verbose_name='Требования')
    salary_from = models.DecimalField(max_digits=10, decimal_places=2,
                                       null=True, blank=True, verbose_name='Зарплата от')
    salary_to = models.DecimalField(max_digits=10, decimal_places=2,
                                     null=True, blank=True, verbose_name='Зарплата до')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name='Код')
    description = models.TextField(blank=True, verbose_name='Описание')
    discount_percent = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)],
                                          verbose_name='Скидка %')
    valid_from = models.DateField(verbose_name='Действует с')
    valid_to = models.DateField(verbose_name='Действует до')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'
        ordering = ['-valid_to']

    def __str__(self):
        return f'{self.code} ({self.discount_percent}%)'

    @property
    def is_current(self):
        today = timezone.now().date()
        return self.valid_from <= today <= self.valid_to and self.is_active
