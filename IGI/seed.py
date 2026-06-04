#!/usr/bin/env python
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel.settings')
django.setup()

from django.contrib.auth import get_user_model
from rooms.models import (
    RoomCategory, Room, Article, Review, PromoCode, Vacancy, 
    GlossaryTerm, Client, Booking, Employee
)

User = get_user_model()

def seed():
    print("Начинаем загрузку всех данных...", flush=True)
    
    # 1. Суперпользователь
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print('✅ Админ создан', flush=True)
    
    # 2. Категории номеров
    cats = {}
    for name, comfort in [('Стандартный','standard'),('Полулюкс','semi_lux'),('Люкс','lux'),('Апартаменты','suite')]:
        cat, _ = RoomCategory.objects.get_or_create(name=name, defaults={'comfort': comfort})
        cats[name] = cat
        print(f'📁 Категория: {name}', flush=True)
    
    # 3. Номера
    rooms_data = [
        ('101', 'Стандартный', 1, 55, 'Уютный одноместный номер'),
        ('102', 'Стандартный', 2, 75, 'Стандартный двухместный'),
        ('103', 'Стандартный', 2, 85, 'Студия с мини-кухней'),
        ('104', 'Стандартный', 2, 95, 'Номер с видом на город'),
        ('105', 'Стандартный', 3, 110, 'Семейный номер'),
        ('201', 'Полулюкс', 2, 180, 'Полулюкс с гостиной зоной'),
        ('202', 'Полулюкс', 2, 200, 'Полулюкс с видом на парк'),
        ('301', 'Люкс', 2, 250, 'Люкс с джакузи'),
        ('302', 'Люкс', 3, 280, 'Люкс с отдельной спальней'),
        ('401', 'Апартаменты', 4, 380, 'Президентский люкс'),
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
                'area': 20 + cap * 5
            }
        )
    print(f'🛏️ Создано {Room.objects.count()} номеров', flush=True)
    
    # 4. Новости (Article)
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
    ]
    for title, summary, content in news_data:
        Article.objects.get_or_create(
            title=title,
            defaults={'summary': summary, 'content': content, 'is_published': True}
        )
    print(f'📰 Создано {Article.objects.count()} новостей', flush=True)
    
    # 5. Отзывы (Review)
    reviews_data = [
        ('Анна', 5, 'Отличный отель! Чисто, уютно, персонал вежливый. Рекомендую!'),
        ('Михаил', 4, 'Хороший номер, удобная кровать. Завтрак вкусный.'),
        ('Екатерина', 5, 'Шикарный вид из окна. SPA понравилось. Вернусь ещё.'),
        ('Дмитрий', 3, 'Неплохо, но дороговато. В целом нормально.'),
    ]
    for name, rating, text in reviews_data:
        Review.objects.get_or_create(
            name=name,
            defaults={'rating': rating, 'text': text, 'is_approved': True}
        )
    print(f'💬 Создано {Review.objects.count()} отзывов', flush=True)
    
    # 6. Промокоды (PromoCode)
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
    
    # 7. Вакансии (Vacancy)
    Vacancy.objects.get_or_create(
        title='Администратор ресепшн',
        defaults={
            'description': 'Встреча гостей, оформление броней, работа в системе.',
            'requirements': 'Английский язык, опыт работы от 1 года.',
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
    
    # 8. Словарь терминов (GlossaryTerm)
    terms = [
        ('Check-in', 'Время заезда в отель (обычно после 14:00).'),
        ('Check-out', 'Время выезда из отеля (обычно до 12:00).'),
        ('Консьерж', 'Сотрудник отеля, помогающий гостям с различными услугами.'),
        ('Люкс', 'Номер повышенной комфортности.'),
        ('Овербукинг', 'Ситуация, когда забронировано больше номеров, чем есть в наличии.'),
    ]
    for term, definition in terms:
        GlossaryTerm.objects.get_or_create(term=term, defaults={'definition': definition})
    print(f'📚 Создано {GlossaryTerm.objects.count()} терминов', flush=True)
    
    # 9. Клиенты (Client)
    clients_data = [
        ('Иван', 'Петров', '+375291234567', 'ivan@mail.ru'),
        ('Мария', 'Иванова', '+375293334455', 'maria@mail.ru'),
        ('Сергей', 'Сидоров', '+375445556677', 'sergey@mail.ru'),
    ]
    for first, last, phone, email in clients_data:
        Client.objects.get_or_create(
            first_name=first,
            last_name=last,
            defaults={'phone': phone, 'email': email}
        )
    print(f'👥 Создано {Client.objects.count()} клиентов', flush=True)
    
    print('\n✅ ВСЕ ДАННЫЕ УСПЕШНО ЗАГРУЖЕНЫ!', flush=True)

if __name__ == '__main__':
    seed()