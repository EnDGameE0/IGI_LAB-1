from django.contrib import admin
from .models import (RoomCategory, Room, RoomTag, Employee, Client,
                     Booking, Payment, Article, CompanyInfo,
                     GlossaryTerm, Review, Vacancy, PromoCode)


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    fields = ['room', 'check_in', 'check_out', 'status', 'total_price']
    readonly_fields = ['total_price']


@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'comfort']
    list_filter = ['comfort']

@admin.register(RoomTag)
class RoomTagAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['number', 'category', 'capacity', 'price_per_night', 'floor', 'is_available']
    list_filter = ['category', 'is_available', 'floor']
    list_editable = ['is_available']
    search_fields = ['number', 'description']
    filter_horizontal = ['tags']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position', 'salary', 'hire_date', 'is_active']
    list_filter = ['position', 'is_active']
    list_editable = ['is_active']
    def full_name(self, obj): return obj.full_name
    full_name.short_description = 'ФИО'

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'email', 'has_children', 'bookings_count']
    search_fields = ['first_name', 'last_name', 'phone']
    list_filter = ['has_children']
    inlines = [BookingInline]
    def full_name(self, obj): return obj.full_name
    full_name.short_description = 'ФИО'
    def bookings_count(self, obj): return obj.bookings.count()
    bookings_count.short_description = 'Броней'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'room', 'client', 'check_in', 'check_out', 'status', 'total_price']
    list_filter = ['status']
    list_editable = ['status']
    search_fields = ['client__last_name', 'room__number']
    date_hierarchy = 'check_in'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'amount', 'method', 'paid_at']
    list_filter = ['method']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'created_at']
    list_editable = ['is_published']

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'stars', 'phone', 'email']

@admin.register(GlossaryTerm)
class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ['term', 'created_at']
    search_fields = ['term']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'is_approved', 'created_at']
    list_editable = ['is_approved']
    list_filter = ['rating', 'is_approved']

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'salary_from', 'salary_to', 'is_active']
    list_editable = ['is_active']

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'valid_from', 'valid_to', 'is_active']
    list_editable = ['is_active']
