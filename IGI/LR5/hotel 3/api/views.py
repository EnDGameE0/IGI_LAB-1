from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rooms.models import Room, Booking, Client
from django.db.models import Sum, Count

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_rooms(request):
    qs = Room.objects.filter(is_available=True).values(
        'id','number','category__name','capacity','price_per_night','floor','is_available')
    return Response(list(qs))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_room_detail(request, pk):
    try:
        r = Room.objects.get(pk=pk)
    except Room.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    return Response({
        'id': r.pk, 'number': r.number, 'category': r.category.name,
        'capacity': r.capacity, 'price_per_night': str(r.price_per_night),
        'floor': r.floor, 'description': r.description, 'is_available': r.is_available,
        'created_at': r.created_at.strftime('%d/%m/%Y'),
    })

@api_view(['GET'])
@permission_classes([IsAdminUser])
def api_statistics(request):
    return Response({
        'total_rooms': Room.objects.count(),
        'total_bookings': Booking.objects.count(),
        'completed_bookings': Booking.objects.filter(status='checked_out').count(),
        'total_clients': Client.objects.count(),
        'total_revenue': str(Booking.objects.filter(status='checked_out').aggregate(
            s=Sum('total_price'))['s'] or 0),
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_my_bookings(request):
    user = request.user
    if user.is_client():
        try:
            bookings = Booking.objects.filter(client=user.client_profile).values(
                'id','room__number','status','total_price','check_in','check_out')
            return Response(list(bookings))
        except Exception:
            return Response([])
    return Response({'error': 'Forbidden'}, status=403)
