#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel.settings')
django.setup()

from rooms.models import Category, Room

def seed():
    print("Начинаем загрузку данных...")
    
    # Создаём категории
    categories = {
        'standard': {'name': 'Стандартный', 'description': 'Стандартные номера'},
        'lux': {'name': 'Люкс', 'description': 'Номера повышенной комфортности'},
    }
    
    created_cats = {}
    for key, cat_data in categories.items():
        cat, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        created_cats[key] = cat
        print(f'Категория "{cat.name}": {"создана" if created else "уже существует"}')
    
    # Данные номеров
    rooms_data = [
        # Стандартные номера
        {'number': '101', 'category': 'standard', 'capacity': 1, 'floor': 1, 'area': 18.0, 'price': 55.0, 'description': 'Уютный одноместный номер на первом этаже'},
        {'number': '102', 'category': 'standard', 'capacity': 2, 'floor': 1, 'area': 22.0, 'price': 75.0, 'description': 'Стандартный двухместный номер'},
        {'number': '103', 'category': 'standard', 'capacity': 2, 'floor': 1, 'area': 28.0, 'price': 85.0, 'description': 'Студия с мини-кухней'},
        {'number': '104', 'category': 'standard', 'capacity': 2, 'floor': 2, 'area': 24.0, 'price': 95.0, 'description': 'Номер с видом на город'},
        {'number': '105', 'category': 'standard', 'capacity': 3, 'floor': 2, 'area': 32.0, 'price': 110.0, 'description': 'Семейный номер'},
        
        # Люкс
        {'number': '201', 'category': 'lux', 'capacity': 2, 'floor': 2, 'area': 45.0, 'price': 180.0, 'description': 'Полулюкс с гостиной зоной'},
        {'number': '202', 'category': 'lux', 'capacity': 2, 'floor': 3, 'area': 55.0, 'price': 250.0, 'description': 'Люкс с джакузи и панорамным видом'},
        {'number': '203', 'category': 'lux', 'capacity': 4, 'floor': 3, 'area': 70.0, 'price': 320.0, 'description': 'Президентский люкс с кухней и двумя спальнями'},
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
            print(f'✓ Создан номер {room.number} - {room.category.name}')
        else:
            existing_count += 1
    
    print(f'\n✅ Готово! Создано {created_count} номеров, {existing_count} уже существовали.')
    print(f'📊 Всего номеров в базе: {Room.objects.count()}')

if __name__ == '__main__':
    seed()

