from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from ..models import Event, Ticket, ServiceRequest
from django.utils import timezone
from django.http import HttpResponseBadRequest

class EnterpriseLandingView(TemplateView):
    template_name = 'academy/enterprise.html'

    def post(self, request, *args, **kwargs):
        company_name = request.POST.get('company_name')
        contact_name = request.POST.get('contact_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        if company_name and contact_name and email:
            ServiceRequest.objects.create(
                company_name=company_name,
                contact_name=contact_name,
                email=email,
                phone=phone,
                message=message
            )
            messages.success(request, "Su solicitud ha sido enviada. Nos pondremos en contacto pronto.")
            return redirect('academy:enterprise_services')
        else:
            messages.error(request, "Por favor complete todos los campos requeridos.")
            return redirect('academy:enterprise_services')

class EventListView(ListView):
    model = Event
    template_name = 'academy/event_list.html'
    context_object_name = 'events'
    ordering = ['date']

    def get_queryset(self):
        return Event.objects.filter(is_active=True, date__gte=timezone.now()).order_by('date')

class EventDetailView(DetailView):
    model = Event
    template_name = 'academy/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_ticket'] = Ticket.objects.filter(user=self.request.user, event=self.object).first()
        return context

class EventRegistrationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        # Check availability
        if event.spots_left <= 0:
            messages.error(request, "Lo sentimos, este evento ya no tiene cupos disponibles.")
            return redirect('academy:event_detail', slug=event.slug)

        # Check existing ticket
        existing_ticket = Ticket.objects.filter(user=request.user, event=event).first()
        if existing_ticket:
            if existing_ticket.status == 'pending':
                return redirect('academy:event_payment', ticket_id=existing_ticket.id)
            messages.info(request, "Ya estás registrado en este evento.")
            return redirect('academy:event_detail', slug=event.slug)

        # Create ticket
        if event.price > 0:
            ticket = Ticket.objects.create(user=request.user, event=event, status='pending')
            return redirect('academy:event_payment', ticket_id=ticket.id)
        else:
            ticket = Ticket.objects.create(user=request.user, event=event, status='approved')
            messages.success(request, "¡Registro exitoso! Aquí está tu entrada.")
            return redirect('academy:ticket_detail', ticket_id=ticket.id)


class EventPaymentView(LoginRequiredMixin, View):
    def get(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

        if ticket.status == 'approved':
             return redirect('academy:ticket_detail', ticket_id=ticket.id)

        # Assuming we can use the same payment methods as courses or default ones
        # For simplicity, we might just show bank info or use existing PaymentMethods
        # Let's fetch all payment methods for now, or if events had specific ones we would use that.
        # Since Event doesn't have m2m to PaymentMethod, let's just show all available.
        from ..models import PaymentMethod
        payment_methods = PaymentMethod.objects.all()

        return render(request, 'academy/event_payment.html', {
            'ticket': ticket,
            'event': ticket.event,
            'payment_methods': payment_methods
        })

    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

        voucher = request.FILES.get('voucher_image')
        if voucher:
            ticket.voucher_image = voucher
            ticket.status = 'review'
            ticket.save()
            messages.success(request, "Tu constancia ha sido enviada. Un administrador la revisará pronto.")
            return redirect('academy:event_detail', slug=ticket.event.slug)
        else:
            messages.error(request, "Por favor sube una imagen del voucher.")
            return redirect('academy:event_payment', ticket_id=ticket.id)

class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'academy/ticket_detail.html'
    context_object_name = 'ticket'
    pk_url_kwarg = 'ticket_id'

    def get_queryset(self):
        # Allow users to see their own tickets, or staff to see any ticket
        if self.request.user.is_staff:
            return Ticket.objects.all()
        return Ticket.objects.filter(user=self.request.user)
