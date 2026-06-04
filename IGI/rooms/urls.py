from django.urls import re_path
from . import views
app_name = 'rooms'
urlpatterns = [
    re_path(r'^$', views.home, name='home'),
    re_path(r'^about/$', views.about, name='about'),
    re_path(r'^news/$', views.news_list, name='news'),
    re_path(r'^news/(?P<pk>\d+)/$', views.news_detail, name='news_detail'),
    re_path(r'^glossary/$', views.glossary, name='glossary'),
    re_path(r'^contacts/$', views.contacts, name='contacts'),
    re_path(r'^privacy/$', views.privacy, name='privacy'),
    re_path(r'^vacancies/$', views.vacancies, name='vacancies'),
    re_path(r'^reviews/$', views.reviews, name='reviews'),
    re_path(r'^reviews/(?P<pk>\d+)/edit/$', views.review_update, name='review_update'),
    re_path(r'^reviews/(?P<pk>\d+)/delete/$', views.review_delete, name='review_delete'),
    re_path(r'^promos/$', views.promo_codes, name='promos'),
    # Номера CRUD
    re_path(r'^rooms/$', views.room_list, name='room_list'),
    re_path(r'^rooms/(?P<pk>\d+)/$', views.room_detail, name='room_detail'),
    re_path(r'^rooms/create/$', views.room_create, name='room_create'),
    re_path(r'^rooms/(?P<pk>\d+)/edit/$', views.room_update, name='room_update'),
    re_path(r'^rooms/(?P<pk>\d+)/delete/$', views.room_delete, name='room_delete'),
    # Брони CRUD
    re_path(r'^bookings/$', views.booking_list, name='booking_list'),
    re_path(r'^bookings/(?P<pk>\d+)/$', views.booking_detail, name='booking_detail'),
    re_path(r'^bookings/create/$', views.booking_create, name='booking_create'),
    re_path(r'^bookings/(?P<pk>\d+)/edit/$', views.booking_update, name='booking_update'),
    re_path(r'^bookings/(?P<pk>\d+)/delete/$', views.booking_delete, name='booking_delete'),
    # Клиенты CRUD
    re_path(r'^clients/$', views.client_list, name='client_list'),
    re_path(r'^clients/create/$', views.client_create, name='client_create'),
    re_path(r'^clients/(?P<pk>\d+)/edit/$', views.client_update, name='client_update'),
    re_path(r'^clients/(?P<pk>\d+)/delete/$', views.client_delete, name='client_delete'),
    # Статистика
    re_path(r'^statistics/$', views.statistics, name='statistics'),
    re_path(r'^statistics/chart/$', views.chart_python, name='chart_python'),
]
