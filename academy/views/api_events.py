from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ..models import Event, Ticket
from ..serializers import EventSerializer, TicketSerializer

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.filter(is_active=True).order_by('start_date')
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action in ['register', 'my_tickets']:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        event = self.get_object()

        # Check availability
        if event.spots_left <= 0:
             return Response({'error': 'Evento agotado'}, status=status.HTTP_400_BAD_REQUEST)

        # Create ticket
        ticket = Ticket.objects.create(user=request.user, event=event)

        return Response({
            'status': 'registered',
            'ticket_id': ticket.id
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_tickets(self, request):
        tickets = Ticket.objects.filter(user=request.user).order_by('-purchase_date')
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)
