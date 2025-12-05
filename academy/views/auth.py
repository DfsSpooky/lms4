from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.views import generic
from django.contrib import messages
from django.utils.decorators import method_decorator
from ..forms import SignUpForm, UserUpdateForm, ProfileUpdateForm
from ..models import User, Enrollment
from ..decorators import rate_limit

# --- LOGIN MODERNO ---
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    @method_decorator(rate_limit(limit=5, period=300)) # 5 attempts per 5 minutes
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        # Loguear al usuario
        login(self.request, form.get_user())

        # Respuesta JSON para React
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'redirect_url': self.get_success_url()
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        # Respuesta JSON de error para React
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': {'non_field_errors': ['Usuario o contraseña incorrectos.']}
            }, status=400)
        return super().form_invalid(form)

# --- SIGNUP VIEW ---
class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        # Guardar y loguear si todo está bien
        user = form.save()
        login(self.request, user)

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Cuenta creada',
                'redirect_url': reverse('academy:dashboard')
            })
        return redirect('academy:dashboard')

    def form_invalid(self, form):
        errors = dict(form.errors)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': errors
            }, status=400)
        return super().form_invalid(form)

@login_required
def profile_edit(request):
    # Validar si el perfil está incompleto para mostrar advertencia
    profile = request.user.profile
    is_organizer = profile.role == 'organizer'

    # Check for missing fields based on role
    if not is_organizer:
        if not profile.dni or not profile.phone_number:
            messages.warning(request, "Por favor completa tu perfil para continuar (DNI y Celular son obligatorios).")
    else:
        if not profile.phone_number: # DNI is not required for organizers in UI
            messages.warning(request, "Por favor completa tu perfil (Celular).")

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        # If organizer, we might need to bypass DNI validation if it's strictly required by the form
        if is_organizer:
            # We filled it with dummy data in template, but form validation runs on cleaned data.
            # If DNI is required in form definition, the hidden input in template should handle it.
            pass

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Perfil actualizado correctamente")
            # Si ya completó, se queda aquí o puede ir al dashboard
            return redirect('academy:profile_edit')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    if is_organizer:
        u_form.fields['first_name'].label = "Nombre de la Organización"
        # Since we use manual rendering in template with conditional logic,
        # we don't strictly need to modify widget attributes here, but it's good practice.

    enrollments = Enrollment.objects.filter(user=request.user).select_related('course').order_by('-enrolled_at')

    return render(request, 'academy/profile_edit.html', {
        'u_form': u_form,
        'p_form': p_form,
        'enrollments': enrollments
    })

class PublicProfileView(generic.DetailView):
    model = User
    template_name = 'academy/public_profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        completed_enrollments = Enrollment.objects.filter(user=user, status='approved', is_completed=True).select_related('course')
        context['completed_courses'] = completed_enrollments
        context['certificates_count'] = completed_enrollments.count()
        return context
