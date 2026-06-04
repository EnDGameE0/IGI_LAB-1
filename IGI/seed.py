#!/usr/bin/env python
import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel.settings')
django.setup()

from django.contrib.auth import get_user_model
from rooms.models import (
    RoomCategory, Room, Article, Review, PromoCode, Vacancy,
    GlossaryTerm, Client, Booking, Employee, CompanyInfo
)

User = get_user_model()

def seed():
    print("=" * 50)
    print("НАЧИНАЕМ ЗАГРУЗКУ ВСЕХ ДАННЫХ")
    print("=" * 50, flush=True)

    # =========================================================
    # 1. СУПЕРПОЛЬЗОВАТЕЛЬ
    # =========================================================
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print('✅ Суперпользователь admin (admin@example.com / admin123)', flush=True)
    else:
        print('⚠️ Суперпользователь admin уже существует', flush=True)

    # =========================================================
    # 2. ОБЫЧНЫЕ ПОЛЬЗОВАТЕЛИ (клиенты + сотрудник)
    # =========================================================
    users_data = [
        # Клиенты (is_staff=False)
        ('client1', 'client1@example.com', 'client123', 'Иван', 'Петров', '+375291234567', date(1990, 5, 15), False),
        ('client2', 'client2@example.com', 'client123', 'Мария', 'Иванова', '+375293334455', date(1985, 8, 22), False),
        ('client3', 'client3@example.com', 'client123', 'Сергей', 'Сидоров', '+375445556677', date(1995, 3, 10), False),
        ('client4', 'client4@example.com', 'client123', 'Анна', 'Козлова', '+375296667788', date(1988, 11, 30), False),
        ('client5', 'client5@example.com', 'client123', 'Павел', 'Воробьёв', '+375336022222', date(2000, 1, 20), False),
        ('client6', 'client6@example.com', 'client123', 'Ольга', 'Захарова', '+375296011111', date(1992, 7, 7), False),
        ('client7', 'client7@example.com', 'client123', 'Виктор', 'Новиков', '+375296100000', date(1980, 12, 1), False),
        ('client8', 'client8@example.com', 'client123', 'Наталья', 'Попова', '+375336055555', date(1998, 6, 25), False),
        ('client9', 'client9@example.com', 'client123', 'Алексей', 'Кузнецов', '+375296044444', date(1975, 4, 18), False),
        ('client10', 'client10@example.com', 'client123', 'Егор', 'Лебедев', '+375446066666', date(2002, 9, 12), False),
        # Сотрудник (is_staff=True)
        ('receptionist_a', 'receptionist_a@hotel.by', 'emp123', 'Анна', 'Иванова', '+375291111111', date(1988, 3, 10), True),
    ]

    created_users = {}
    for username, email, pwd, first, last, phone, birth, is_staff in users_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first,
                'last_name': last,
                'phone': phone,
                'birth_date': birth,
                'is_staff': is_staff,
            }
        )
        if created:
            user.set_password(pwd)
            user.save()
            print(f'👤 Создан пользователь {username} ({first} {last})', flush=True)
        created_users[username] = user
        
    # =========================================================
    # 3. ИНФОРМАЦИЯ О КОМПАНИИ
    # =========================================================
    CompanyInfo.objects.get_or_create(
        name='Гостиница «Олимп»',
        defaults={
            'description': 'Комфортабельная гостиница в центре Минска. 80 номеров различных категорий, ресторан, SPA, конференц-зал.',
            'founded_year': 2005,
            'address': 'г. Минск, пр. Независимости, 42',
            'phone': '+375 (17) 300-40-50',
            'email': 'info@olimp-hotel.by',
            'stars': 4,
            'history': '2005 — открытие гостиницы\n2010 — реновация номерного фонда\n2015 — открытие SPA-комплекса\n2020 — расширение до 80 номеров\n2024 — запуск онлайн-бронирования'
        }
    )
    print('🏢 Создана информация о компании', flush=True)

    # =========================================================
    # 4. СОТРУДНИКИ
    # =========================================================
    employee_users = [
        ('receptionist_a', 'admin', date(2022, 1, 15), 1200),
    ]

    for username, position, hire_date, salary in employee_users:
        user = created_users.get(username)
        if user:
            Employee.objects.get_or_create(
                user=user,
                defaults={
                    'position': position,
                    'hire_date': hire_date,
                    'salary': salary,
                    'is_active': True
                }
            )
    print(f'👔 Создано {Employee.objects.count()} сотрудников', flush=True)

    # =========================================================
    # 5. КЛИЕНТЫ
    # =========================================================
    client_users = [f'client{i}' for i in range(1, 11)]
    for username in client_users:
        user = created_users.get(username)
        if user:
            Client.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone,
                    'email': user.email,
                    'has_children': random.choice([True, False])
                }
            )
    print(f'👥 Создано {Client.objects.count()} клиентов', flush=True)

    # =========================================================
    # 6. КАТЕГОРИИ НОМЕРОВ
    # =========================================================
    categories_data = [
        ('Стандартный', 'standard', 'Стандартные номера с базовыми удобствами.'),
        ('Полулюкс', 'semi_lux', 'Номера повышенной комфортности с гостиной зоной.'),
        ('Люкс', 'lux', 'Люксовые номера с джакузи и панорамным видом.'),
        ('Апартаменты', 'suite', 'Просторные апартаменты с кухней и двумя спальнями.'),
    ]

    cats = {}
    for name, comfort, desc in categories_data:
        cat, _ = RoomCategory.objects.get_or_create(
            name=name,
            defaults={'comfort': comfort, 'description': desc}
        )
        cats[name] = cat
    print(f'📁 Создано {RoomCategory.objects.count()} категорий', flush=True)

    # =========================================================
    # 7. НОМЕРА
    # =========================================================
    rooms_data = [
        ('101', 'Стандартный', 1, 55, 'Уютный одноместный номер на первом этаже.', 1, 18),
        ('102', 'Стандартный', 2, 75, 'Стандартный двухместный номер.', 1, 22),
        ('103', 'Стандартный', 2, 85, 'Студия с мини-кухней.', 1, 28),
        ('104', 'Стандартный', 2, 95, 'Номер с видом на город.', 2, 24),
        ('105', 'Стандартный', 3, 110, 'Семейный номер.', 2, 32),
        ('106', 'Стандартный', 2, 80, 'Номер с улучшенной звукоизоляцией.', 2, 22),
        ('107', 'Стандартный', 1, 60, 'Эконом вариант для командировок.', 3, 18),
        ('201', 'Полулюкс', 2, 180, 'Полулюкс с гостиной зоной.', 2, 45),
        ('202', 'Полулюкс', 2, 200, 'Полулюкс с видом на парк.', 2, 48),
        ('203', 'Полулюкс', 3, 220, 'Полулюкс для семьи.', 2, 52),
        ('301', 'Люкс', 2, 250, 'Люкс с джакузи и панорамным видом.', 3, 55),
        ('302', 'Люкс', 3, 280, 'Люкс с отдельной спальней.', 3, 60),
        ('303', 'Люкс', 2, 300, 'Президентский люкс.', 3, 70),
        ('401', 'Апартаменты', 4, 380, 'Двухкомнатные апартаменты.', 4, 85),
        ('402', 'Апартаменты', 4, 400, 'Апартаменты с террасой.', 4, 90),
    ]

    for num, cat_name, cap, price, desc, floor, area in rooms_data:
        Room.objects.get_or_create(
            number=num,
            defaults={
                'category': cats[cat_name],
                'capacity': cap,
                'price_per_night': price,
                'description': desc,
                'floor': floor,
                'area': area,
                'is_available': True
            }
        )
    print(f'🛏️ Создано {Room.objects.count()} номеров', flush=True)

    # =========================================================
    # 8. НОВОСТИ
    # =========================================================
    news_data = [
        ('Детская комната открыта', 'Игровая зона для маленьких гостей', 'Теперь в нашей гостинице есть детская комната с аниматором.'),
        ('Фитнес-центр обновлён', 'Новое оборудование в зале', 'Мы закупили новые беговые дорожки и силовые тренажёры.'),
        ('Новые апартаменты', 'Представляем расширенный номерной фонд', 'Открылись новые просторные апартаменты на 4-м этаже.'),
        ('Трансфер из аэропорта', 'Новая услуга для гостей', 'Заказывайте трансфер из аэропорта Минск-2.'),
        ('День рождения в «Олимпе»', 'Отпразднуйте с нами', 'Организуем праздник в ресторане со скидкой 20%.'),
        ('Акция: раннее бронирование', 'Скидки при бронировании за 30 дней', 'Забронируйте номер за 30 дней и получите скидку 15%.'),
    ]
    for title, summary, content in news_data:
        Article.objects.get_or_create(
            title=title,
            defaults={'summary': summary, 'content': content, 'is_published': True}
        )
    print(f'📰 Создано {Article.objects.count()} новостей', flush=True)

    # =========================================================
    # 9. ОТЗЫВЫ
    # =========================================================
    reviews_data = [
        ('Анна', 5, 'Отличный отель! Чисто, уютно, персонал вежливый. Рекомендую!'),
        ('Михаил', 4, 'Хороший номер, удобная кровать. Завтрак вкусный.'),
        ('Екатерина', 5, 'Шикарный вид из окна. SPA понравилось. Вернусь ещё.'),
        ('Дмитрий', 3, 'Неплохо, но дороговато. В целом нормально.'),
        ('Ольга', 5, 'Лучший отель в Минске! Обслуживание на высоте.'),
        ('Алексей', 4, 'Отличное расположение, чисто, уютно.'),
    ]
    for name, rating, text in reviews_data:
        Review.objects.get_or_create(
            name=name,
            defaults={'rating': rating, 'text': text, 'is_approved': True}
        )
    print(f'💬 Создано {Review.objects.count()} отзывов', flush=True)

    # =========================================================
    # 10. ПРОМОКОДЫ
    # =========================================================
    today = date.today()
    PromoCode.objects.get_or_create(
        code='WELCOME10',
        defaults={
            'description': 'Скидка 10% на первое бронирование',
            'discount_percent': 10,
            'valid_from': today - timedelta(days=30),
            'valid_to': today + timedelta(days=90),
            'is_active': True
        }
    )
    PromoCode.objects.get_or_create(
        code='SPRING25',
        defaults={
            'description': 'Весенняя акция — скидка 25%',
            'discount_percent': 25,
            'valid_from': today - timedelta(days=10),
            'valid_to': today + timedelta(days=30),
            'is_active': True
        }
    )
    print(f'🎫 Создано {PromoCode.objects.count()} промокодов', flush=True)

    # =========================================================
    # 11. ВАКАНСИИ
    # =========================================================
    Vacancy.objects.get_or_create(
        title='Администратор ресепшн',
        defaults={
            'description': 'Встреча гостей, оформление броней.',
            'requirements': 'Английский язык, опыт от 1 года.',
            'salary_from': 800,
            'salary_to': 1200,
            'is_active': True
        }
    )
    Vacancy.objects.get_or_create(
        title='Горничная',
        defaults={
            'description': 'Уборка номеров и общественных зон.',
            'requirements': 'Опыт не обязателен.',
            'salary_from': 600,
            'salary_to': 800,
            'is_active': True
        }
    )
    print(f'💼 Создано {Vacancy.objects.count()} вакансий', flush=True)

    # =========================================================
    # 12. СЛОВАРЬ ТЕРМИНОВ
    # =========================================================
    terms_data = [
        ('Check-in', 'Время заезда в отель (обычно после 14:00).'),
        ('Check-out', 'Время выезда из отеля (обычно до 12:00).'),
        ('Консьерж', 'Сотрудник отеля, помогающий гостям с различными услугами.'),
        ('Люкс', 'Номер повышенной комфортности с дополнительными услугами.'),
        ('Овербукинг', 'Ситуация, когда забронировано больше номеров, чем есть в наличии.'),
    ]
    for term, definition in terms_data:
        GlossaryTerm.objects.get_or_create(term=term, defaults={'definition': definition})
    print(f'📚 Создано {GlossaryTerm.objects.count()} терминов', flush=True)

    # =========================================================
    # 13. БРОНИ
    # =========================================================
    rooms_list = list(Room.objects.all())
    clients_list = list(Client.objects.all())
    statuses = ['confirmed', 'confirmed', 'checked_in', 'checked_out', 'confirmed', 'checked_out', 'cancelled']

    for i in range(20):
        room = rooms_list[i % len(rooms_list)]
        client = clients_list[i % len(clients_list)]
        check_in = today - timedelta(days=i * 3 + 5)
        check_out = check_in + timedelta(days=random.randint(1, 5))
        status = random.choice(statuses)
        total = room.price_per_night * (check_out - check_in).days

        Booking.objects.get_or_create(
            room=room,
            client=client,
            check_in=check_in,
            defaults={
                'check_out': check_out,
                'status': status,
                'guests_count': min(room.capacity, random.randint(1, 4)),
                'total_price': total,
            }
        )
    print(f'📅 Создано {Booking.objects.count()} броней', flush=True)

    # =========================================================
    # 14. ИТОГИ
    # =========================================================
    print("\n" + "=" * 50)
    print("ЗАГРУЗКА ЗАВЕРШЕНА УСПЕШНО!")
    print("=" * 50)
    print(f"👤 Суперпользователь: admin / admin123")
    print(f"👔 Сотрудник: receptionist_a / emp123")
    print(f"👥 Клиент: client1 / client123")
    print(f"📊 Статистика сайта:")
    print(f"   - Номеров: {Room.objects.count()}")
    print(f"   - Броней: {Booking.objects.count()}")
    print(f"   - Клиентов: {Client.objects.count()}")
    print("=" * 50, flush=True)

if __name__ == '__main__':
    seed()