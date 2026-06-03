import re
from django import forms
from django.core.exceptions import ValidationError
from .models import Room, Booking, Client, Review


class RoomFilterForm(forms.Form):
    search = forms.CharField(required=False, label='Поиск',
        widget=forms.TextInput(attrs={'placeholder': 'Название, описание...', 'class': 'form-control'}))
    category = forms.IntegerField(required=False,
        widget=forms.Select(attrs={'class': 'form-select'}))
    price_min = forms.DecimalField(required=False, label='Цена от',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '0'}))
    price_max = forms.DecimalField(required=False, label='Цена до',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '9999', 'min': '0'}))
    capacity = forms.IntegerField(required=False, label='Гостей',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1', 'min': '1'}))
    is_available = forms.BooleanField(required=False, label='Только свободные',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    sort = forms.ChoiceField(required=False, choices=[
        ('', 'По умолчанию'),
        ('price_per_night', 'Цена ↑'),
        ('-price_per_night', 'Цена ↓'),
        ('capacity', 'Вместимость ↑'),
        ('number', 'По номеру'),
    ], widget=forms.Select(attrs={'class': 'form-select'}))


class RoomForm(forms.ModelForm):
    price_per_night = forms.DecimalField(
        min_value=0.01, max_digits=10, decimal_places=2,
        label='Цена за сутки (руб.)',
        widget=forms.NumberInput(attrs={
            'min': '0.01', 'step': '0.01',
            'class': 'form-control', 'placeholder': 'Например: 85.00'
        })
    )

    class Meta:
        model = Room
        exclude = ['created_at', 'updated_at']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'amenities': forms.Textarea(attrs={'rows': 2}),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def clean_price_per_night(self):
        price = self.cleaned_data.get('price_per_night')
        if price is not None and price <= 0:
            raise ValidationError('Цена должна быть больше 0.')
        if price is not None and price > 99999:
            raise ValidationError('Цена не может превышать 99 999 руб.')
        return price


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room', 'client', 'employee', 'check_in', 'check_out',
                  'status', 'promo_code', 'discount_amount', 'total_price',
                  'guests_count', 'special_requests', 'comment']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'special_requests': forms.Textarea(attrs={'rows': 2}),
            'comment': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get('check_in')
        check_out = cleaned.get('check_out')
        if check_in and check_out:
            if check_out <= check_in:
                raise ValidationError('Дата выезда должна быть позже даты заезда.')
        return cleaned


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ['user', 'created_at', 'updated_at']
        widgets = {'comment': forms.Textarea(attrs={'rows': 2})}

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone and not re.match(r'^\+375 \((29|33|44|25)\) \d{3}-\d{2}-\d{2}$', phone):
            raise ValidationError('Формат: +375 (29) XXX-XX-XX')
        return phone


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'rating', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'rating': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_text(self):
        text = self.cleaned_data.get('text', '')
        if len(text) < 10:
            raise ValidationError('Отзыв должен содержать не менее 10 символов.')
        return text


class ClientBookingForm(forms.ModelForm):
    """Упрощённая форма бронирования для клиентов (без полей администратора)."""
    class Meta:
        model = Booking
        fields = ['room', 'check_in', 'check_out', 'guests_count', 'special_requests']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'special_requests': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get('check_in')
        check_out = cleaned.get('check_out')
        if check_in and check_out:
            if check_out <= check_in:
                raise ValidationError('Дата выезда должна быть позже даты заезда.')
        return cleaned
