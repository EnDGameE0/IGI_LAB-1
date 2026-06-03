from django.urls import re_path
from . import views
app_name = 'api'
urlpatterns = [
    re_path(r'^rooms/$', views.api_rooms, name='rooms'),
    re_path(r'^rooms/(?P<pk>\d+)/$', views.api_room_detail, name='room_detail'),
    re_path(r'^statistics/$', views.api_statistics, name='statistics'),
    re_path(r'^my-bookings/$', views.api_my_bookings, name='my_bookings'),
]
