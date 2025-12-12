from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from ..models import Event, Ticket, ServiceRequest, TicketTier
from django.utils import timezone
from django.http import HttpResponseBadRequest
from ..forms import TicketVoucherForm

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
    ordering = ['start_date']

    def get_queryset(self):
        return Event.objects.filter(is_active=True, start_date__gte=timezone.now()).order_by('start_date')

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
        tier_id = request.POST.get('tier_id')

        tier = None
        price = event.price

        # Check specific tier availability if selected
        if tier_id:
            tier = get_object_or_404(TicketTier, id=tier_id, event=event)
            if tier.remaining <= 0:
                messages.error(request, "Lo sentimos, ese tipo de entrada está agotado.")
                return redirect('academy:event_detail', slug=event.slug)
            price = tier.price
        else:
            # General availability check
            if event.spots_left <= 0:
                messages.error(request, "Lo sentimos, este evento ya no tiene cupos disponibles.")
                return redirect('academy:event_detail', slug=event.slug)

        # Set status based on price
        initial_status = 'approved' if price == 0 else 'pending'

        # Create ticket
        ticket = Ticket.objects.create(user=request.user, event=event, status=initial_status, tier=tier)

        if ticket.status == 'approved':
            messages.success(request, "¡Registro exitoso! Aquí está tu entrada.")
            return redirect('academy:ticket_detail', ticket_id=ticket.id)
        else:
            messages.info(request, "Reserva creada. Por favor sube tu comprobante de pago.")
            return redirect('academy:ticket_payment', ticket_id=ticket.id)

class TicketPaymentView(LoginRequiredMixin, View):
    def get(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
        if ticket.status == 'approved':
             messages.info(request, "Este ticket ya está pagado.")
             return redirect('academy:ticket_detail', ticket_id=ticket.id)

        form = TicketVoucherForm()
        return render(request, 'academy/ticket_payment.html', {'ticket': ticket, 'form': form})

    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
        if ticket.status == 'approved':
             return redirect('academy:ticket_detail', ticket_id=ticket.id)

        form = TicketVoucherForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            t = form.save(commit=False)
            t.status = 'review'
            t.save()
            messages.success(request, "Comprobante subido. Tu ticket está en revisión.")
            return redirect('academy:ticket_detail', ticket_id=ticket.id)

        messages.error(request, "Error al subir el comprobante. Por favor intenta de nuevo.")
        return render(request, 'academy/ticket_payment.html', {'ticket': ticket, 'form': form})

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
