#!/usr/bin/env python
import os
import django
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel.settings')
django.setup()

from django.contrib.auth import get_user_model
from rooms.models import (
    RoomCategory, Room, Article, Review, PromoCode, Vacancy, 
    GlossaryTerm, Client, Booking, Employee, CompanyInfo
)

User = get_user_model()

def seed():
    print("Начинаем загрузку ВСЕХ данных...", flush=True)
    
    # ==================== 1. ПОЛЬЗОВАТЕЛИ ====================
    # Суперпользователь
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print('✅ Админ создан (admin/admin123)', flush=True)
    
    # Обычные пользователи (клиенты)
    users_data = [
        ('client1', 'client1@example.com', 'client123', 'Иван', 'Петров', '+375291234567'),
        ('client2', 'client2@example.com', 'client123', 'Мария', 'Иванова', '+375293334455'),
        ('client3', 'client3@example.com', 'client123', 'Сергей', 'Сидоров', '+375445556677'),
        ('client4', 'client4@example.com', 'client123', 'Анна', 'Козлова', '+375296667788'),
        ('client5', 'client5@example.com', 'client123', 'Павел', 'Воробьёв', '+375336022222'),
        ('client6', 'client6@example.com', 'client123', 'Ольга', 'Захарова', '+375296011111'),
        ('client7', 'client7@example.com', 'client123', 'Виктор', 'Новиков', '+375296100000'),
        ('client8', 'client8@example.com', 'client123', 'Наталья', 'Попова', '+375336055555'),
        ('client9', 'client9@example.com', 'client123', 'Алексей', 'Кузнецов', '+375296044444'),
        ('client10', 'client10@example.com', 'client123', 'Егор', 'Лебедев', '+375446066666'),
    ]
    created_users = {}
    for username, email, pwd, first, last, phone in users_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first,
                'last_name': last,
                'phone': phone
            }
        )
        if created:
            user.set_password(pwd)
            user.save()
            print(f'👤 Создан пользователь {username}', flush=True)
        created_users[username] = user
    
    # ==================== 2. КОМПАНИЯ (О нас) ====================
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
    
    # ==================== 3. СОТРУДНИКИ ====================
    employees_data = [
        ('Анна', 'Иванова', 'admin', 'Администратор', '+375 (29) 111-11-11'),
        ('Сергей', 'Петров', 'manager', 'Менеджер', '+375 (33) 222-22-22'),
        ('Татьяна', 'Сидорова', 'concierge', 'Консьерж', '+375 (44) 333-33-33'),
        ('Ольга', 'Смирнова', 'cleaner', 'Горничная', '+375 (29) 444-44-44'),
        ('Дмитрий', 'Козлов', 'security', 'Охрана', '+375 (33) 555-55-55'),
    ]
    for first, last, pos, pos_display, phone in employees_data:
        Employee.objects.get_or_create(
            first_name=first,
            last_name=last,
            defaults={
                'position': pos,
                'hire_date': date(2023, 1, 1),
                'salary': 800,
                'phone': phone,
                'is_active': True
            }
        )
    print(f'👔 Создано {Employee.objects.count()} сотрудников', flush=True)
    
    # ==================== 4. КАТЕГОРИИ НОМЕРОВ ====================
    cats = {}
    for name, comfort, desc in [
        ('Стандартный', 'standard', 'Стандартные номера с базовыми удобствами.'),
        ('Полулюкс', 'semi_lux', 'Номера повышенной комфортности с гостиной зоной.'),
        ('Люкс', 'lux', 'Люксовые номера с джакузи и панорамным видом.'),
        ('Апартаменты', 'suite', 'Просторные апартаменты с кухней и двумя спальнями.'),
    ]:
        cat, _ = RoomCategory.objects.get_or_create(
            name=name,
            defaults={'comfort': comfort, 'description': desc}
        )
        cats[name] = cat
    print(f'📁 Создано {RoomCategory.objects.count()} категорий', flush=True)
    
    # ==================== 5. НОМЕРА ====================
    rooms_data = [
        ('101', 'Стандартный', 1, 55, 'Уютный одноместный номер на первом этаже. Всё необходимое для комфортного проживания.'),
        ('102', 'Стандартный', 2, 75, 'Стандартный двухместный номер. Удобные кровати, телевизор, кондиционер.'),
        ('103', 'Стандартный', 2, 85, 'Студия с мини-кухней. Идеально для длительного проживания.'),
        ('104', 'Стандартный', 2, 95, 'Номер с видом на город. Панорамные окна.'),
        ('105', 'Стандартный', 3, 110, 'Семейный номер. Дополнительное спальное место.'),
        ('106', 'Стандартный', 2, 80, 'Номер с улучшенной звукоизоляцией.'),
        ('107', 'Стандартный', 1, 60, 'Эконом вариант для командировок.'),
        ('201', 'Полулюкс', 2, 180, 'Полулюкс с гостиной зоной. Отдельная спальня.'),
        ('202', 'Полулюкс', 2, 200, 'Полулюкс с видом на парк. Джакузи.'),
        ('203', 'Полулюкс', 3, 220, 'Полулюкс для семьи. Детская кровать.'),
        ('301', 'Люкс', 2, 250, 'Люкс с джакузи и панорамным видом. Гостиная, спальня, две ванны.'),
        ('302', 'Люкс', 3, 280, 'Люкс с отдельной спальней и кухней.'),
        ('303', 'Люкс', 2, 300, 'Президентский люкс. Сауна, бильярд.'),
        ('401', 'Апартаменты', 4, 380, 'Двухкомнатные апартаменты. Кухня, гостиная, две спальни.'),
        ('402', 'Апартаменты', 4, 400, 'Апартаменты с террасой. Вид на город.'),
    ]
    for num, cat_name, cap, price, desc in rooms_data:
        Room.objects.get_or_create(
            number=num,
            defaults={
                'category': cats[cat_name],
                'capacity': cap,
                'price_per_night': price,
                'description': desc,
                'floor': int(num[0]),
                'area': 18 + cap * 3,
                'is_available': True
            }
        )
    print(f'🛏️ Создано {Room.objects.count()} номеров', flush=True)
    
    # ==================== 6. НОВОСТИ (15 штук) ====================
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
    
    # ==================== 7. ОТЗЫВЫ (15 штук) ====================
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
    
    # ==================== 8. ПРОМОКОДЫ (10 штук) ====================
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
    
    # ==================== 9. ВАКАНСИИ (10 штук) ====================
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
    
    # ==================== 10. СЛОВАРЬ ТЕРМИНОВ ====================
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
    
    # ==================== 11. КЛИЕНТЫ (15 штук) ====================
    clients_data = [
        ('Иван', 'Петров', '', '+375291234567', 'ivan@mail.ru', 'MP1234567'),
        ('Мария', 'Иванова', '', '+375293334455', 'maria@mail.ru', 'MP2345678'),
        ('Сергей', 'Сидоров', '', '+375445556677', 'sergey@mail.ru', 'MP3456789'),
        ('Анна', 'Козлова', 'Петровна', '+375296667788', 'anna@mail.ru', 'MP4567890'),
        ('Павел', 'Воробьёв', 'Сергеевич', '+375336022222', 'pavel@mail.ru', 'MP5678901'),
        ('Ольга', 'Захарова', 'Дмитриевна', '+375296011111', 'olga@mail.ru', 'MP6789012'),
        ('Виктор', 'Новиков', 'Игоревич', '+375296100000', 'viktor@mail.ru', 'MP7890123'),
        ('Наталья', 'Попова', 'Вячеславовна', '+375336055555', 'natalia@mail.ru', 'MP8901234'),
        ('Алексей', 'Кузнецов', 'Юрьевич', '+375296044444', 'alexey@mail.ru', 'MP9012345'),
        ('Егор', 'Лебедев', 'Николаевич', '+375446066666', 'egor@mail.ru', 'MP0123456'),
        ('Дмитрий', 'Соколов', 'Андреевич', '+375291112233', 'dmitry@mail.ru', 'MP1237890'),
        ('Елена', 'Михайлова', 'Владимировна', '+375293334466', 'elena@mail.ru', 'MP2348901'),
        ('Андрей', 'Фёдоров', 'Иванович', '+375445556699', 'andrey@mail.ru', 'MP3459012'),
        ('Татьяна', 'Морозова', 'Викторовна', '+375296667799', 'tatyana@mail.ru', 'MP4560123'),
        ('Владимир', 'Волков', 'Сергеевич', '+375336022288', 'vladimir@mail.ru', 'MP5671234'),
    ]
    for first, last, middle, phone, email, passport in clients_data:
        Client.objects.get_or_create(
            first_name=first,
            last_name=last,
            defaults={
                'middle_name': middle,
                'phone': phone,
                'email': email,
                'passport': passport,
                'has_children': len(middle) > 0 and 'Петровна' not in middle
            }
        )
    print(f'👥 Создано {Client.objects.count()} клиентов', flush=True)
    
    # ==================== 12. БРОНИ (20 штук) ====================
    rooms_list = list(Room.objects.all())
    clients_list = list(Client.objects.all())
    statuses = ['confirmed', 'confirmed', 'checked_in', 'checked_out', 'confirmed', 'checked_out', 'cancelled']
    
    for i in range(20):
        room = rooms_list[i % len(rooms_list)]
        client = clients_list[i % len(clients_list)]
        check_in = today - timedelta(days=i * 3)
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
    
    print('\n' + '='*50)
    print('✅ ВСЕ ДАННЫЕ УСПЕШНО ЗАГРУЖЕНЫ!')
    print(f'👤 Пользователей: {User.objects.count()}')
    print(f'🏢 Компания: {CompanyInfo.objects.count()}')
    print(f'👔 Сотрудников: {Employee.objects.count()}')
    print(f'📁 Категорий: {RoomCategory.objects.count()}')
    print(f'🛏️ Номеров: {Room.objects.count()}')
    print(f'📰 Новостей: {Article.objects.count()}')
    print(f'💬 Отзывов: {Review.objects.count()}')
    print(f'🎫 Промокодов: {PromoCode.objects.count()}')
    print(f'💼 Вакансий: {Vacancy.objects.count()}')
    print(f'📚 Терминов: {GlossaryTerm.objects.count()}')
    print(f'👥 Клиентов: {Client.objects.count()}')
    print(f'📅 Броней: {Booking.objects.count()}')
    print('='*50, flush=True)

if __name__ == '__main__':
    import random
    seed()