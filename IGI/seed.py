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
    # 2. ОБЫЧНЫЕ ПОЛЬЗОВАТЕЛИ (клиенты + сотрудники)
    # =========================================================
    users_data = [
        # Клиенты
        ('client1', 'client1@example.com', 'client123', 'Иван', 'Петров', '+375291234567', date(1990, 5, 15)),
        ('client2', 'client2@example.com', 'client123', 'Мария', 'Иванова', '+375293334455', date(1985, 8, 22)),
        ('client3', 'client3@example.com', 'client123', 'Сергей', 'Сидоров', '+375445556677', date(1995, 3, 10)),
        ('client4', 'client4@example.com', 'client123', 'Анна', 'Козлова', '+375296667788', date(1988, 11, 30)),
        ('client5', 'client5@example.com', 'client123', 'Павел', 'Воробьёв', '+375336022222', date(2000, 1, 20)),
        ('client6', 'client6@example.com', 'client123', 'Ольга', 'Захарова', '+375296011111', date(1992, 7, 7)),
        ('client7', 'client7@example.com', 'client123', 'Виктор', 'Новиков', '+375296100000', date(1980, 12, 1)),
        ('client8', 'client8@example.com', 'client123', 'Наталья', 'Попова', '+375336055555', date(1998, 6, 25)),
        ('client9', 'client9@example.com', 'client123', 'Алексей', 'Кузнецов', '+375296044444', date(1975, 4, 18)),
        ('client10', 'client10@example.com', 'client123', 'Егор', 'Лебедев', '+375446066666', date(2002, 9, 12)),
        # Сотрудники
        ('receptionist_a', 'receptionist_a@hotel.by', 'emp123', 'Анна', 'Иванова', '+375291111111', date(1988, 3, 10)),
        ('manager_b', 'manager_b@hotel.by', 'emp123', 'Сергей', 'Петров', '+375332222222', date(1985, 7, 20)),
        ('concierge_c', 'concierge_c@hotel.by', 'emp123', 'Татьяна', 'Сидорова', '+375443333333', date(1990, 11, 5)),
    ]

    created_users = {}
    for username, email, pwd, first, last, phone, birth in users_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first,
                'last_name': last,
                'phone': phone,
                'birth_date': birth
            }
        )
        if created:
            user.set_password(pwd)
            user.save()
            print(f'👤 Создан пользователь {username} ({first} {last})', flush=True)
        created_users[username] = user

    # =========================================================
    # 3. ИНФОРМАЦИЯ О КОМПАНИИ (О нас)
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
    # 4. СОТРУДНИКИ (связь с пользователями)
    # =========================================================
    employee_positions = {
        'receptionist_a': ('admin', date(2022, 1, 15), 1200),
        'manager_b': ('manager', date(2021, 6, 10), 1500),
        'concierge_c': ('concierge', date(2023, 3, 20), 900),
    }

    for username, (position, hire_date, salary) in employee_positions.items():
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
    # 5. КЛИЕНТЫ (связь с пользователями)
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
    # 7. НОМЕРА (15 штук)
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
    # 8. НОВОСТИ (15 штук)
    # =========================================================
    news_data = [
        ('Детская комната открыта', 'Игровая зона для маленьких гостей', 'Теперь в нашей гостинице есть детская комната с аниматором. Часы работы: 10:00-20:00.'),
        ('Фитнес-центр обновлён', 'Новое оборудование в зале', 'Мы закупили новые беговые дорожки и силовые тренажёры.'),
        ('Новые апартаменты', 'Представляем расширенный номерной фонд', 'Открылись новые просторные апартаменты на 4-м этаже.'),
        ('Трансфер из аэропорта', 'Новая услуга для гостей', 'Заказывайте трансфер из аэропорта Минск-2.'),
        ('День рождения в «Олимпе»', 'Отпразднуйте с нами', 'Организуем праздник в ресторане со скидкой 20%.'),
        ('Акция: раннее бронирование', 'Скидки при бронировании за 30 дней', 'Забронируйте номер за 30 дней и получите скидку 15%.'),
        ('Экскурсии по Минску', 'Организуем туры для гостей', 'Групповые и индивидуальные экскурсии по столице.'),
        ('Конференц-зал для бизнеса', 'Аренда зала для мероприятий', 'Вместимость до 50 человек. Оборудование входит в стоимость.'),
        ('Летнее меню ресторана', 'Свежие блюда этого сезона', 'Шеф-повар обновил меню: салаты, рыбные блюда, десерты.'),
        ('Новый SPA-комплекс', 'Приглашаем насладиться', 'Сауна, хамам, массажный кабинет.'),
        ('Новогодняя акция', 'Скидки до 30%', 'Забронируйте проживание на новогодние праздники.'),
        ('Бесплатный Wi-Fi', 'Скоростной интернет по всей гостинице', 'Мы модернизировали сеть Wi-Fi.'),
        ('Парковка для гостей', 'Бесплатная парковка', 'Охраняемая парковка на 50 мест.'),
        ('Ресторан "Олимп"', 'Новое меню от шеф-повара', 'Европейская и белорусская кухня.'),
        ('Бизнес-ланчи', 'Обеды для деловых людей', 'Скидка 10% при заказе от 5 персон.'),
    ]

    for title, summary, content in news_data:
        Article.objects.get_or_create(
            title=title,
            defaults={'summary': summary, 'content': content, 'is_published': True}
        )
    print(f'📰 Создано {Article.objects.count()} новостей', flush=True)

    # =========================================================
    # 9. ОТЗЫВЫ (15 штук)
    # =========================================================
    reviews_data = [
        ('Анна', 5, 'Отличный отель! Чисто, уютно, персонал вежливый. Рекомендую!'),
        ('Михаил', 4, 'Хороший номер, удобная кровать. Завтрак вкусный.'),
        ('Екатерина', 5, 'Шикарный вид из окна. SPA понравилось. Вернусь ещё.'),
        ('Дмитрий', 3, 'Неплохо, но дороговато. В целом нормально.'),
        ('Ольга', 5, 'Лучший отель в Минске! Обслуживание на высоте.'),
        ('Алексей', 4, 'Отличное расположение, чисто, уютно. Немного шумновато.'),
        ('Татьяна', 5, 'Великолепные апартаменты! Приеду ещё.'),
        ('Сергей', 4, 'Хороший отель для деловых поездок. Скоростной Wi-Fi.'),
        ('Наталья', 5, 'Прекрасный SPA! Массажистка профессионал.'),
        ('Павел', 4, 'Неплохо, но завтрак однообразный. Остальное хорошо.'),
        ('Мария', 5, 'Романтический уикенд удался! Спасибо персоналу.'),
        ('Владимир', 3, 'Номер хороший, но кондиционер шумел. Попросили переселить.'),
        ('Елена', 5, 'Отдыхала с детьми. Детская комната супер!'),
        ('Игорь', 4, 'Хороший отель. Цена/качество отличное.'),
        ('Светлана', 5, 'Шикарный вид, вкусные завтраки. Обязательно вернусь!'),
    ]

    for name, rating, text in reviews_data:
        Review.objects.get_or_create(
            name=name,
            defaults={'rating': rating, 'text': text, 'is_approved': True}
        )
    print(f'💬 Создано {Review.objects.count()} отзывов', flush=True)

    # =========================================================
    # 10. ПРОМОКОДЫ (10 штук)
    # =========================================================
    today = date.today()
    promos_data = [
        ('WELCOME10', 'Скидка 10% на первое бронирование', 10, today - timedelta(days=30), today + timedelta(days=90)),
        ('SPRING25', 'Весенняя акция — скидка 25%', 25, today - timedelta(days=10), today + timedelta(days=30)),
        ('SUMMER15', 'Летняя акция — скидка 15%', 15, today - timedelta(days=5), today + timedelta(days=60)),
        ('AUTUMN20', 'Осенняя акция — скидка 20%', 20, today + timedelta(days=30), today + timedelta(days=120)),
        ('WINTER30', 'Зимняя сказка — скидка 30%', 30, today + timedelta(days=90), today + timedelta(days=180)),
        ('BUSINESS10', 'Для деловых людей — скидка 10%', 10, today - timedelta(days=20), today + timedelta(days=45)),
        ('FAMILY15', 'Семейный отдых — скидка 15%', 15, today - timedelta(days=15), today + timedelta(days=75)),
        ('WEEKEND20', 'Уикенд со скидкой — 20%', 20, today - timedelta(days=7), today + timedelta(days=30)),
        ('LOYALTY5', 'Постоянным гостям — 5%', 5, today - timedelta(days=365), today + timedelta(days=365)),
        ('FIRST20', 'Первое бронирование — 20%', 20, today - timedelta(days=60), today + timedelta(days=60)),
    ]

    for code, desc, percent, v_from, v_to in promos_data:
        PromoCode.objects.get_or_create(
            code=code,
            defaults={
                'description': desc,
                'discount_percent': percent,
                'valid_from': v_from,
                'valid_to': v_to,
                'is_active': True
            }
        )
    print(f'🎫 Создано {PromoCode.objects.count()} промокодов', flush=True)

    # =========================================================
    # 11. ВАКАНСИИ (10 штук)
    # =========================================================
    vacancies_data = [
        ('Администратор ресепшн', 'Встреча гостей, оформление броней.', 'Английский язык, опыт от 1 года.', 800, 1200),
        ('Горничная', 'Уборка номеров и общественных зон.', 'Опыт не обязателен.', 600, 800),
        ('Менеджер по бронированию', 'Работа с заявками, консультации.', 'Английский, опыт в гостиничном бизнесе.', 1000, 1500),
        ('Шеф-повар', 'Руководство кухней ресторана.', 'Опыт работы от 3 лет.', 1500, 2500),
        ('Официант', 'Обслуживание гостей ресторана.', 'Приветствуется опыт.', 500, 700),
        ('SPA-терапевт', 'Массаж, уход за телом.', 'Наличие сертификатов.', 800, 1200),
        ('Инженер', 'Обслуживание инженерных систем.', 'Высшее техническое образование.', 1000, 1500),
        ('Бухгалтер', 'Ведение учёта и отчётности.', 'Опыт от 2 лет.', 900, 1300),
        ('Маркетолог', 'Продвижение гостиницы.', 'Опыт в digital-маркетинге.', 1000, 1600),
        ('Охранник', 'Обеспечение безопасности гостей.', 'Удостоверение ЧОП.', 600, 800),
    ]

    for title, desc, req, sal_from, sal_to in vacancies_data:
        Vacancy.objects.get_or_create(
            title=title,
            defaults={
                'description': desc,
                'requirements': req,
                'salary_from': sal_from,
                'salary_to': sal_to,
                'is_active': True
            }
        )
    print(f'💼 Создано {Vacancy.objects.count()} вакансий', flush=True)

    # =========================================================
    # 12. СЛОВАРЬ ТЕРМИНОВ (10 штук)
    # =========================================================
    terms_data = [
        ('Check-in', 'Время заезда в отель (обычно после 14:00).'),
        ('Check-out', 'Время выезда из отеля (обычно до 12:00).'),
        ('Консьерж', 'Сотрудник отеля, помогающий гостям с различными услугами.'),
        ('Люкс', 'Номер повышенной комфортности с дополнительными услугами.'),
        ('Овербукинг', 'Ситуация, когда забронировано больше номеров, чем есть в наличии.'),
        ('Депозит', 'Предварительная оплата за проживание или страховка.'),
        ('Двойное занятие', 'Проживание двух гостей в одном номере.'),
        ('Поздний выезд', 'Возможность выехать из номера позже стандартного времени.'),
        ('Ранний заезд', 'Возможность заехать в номер раньше стандартного времени.'),
        ('Континентальный завтрак', 'Лёгкий завтрак из кофе/чая, выпечки, масла, джема.'),
    ]

    for term, definition in terms_data:
        GlossaryTerm.objects.get_or_create(term=term, defaults={'definition': definition})
    print(f'📚 Создано {GlossaryTerm.objects.count()} терминов', flush=True)

    # =========================================================
    # 13. БРОНИ (30 штук для статистики)
    # =========================================================
    rooms_list = list(Room.objects.all())
    clients_list = list(Client.objects.all())
    statuses = ['confirmed', 'confirmed', 'checked_in', 'checked_out', 'confirmed', 'checked_out', 'cancelled']

    for i in range(30):
        room = rooms_list[i % len(rooms_list)]
        client = clients_list[i % len(clients_list)]
        check_in = today - timedelta(days=i * 2 + 5)
        check_out = check_in + timedelta(days=random.randint(1, 7))
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
                'special_requests': 'Просьба о тихом номере' if i % 3 == 0 else ''
            }
        )
    print(f'📅 Создано {Booking.objects.count()} броней', flush=True)

    # =========================================================
    # 14. ИТОГОВАЯ СТАТИСТИКА
    # =========================================================
    print("\n" + "=" * 50)
    print("ЗАГРУЗКА ЗАВЕРШЕНА УСПЕШНО!")
    print("=" * 50)
    print(f"👤 Суперпользователь: admin / admin123")
    print(f"👔 Сотрудники: receptionist_a / emp123, manager_b / emp123, concierge_c / emp123")
    print(f"👥 Клиент: client1 / client123")
    print(f"📊 Статистика сайта:")
    print(f"   - Пользователей: {User.objects.count()}")
    print(f"   - Сотрудников: {Employee.objects.count()}")
    print(f"   - Клиентов: {Client.objects.count()}")
    print(f"   - Категорий: {RoomCategory.objects.count()}")
    print(f"   - Номеров: {Room.objects.count()}")
    print(f"   - Новостей: {Article.objects.count()}")
    print(f"   - Отзывов: {Review.objects.count()}")
    print(f"   - Промокодов: {PromoCode.objects.count()}")
    print(f"   - Вакансий: {Vacancy.objects.count()}")
    print(f"   - Терминов: {GlossaryTerm.objects.count()}")
    print(f"   - Броней: {Booking.objects.count()}")
    print("=" * 50, flush=True)

if __name__ == '__main__':
    seed()