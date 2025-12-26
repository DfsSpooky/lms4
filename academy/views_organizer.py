from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from .models import Event, Ticket, Profile

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

    def form_valid(self, form):
        # ASSIGNMENT: Automatically set the organizer to the current user
        form.instance.organizer = self.request.user
        messages.success(self.request, "Evento creado exitosamente.")
        return super().form_valid(form)

class OrganizerEventUpdateView(OrganizerRequiredMixin, UpdateView):
    model = Event
    template_name = 'academy/organizer/event_form.html'
    fields = ['title', 'description', 'start_date', 'end_date', 'location', 'capacity', 'price', 'image', 'is_active']
    success_url = reverse_lazy('academy:organizer_dashboard')

    def get_queryset(self):
        # ISOLATION: Ensure user can only edit their own events
        return Event.objects.filter(organizer=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Evento actualizado exitosamente.")
        return super().form_valid(form)

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
