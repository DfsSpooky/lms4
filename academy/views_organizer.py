from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from .models import Event, Ticket, Profile
from .forms import TicketTierFormSet

# --- MIXINS ---

class OrganizerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Ensure the user is logged in and has the 'organizer' role.
    """
    def test_func(self):
        try:
            return self.request.user.profile.role == 'organizer'
        except Profile.DoesNotExist:
            return False

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permiso para acceder a esta área.")
        return redirect('academy:dashboard')

# --- VIEWS ---

class OrganizerDashboardView(OrganizerRequiredMixin, ListView):
    model = Event
    template_name = 'academy/organizer/dashboard.html'
    context_object_name = 'events'

    def get_queryset(self):
        # ISOLATION: Only show events created by the current user
        return Event.objects.filter(organizer=self.request.user).order_by('-start_date')

class OrganizerEventCreateView(OrganizerRequiredMixin, CreateView):
    model = Event
    template_name = 'academy/organizer/event_form.html'
    fields = ['title', 'description', 'start_date', 'end_date', 'location', 'capacity', 'price', 'image', 'is_active']
    success_url = reverse_lazy('academy:organizer_dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['tiers'] = TicketTierFormSet(self.request.POST)
        else:
            context['tiers'] = TicketTierFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        tiers = context['tiers']
        form.instance.organizer = self.request.user

        if form.is_valid() and tiers.is_valid():
            self.object = form.save()
            tiers.instance = self.object
            tiers.save()
            messages.success(self.request, "Evento creado exitosamente.")
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class OrganizerEventUpdateView(OrganizerRequiredMixin, UpdateView):
    model = Event
    template_name = 'academy/organizer/event_form.html'
    fields = ['title', 'description', 'start_date', 'end_date', 'location', 'capacity', 'price', 'image', 'is_active']
    success_url = reverse_lazy('academy:organizer_dashboard')

    def get_queryset(self):
        # ISOLATION: Ensure user can only edit their own events
        return Event.objects.filter(organizer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['tiers'] = TicketTierFormSet(self.request.POST, instance=self.object)
        else:
            context['tiers'] = TicketTierFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        tiers = context['tiers']

        if form.is_valid() and tiers.is_valid():
            self.object = form.save()
            tiers.save()
            messages.success(self.request, "Evento actualizado exitosamente.")
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class OrganizerEventDetailView(OrganizerRequiredMixin, DetailView):
    model = Event
    template_name = 'academy/organizer/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        # ISOLATION: Ensure user can only view their own event details
        return Event.objects.filter(organizer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add tickets/attendees to context
        context['tickets'] = self.object.tickets.all().select_related('user', 'user__profile')
        context['tickets_sold'] = self.object.tickets.count()
        context['revenue'] = sum(t.event.price for t in context['tickets']) # Simplified revenue calc
        return context

class OrganizerTicketCheckInView(OrganizerRequiredMixin, View):
    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id, organizer=request.user)
        return render(request, 'academy/organizer/checkin.html', {'event': event})

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id, organizer=request.user)
        ticket_id = request.POST.get('ticket_id')

        try:
            ticket = Ticket.objects.get(id=ticket_id, event=event)
        except (Ticket.DoesNotExist, ValueError):
            return JsonResponse({'status': 'error', 'message': 'Ticket no encontrado o no válido.'})

        if ticket.status != 'approved':
            return JsonResponse({
                'status': 'error',
                'message': f'Ticket INVÁLIDO. Estado: {ticket.get_status_display()}'
            })

        if ticket.is_used:
            return JsonResponse({
                'status': 'warning',
                'message': f'¡ALERTA! Este ticket YA FUE USADO anteriormente.',
                'user': ticket.user.get_full_name()
            })

        # Valid Check-in
        ticket.is_used = True
        ticket.save() # updated_at updates automatically

        return JsonResponse({
            'status': 'success',
            'message': 'Check-in Exitoso',
            'user': ticket.user.get_full_name() or ticket.user.username,
            'type': 'General' # Placeholder for ticket type
        })
