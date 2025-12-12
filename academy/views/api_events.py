from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ..models import Event, Ticket, TicketTier
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
        tier_id = request.data.get('tier_id')

        tier = None
        price = event.price

        if tier_id:
            try:
                tier = TicketTier.objects.get(id=tier_id, event=event)
                if tier.remaining <= 0:
                    return Response({'error': 'Tipo de entrada agotado'}, status=status.HTTP_400_BAD_REQUEST)
                price = tier.price
            except TicketTier.DoesNotExist:
                return Response({'error': 'Tipo de entrada inválido'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Check availability general
            if event.spots_left <= 0:
                 return Response({'error': 'Evento agotado'}, status=status.HTTP_400_BAD_REQUEST)

        # Determine initial status
        initial_status = 'approved' if price == 0 else 'pending'

        # Create ticket
        ticket = Ticket.objects.create(user=request.user, event=event, status=initial_status, tier=tier)

        return Response({
            'status': ticket.status,
            'ticket_id': ticket.id,
            'message': 'Registro exitoso' if ticket.status == 'approved' else 'Reserva creada. Sube tu comprobante.'
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='upload-voucher')
    def upload_voucher(self, request, pk=None):
        # NOTE: pk here refers to EVENT pk because this is EventViewSet,
        # BUT logically we upload for a TICKET.
        # Standard DRF pattern: nested route or specific TicketViewSet.
        # Since we don't have TicketViewSet, we can accept ticket_id in body OR
        # create a standalone action that finds the latest pending ticket for this event.

        event = self.get_object()
        ticket_id = request.data.get('ticket_id')

        if ticket_id:
            ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user, event=event)
        else:
            # Fallback: Find latest pending ticket
            ticket = Ticket.objects.filter(user=request.user, event=event, status__in=['pending', 'rejected']).order_by('-purchase_date').first()

        if not ticket:
            return Response({'error': 'No se encontró un ticket pendiente para este evento'}, status=status.HTTP_404_NOT_FOUND)

        if 'file' not in request.FILES:
             return Response({'error': 'No se envió ningún archivo'}, status=status.HTTP_400_BAD_REQUEST)

        ticket.voucher_image = request.FILES['file']
        ticket.status = 'review'
        ticket.save()

        return Response({'status': 'uploaded', 'ticket_status': 'review'})

    @action(detail=False, methods=['get'])
    def my_tickets(self, request):
        tickets = Ticket.objects.filter(user=request.user).order_by('-purchase_date')
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)
