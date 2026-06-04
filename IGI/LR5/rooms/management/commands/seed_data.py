import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rooms.models import (RoomCategory, Room, RoomTag, Employee, Client,
                           Booking, Payment, Article, CompanyInfo,
                           GlossaryTerm, Review, Vacancy, PromoCode)

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database — Вариант 2 Гостиница'

    def add_arguments(self, parser):
        parser.add_argument('--skip-if-exists', action='store_true')

    def handle(self, *args, **options):
        if options.get('skip_if_exists'):
            if User.objects.filter(username='admin').exists():
                self.stdout.write('✓ Already seeded.')
                return

        self.stdout.write('Seeding...')

        # Users
        u_admin, _ = User.objects.get_or_create(username='admin', defaults=dict(
            first_name='Администратор', last_name='Системы',
            email='admin@hotel.by', role='admin', is_staff=True, is_superuser=True))
        u_admin.set_password('admin123'); u_admin.save()

        emp_users = [
            ('receptionist_a', 'Анна', 'Иванова', '+375 (29) 111-11-11', date(1990,3,15), 'admin'),
            ('manager_s', 'Сергей', 'Петров', '+375 (33) 222-22-22', date(1985,7,22), 'manager'),
            ('concierge_t', 'Татьяна', 'Сидорова', '+375 (44) 333-33-33', date(1992,11,8), 'concierge'),
        ]
        employees = []
        positions = ['admin', 'manager', 'concierge']
        for i, (uname, fn, ln, phone, bd, pos) in enumerate(emp_users):
            u, c = User.objects.get_or_create(username=uname, defaults=dict(
                first_name=fn, last_name=ln, email=f'{uname}@hotel.by',
                role='employee', phone=phone, birth_date=bd))
            if c: u.set_password('emp123'); u.save()
            emp, _ = Employee.objects.get_or_create(user=u, defaults=dict(
                position=positions[i], hire_date=date(2019, 1, 15),
                salary=Decimal('1200.00')))
            employees.append(emp)

        u_client, c = User.objects.get_or_create(username='client1', defaults=dict(
            first_name='Мария', last_name='Козлова', email='maria@mail.by',
            role='client', birth_date=date(1995, 6, 10)))
        if c: u_client.set_password('client123'); u_client.save()

        # Company
        CompanyInfo.objects.get_or_create(name='Гостиница «Олимп»', defaults=dict(
            description='Комфортабельная гостиница в центре Минска. Номера различных категорий, ресторан, SPA.',
            founded_year=2005, address='г. Минск, пр. Независимости, 42',
            phone='+375 (17) 300-40-50', email='info@olimp-hotel.by', stars=4,
            history='2005 — открытие\n2010 — реновация\n2015 — открытие SPA\n2020 — расширение до 80 номеров'))

        # Categories (10)
        cats_data = [
            ('Стандарт одноместный', 'standard'),
            ('Стандарт двухместный', 'standard'),
            ('Улучшенный стандарт', 'standard'),
            ('Полулюкс', 'semi_lux'),
            ('Полулюкс семейный', 'semi_lux'),
            ('Люкс', 'lux'),
            ('Люкс с видом', 'lux'),
            ('Апартаменты', 'suite'),
            ('Апартаменты Президентские', 'suite'),
            ('Студия', 'standard'),
        ]
        cats = []
        for name, comfort in cats_data:
            cat, _ = RoomCategory.objects.get_or_create(name=name, defaults=dict(
                comfort=comfort, description=f'Категория {name}'))
            cats.append(cat)

        # Tags
        tag_names = ['Wi-Fi','Кондиционер','Мини-бар','Джакузи','Балкон','Вид на город','Завтрак включён','Сейф']
        tags = [RoomTag.objects.get_or_create(name=t)[0] for t in tag_names]

        # Rooms (12)
        rooms_data = [
            ('101', cats[0], 1, Decimal('55.00'), 1, 18.0, 'Уютный одноместный номер на первом этаже'),
            ('102', cats[1], 2, Decimal('75.00'), 1, 22.0, 'Стандартный двухместный номер'),
            ('201', cats[2], 2, Decimal('95.00'), 2, 25.0, 'Улучшенный номер с мини-баром'),
            ('202', cats[1], 2, Decimal('75.00'), 2, 22.0, 'Двухместный с видом на двор'),
            ('301', cats[3], 2, Decimal('130.00'), 3, 35.0, 'Полулюкс с диваном и рабочей зоной'),
            ('302', cats[4], 4, Decimal('155.00'), 3, 45.0, 'Семейный номер с детской кроваткой'),
            ('401', cats[5], 2, Decimal('200.00'), 4, 50.0, 'Люкс с панорамным видом на город'),
            ('402', cats[6], 2, Decimal('220.00'), 4, 55.0, 'Люкс с балконом и джакузи'),
            ('501', cats[7], 4, Decimal('320.00'), 5, 80.0, 'Апартаменты — гостиная + спальня + кухня'),
            ('502', cats[8], 6, Decimal('500.00'), 5, 120.0, 'Президентские апартаменты'),
            ('103', cats[9], 2, Decimal('85.00'), 1, 28.0, 'Студия с мини-кухней'),
            ('203', cats[2], 2, Decimal('95.00'), 2, 25.0, 'Улучшенный с балконом'),
        ]
        room_objs = []
        for number, cat, cap, price, floor, area, desc in rooms_data:
            r, _ = Room.objects.get_or_create(number=number, defaults=dict(
                category=cat, capacity=cap, price_per_night=price,
                floor=floor, area=area, description=desc, is_available=True))
            if _: r.tags.set(random.sample(tags, 3))
            room_objs.append(r)

        # Clients (10)
        clients_data = [
            ('Захарова', 'Ольга', 'Дмитриевна', '+375 (29) 601-11-11', 'o.z@mail.by', False),
            ('Воробьёв', 'Павел', 'Сергеевич', '+375 (33) 602-22-22', 'p.v@mail.by', False),
            ('Фёдорова', 'Ирина', 'Андреевна', '+375 (44) 603-33-33', 'i.f@mail.by', True),
            ('Кузнецов', 'Алексей', 'Юрьевич', '+375 (29) 604-44-44', 'a.k@mail.by', False),
            ('Попова', 'Наталья', 'Вячеславовна', '+375 (33) 605-55-55', 'n.p@mail.by', True),
            ('Лебедев', 'Егор', 'Николаевич', '+375 (44) 606-66-66', 'e.l@mail.by', False),
            ('Смирнова', 'Виктория', 'Ивановна', '+375 (29) 607-77-77', 'v.s@mail.by', False),
            ('Тихонов', 'Роман', 'Владимирович', '+375 (33) 608-88-88', 'r.t@mail.by', False),
            ('Козлова', 'Мария', 'Петровна', '+375 (44) 609-99-99', 'maria@mail.by', False),
            ('Новиков', 'Виктор', 'Игоревич', '+375 (29) 610-00-00', 'v.n@mail.by', True),
        ]
        clients = []
        for ln, fn, mn, phone, email, children in clients_data:
            cl, _ = Client.objects.get_or_create(last_name=ln, first_name=fn, defaults=dict(
                middle_name=mn, phone=phone, email=email, has_children=children))
            clients.append(cl)
        if not clients[8].user:
            clients[8].user = u_client; clients[8].save()

        # Promcodes (10)
        today = date.today()
        pcodes = [
            ('HOTEL10','Скидка 10%',10,True,0,60),
            ('WEEKEND','Выходные -15%',15,True,0,30),
            ('VIP20','VIP гость',20,True,0,180),
            ('FAMILY','Семья с детьми',8,True,0,90),
            ('BUSINESS','Командировка',12,True,0,365),
            ('LONGSTAY','Длительное проживание',15,True,0,365),
            ('BDAY','Скидка в ДР',10,True,0,365),
            ('CORP','Корпоративный',10,True,0,365),
            ('WINTER23','Зима 2023',7,False,-365,-30),
            ('SPRING23','Весна 2023',10,False,-365,-30),
        ]
        for code, desc, pct, active, df, dt in pcodes:
            PromoCode.objects.get_or_create(code=code, defaults=dict(
                description=desc, discount_percent=pct, is_active=active,
                valid_from=today+timedelta(days=df),
                valid_to=today+timedelta(days=dt)))

        # Bookings (10)
        statuses = ['checked_out','checked_out','checked_out','checked_out','checked_out',
                    'confirmed','checked_in','confirmed','cancelled','confirmed']
        for i in range(10):
            cl = clients[i]
            room = room_objs[i % len(room_objs)]
            emp = employees[i % len(employees)]
            check_in = today - timedelta(days=i*10+5)
            check_out = check_in + timedelta(days=random.randint(2,5))
            nights = (check_out - check_in).days
            total = room.price_per_night * nights
            Booking.objects.get_or_create(
                client=cl, check_in=check_in,
                defaults=dict(room=room, employee=emp, check_out=check_out,
                              status=statuses[i], total_price=total, guests_count=random.randint(1,2)))

        # Articles (10)
        arts = [
            ('Новый SPA-комплекс открылся!','Приглашаем насладиться новым SPA','Гостиница «Олимп» рада сообщить об открытии современного SPA-комплекса.'),
            ('Летнее меню ресторана','Свежие блюда этого сезона','Наш шеф-повар подготовил специальное летнее меню с локальными продуктами.'),
            ('Конференц-зал для бизнеса','Аренда зала для мероприятий','Предлагаем современный конференц-зал вместимостью до 50 человек.'),
            ('Экскурсии по Минску','Организуем туры для гостей','Наши консьержи помогут организовать интересные экскурсии по городу.'),
            ('Акция: ранее бронирование','Скидки при бронировании за 30 дней','При раннем бронировании предоставляется скидка до 20% на любой номер.'),
            ('Новые апартаменты','Представляем расширенный номерной фонд','Пять новых апартаментов класса люкс доступны для бронирования.'),
            ('День рождения в «Олимпе»','Отпразднуйте с нами','Специальная программа для именинников включает торт и шампанское.'),
            ('Фитнес-центр обновлён','Новое оборудование в зале','Установлено современное тренажёрное оборудование ведущих брендов.'),
            ('Трансфер из аэропорта','Новая услуга для гостей','Теперь доступна услуга трансфера от аэропорта прямо до гостиницы.'),
            ('Детская комната открыта','Игровая зона для маленьких гостей','Оборудована просторная игровая комната для детей.'),
        ]
        for title, summary, content in arts:
            Article.objects.get_or_create(title=title, defaults=dict(
                summary=summary, content=content, is_published=True))

        # GlossaryTerms (10)
        terms = [
            ('Check-in','Процедура заселения в гостиницу — регистрация гостя и получение ключа от номера.'),
            ('Check-out','Процедура выселения из гостиницы, сдача номера и ключей.'),
            ('Люкс','Номер высшей категории с расширенным набором услуг и увеличенной площадью.'),
            ('Ранний заезд','Заселение в номер до официального времени check-in (обычно 14:00).'),
            ('Поздний выезд','Право остаться в номере после официального времени check-out (12:00).'),
            ('Депозит','Гарантийная сумма, блокируемая при заселении на случай дополнительных расходов.'),
            ('Континентальный завтрак','Лёгкий завтрак: кофе/чай, сок, выпечка, масло, джем.'),
            ('Двойное занятие','Проживание двух гостей в одном номере.'),
            ('Оверсейл','Ситуация, когда броней больше, чем доступных номеров.'),
            ('Консьерж','Сотрудник гостиницы, помогающий гостям с организацией различных услуг.'),
        ]
        for term, defn in terms:
            GlossaryTerm.objects.get_or_create(term=term, defaults={'definition': defn})

        # Reviews (10)
        revs = [
            ('Алексей М.', 5, 'Отличная гостиница! Чистые номера, вежливый персонал. Обязательно вернусь.'),
            ('Светлана К.', 4, 'Хорошее расположение, удобный номер. Завтрак мог бы быть разнообразнее.'),
            ('Андрей В.', 5, 'Отдыхал с семьёй. Детская комната очень понравилась детям!'),
            ('Марина Р.', 3, 'Средний уровень. Шумновато из-за дороги, но в целом нормально.'),
            ('Дмитрий Г.', 5, 'Останавливаюсь здесь в командировках уже 3 года. Всегда отлично.'),
            ('Ольга Н.', 5, 'SPA-комплекс просто великолепен! Рекомендую всем.'),
            ('Павел С.', 4, 'Хороший отель за свою цену. Персонал отзывчивый.'),
            ('Юлия Б.', 5, 'Праздновали годовщину свадьбы. Всё было идеально!'),
            ('Игорь Ф.', 4, 'Чистые номера, быстрый Wi-Fi. Немного дорого для стандарта.'),
            ('Наталья Д.', 5, 'Прекрасный отель! Вид из окна номера 401 просто захватывает.'),
        ]
        for name, rating, text in revs:
            Review.objects.get_or_create(name=name, defaults=dict(
                rating=rating, text=text, is_approved=True))

        # Vacancies (10)
        vacs = [
            ('Администратор ресепшн','Встреча гостей, check-in/check-out, работа с бронированием.',700,1100),
            ('Горничная','Уборка номеров, поддержание порядка на этажах.',550,800),
            ('Менеджер по бронированию','Обработка онлайн-броней, работа с клиентами.',800,1200),
            ('Консьерж','Помощь гостям в организации экскурсий и услуг.',700,1000),
            ('Шеф-повар','Разработка меню ресторана, приготовление блюд.',1500,2500),
            ('Повар','Приготовление блюд по меню. Опыт от 2 лет.',800,1200),
            ('Охранник','Безопасность гостей и сотрудников. График 2/2.',600,900),
            ('Маркетолог','SMM, реклама, продвижение гостиницы.',900,1400),
            ('Бухгалтер','Ведение бухгалтерского учёта. Опыт от 3 лет.',1000,1600),
            ('Технический специалист','Обслуживание инженерных систем здания.',800,1200),
        ]
        for title, desc, sf, st in vacs:
            Vacancy.objects.get_or_create(title=title, defaults=dict(
                description=desc, salary_from=sf, salary_to=st, is_active=True))

        self.stdout.write(self.style.SUCCESS(
            '✓ Done! admin/admin123 | emp: receptionist_a/emp123 | client: client1/client123'))
