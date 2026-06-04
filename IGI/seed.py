#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel.settings')
django.setup()

from rooms.models import RoomCategory, Room

def seed():
    print("Начинаем загрузку данных...", flush=True)
    
    # Создаём категории (используем RoomCategory, а не Category)
    categories = {
        'standard': {'name': 'Стандартный', 'comfort': 'standard', 'description': 'Стандартные номера с базовыми удобствами'},
        'semi_lux': {'name': 'Полулюкс', 'comfort': 'semi_lux', 'description': 'Номера повышенной комфортности'},
        'lux': {'name': 'Люкс', 'comfort': 'lux', 'description': 'Люксовые номера с дополнительным сервисом'},
        'suite': {'name': 'Апартаменты', 'comfort': 'suite', 'description': 'Просторные апартаменты'},
    }
    
    created_cats = {}
    for key, cat_data in categories.items():
        cat, created = RoomCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'comfort': cat_data['comfort'],
                'description': cat_data['description']
            }
        )
        created_cats[key] = cat
        print(f'Категория "{cat.name}": {"создана" if created else "уже существует"}', flush=True)
    
    # Данные номеров (обратите внимание на поле price_per_night вместо price)
    rooms_data = [
        # Стандартные номера
        {'number': '101', 'category': 'standard', 'capacity': 1, 'floor': 1, 'area': 18.0, 
         'price_per_night': 55.0, 'description': 'Уютный одноместный номер на первом этаже',
         'amenities': 'Wi-Fi, ТВ, кондиционер'},
        {'number': '102', 'category': 'standard', 'capacity': 2, 'floor': 1, 'area': 22.0, 
         'price_per_night': 75.0, 'description': 'Стандартный двухместный номер'},
        {'number': '103', 'category': 'standard', 'capacity': 2, 'floor': 1, 'area': 28.0, 
         'price_per_night': 85.0, 'description': 'Студия с мини-кухней'},
        {'number': '104', 'category': 'standard', 'capacity': 2, 'floor': 2, 'area': 24.0, 
         'price_per_night': 95.0, 'description': 'Номер с видом на город'},
        {'number': '105', 'category': 'standard', 'capacity': 3, 'floor': 2, 'area': 32.0, 
         'price_per_night': 110.0, 'description': 'Семейный номер'},
        
        # Полулюкс
        {'number': '201', 'category': 'semi_lux', 'capacity': 2, 'floor': 2, 'area': 45.0, 
         'price_per_night': 180.0, 'description': 'Полулюкс с гостиной зоной',
         'amenities': 'Wi-Fi, ТВ, кондиционер, мини-бар, халат'},
        {'number': '202', 'category': 'semi_lux', 'capacity': 2, 'floor': 2, 'area': 48.0, 
         'price_per_night': 200.0, 'description': 'Полулюкс с видом на парк'},
        
        # Люкс
        {'number': '301', 'category': 'lux', 'capacity': 2, 'floor': 3, 'area': 55.0, 
         'price_per_night': 250.0, 'description': 'Люкс с джакузи и панорамным видом',
         'amenities': 'Wi-Fi, ТВ, кондиционер, мини-бар, джакузи, халат, тапочки'},
        {'number': '302', 'category': 'lux', 'capacity': 3, 'floor': 3, 'area': 60.0, 
         'price_per_night': 280.0, 'description': 'Люкс с отдельной спальней'},
        
        # Апартаменты
        {'number': '401', 'category': 'suite', 'capacity': 4, 'floor': 4, 'area': 85.0, 
         'price_per_night': 380.0, 'description': 'Президентский люкс с кухней и двумя спальнями',
         'amenities': 'Wi-Fi, ТВ, кондиционер, полноценная кухня, джакузи, сауна, халат, тапочки'},
    ]
    
    created_count = 0
    existing_count = 0
    
    for data in rooms_data:
        category = created_cats[data['category']]
        room_data = {k: v for k, v in data.items() if k != 'category'}
        
        room, created = Room.objects.get_or_create(
            number=data['number'],
            defaults={'category': category, **room_data}
        )
        
        if created:
            created_count += 1
            print(f'✓ Создан номер {room.number} - {room.category.name}', flush=True)
        else:
            existing_count += 1
    
    print(f'\n✅ Готово! Создано {created_count} номеров, {existing_count} уже существовали.', flush=True)
    print(f'📊 Всего номеров в базе: {Room.objects.count()}', flush=True)
    print(f'📊 Всего категорий: {RoomCategory.objects.count()}', flush=True)

if __name__ == '__main__':
    seed()