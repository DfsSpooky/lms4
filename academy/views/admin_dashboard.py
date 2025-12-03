from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from django.urls import reverse_lazy
from ..models import *
from ..forms_admin import *
from ..forms import UserUpdateForm, ProfileUpdateForm

# --- NOTIFICATIONS API ---
@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})

    return redirect(notification.link if notification.link else 'academy:dashboard')

@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'academy:dashboard'))

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, generic.TemplateView):
    template_name = 'academy/admin_dashboard.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['pending_enrollments'] = Enrollment.objects.filter(status='review').select_related('user', 'course')
        ctx['history_enrollments'] = Enrollment.objects.filter(status__in=['approved', 'rejected']).select_related('user', 'course').order_by('-enrolled_at')[:50]
        ctx['pending_installments'] = Installment.objects.filter(status='review').select_related('enrollment__user', 'enrollment__course')
        ctx['users'] = User.objects.select_related('profile').all().order_by('-date_joined')
        ctx['all_courses'] = Course.objects.select_related('instructor', 'category').annotate(
            student_count=Count('enrollments', filter=Q(enrollments__status='approved'))
        ).order_by('-created_at')
        ctx['hero_slides'] = HeroSlide.objects.all().order_by('order')
        ctx['categories'] = Category.objects.all().order_by('name')
        ctx['certifications'] = CertificationCard.objects.all().order_by('order')
        ctx['announcements'] = AnnouncementCard.objects.all().order_by('order')
        ctx['institutions'] = Institution.objects.all()
        ctx['payment_methods'] = PaymentMethod.objects.all()
        ctx['top_banners'] = TopBanner.objects.all().order_by('-created_at')
        ctx['site_config'] = SiteConfiguration.get_solo()
        ctx['site_config_form'] = SiteConfigurationForm(instance=ctx['site_config'])
        
        # CONTEXTOS AÑADIDOS PARA EVENTOS Y EMPRESAS
        ctx['events'] = Event.objects.all().order_by('date')
        ctx['service_requests'] = ServiceRequest.objects.filter(is_handled=False).order_by('-created_at')
        
        return ctx

    def post(self, request, *args, **kwargs):
        if 'site_config_update' in request.POST:
            config = SiteConfiguration.get_solo()
            form = SiteConfigurationForm(request.POST, request.FILES, instance=config)
            if form.is_valid():
                form.save()
                messages.success(request, "Configuración del sitio actualizada.")
            else:
                messages.error(request, "Error al actualizar configuración.")
            return redirect('academy:admin_dashboard')

        if 'enrollment_id' in request.POST:
            enrollment = get_object_or_404(Enrollment, id=request.POST.get('enrollment_id'))
            action = request.POST.get('action')
            if action == 'approve':
                enrollment.status = 'approved'
                enrollment.save()
                if enrollment.selected_payment_plan == 'monthly':
                    enrollment.generate_installments()
                    Installment.objects.filter(enrollment=enrollment, installment_number=1).update(
                        status='approved',
                        paid_at=timezone.now()
                    )
                messages.success(request, f"Inscripción de {enrollment.user.username} aprobada.")
            elif action == 'reject':
                enrollment.status = 'rejected'
                enrollment.save()
                messages.warning(request, f"Inscripción de {enrollment.user.username} rechazada.")

        elif 'installment_id' in request.POST:
            inst = get_object_or_404(Installment, id=request.POST.get('installment_id'))
            action = request.POST.get('action')
            if action == 'approve':
                inst.status = 'approved'
                inst.paid_at = timezone.now()
                inst.save()
                inst.enrollment.installments_paid += 1
                inst.enrollment.save()
                messages.success(request, f"Cuota #{inst.installment_number} de {inst.enrollment.user.username} aprobada.")
            elif action == 'reject':
                inst.status = 'rejected'
                inst.feedback = "Voucher rechazado."
                inst.save()
                messages.warning(request, f"Cuota #{inst.installment_number} rechazada.")

        elif 'user_id' in request.POST:
            user = get_object_or_404(User, id=request.POST.get('user_id'))
            action = request.POST.get('action')
            if action == 'promote_teacher':
                user.profile.role = 'teacher'
                user.profile.save()
                messages.success(request, f"{user.username} ahora es Profesor.")
            elif action == 'demote_student':
                user.profile.role = 'student'
                user.profile.save()
                messages.success(request, f"{user.username} ahora es Estudiante.")

        elif 'slide_id' in request.POST:
            slide = get_object_or_404(HeroSlide, id=request.POST.get('slide_id'))
            action = request.POST.get('action')
            if action == 'toggle_active':
                slide.is_active = not slide.is_active
                slide.save()
                status = "activado" if slide.is_active else "desactivado"
                messages.success(request, f"Slide '{slide.title}' {status}.")
            elif action == 'delete':
                slide.delete()
                messages.success(request, "Slide eliminado.")

        elif 'cert_id' in request.POST:
            cert = get_object_or_404(CertificationCard, id=request.POST.get('cert_id'))
            action = request.POST.get('action')
            if action == 'toggle_active':
                cert.is_active = not cert.is_active
                cert.save()
                messages.success(request, f"Certificación '{cert.title}' actualizada.")
            elif action == 'delete':
                cert.delete()
                messages.success(request, "Certificación eliminada.")

        elif 'announcement_id' in request.POST:
            ann = get_object_or_404(AnnouncementCard, id=request.POST.get('announcement_id'))
            action = request.POST.get('action')
            if action == 'toggle_active':
                ann.is_active = not ann.is_active
                ann.save()
                messages.success(request, f"Anuncio '{ann.title}' actualizado.")
            elif action == 'delete':
                ann.delete()
                messages.success(request, "Anuncio eliminado.")

        elif 'institution_id' in request.POST:
            inst = get_object_or_404(Institution, id=request.POST.get('institution_id'))
            action = request.POST.get('action')
            if action == 'delete':
                inst.delete()
                messages.success(request, "Institución eliminada.")

        elif 'payment_method_id' in request.POST:
            pm = get_object_or_404(PaymentMethod, id=request.POST.get('payment_method_id'))
            action = request.POST.get('action')
            if action == 'delete':
                pm.delete()
                messages.success(request, "Método de Pago eliminado.")

        elif 'category_id' in request.POST:
            cat = get_object_or_404(Category, id=request.POST.get('category_id'))
            action = request.POST.get('action')
            if action == 'delete':
                cat.delete()
                messages.success(request, "Categoría eliminada.")

        elif 'course_id' in request.POST:
            course = get_object_or_404(Course, id=request.POST.get('course_id'))
            action = request.POST.get('action')
            if action == 'delete':
                if course.enrollments.exists():
                    msg = f"No se puede eliminar '{course.title}' porque tiene {course.enrollments.count()} estudiantes inscritos."
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'status': 'error', 'message': msg}, status=400)
                    messages.error(request, msg)
                else:
                    course.delete()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'status': 'ok', 'message': 'Curso eliminado correctamente'})
                    messages.success(request, "Curso eliminado correctamente.")

        elif 'banner_id' in request.POST:
            banner = get_object_or_404(TopBanner, id=request.POST.get('banner_id'))
            action = request.POST.get('action')
            if action == 'toggle_active':
                if not banner.is_active:
                    TopBanner.objects.update(is_active=False)

                banner.is_active = not banner.is_active
                banner.save()
                status = "activado" if banner.is_active else "desactivado"
                messages.success(request, f"Banner '{banner.message}' {status}.")
            elif action == 'delete':
                banner.delete()
                messages.success(request, "Banner eliminado.")

        # LÓGICA AÑADIDA: ServiceRequest
        elif 'service_request_id' in request.POST:
            sr = get_object_or_404(ServiceRequest, id=request.POST.get('service_request_id'))
            action = request.POST.get('action')
            if action == 'mark_handled':
                sr.is_handled = True
                sr.save()
                messages.success(request, f"Solicitud de {sr.company_name} marcada como atendida.")
            elif action == 'delete':
                sr.delete()
                messages.success(request, "Solicitud eliminada.")
        
        # LÓGICA AÑADIDA: Eventos
        elif 'event_id' in request.POST:
            event = get_object_or_404(Event, id=request.POST.get('event_id'))
            action = request.POST.get('action')
            if action == 'delete':
                event.delete()
                messages.success(request, f"Evento '{event.title}' eliminado.")

        return redirect('academy:admin_dashboard')

class AdminUserCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = User
    form_class = AdminUserCreationForm
    template_name = 'academy/admin_user_form.html'
    success_url = reverse_lazy('academy:admin_dashboard')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Usuario creado exitosamente.")
        return super().form_valid(form)

class HeroSlideCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = HeroSlide
    form_class = HeroSlideForm
    template_name = 'academy/hero_slide_form.html'
    success_url = reverse_lazy('academy:admin_dashboard')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Slide creado exitosamente.")
        return super().form_valid(form)

class HeroSlideUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = HeroSlide
    form_class = HeroSlideForm
    template_name = 'academy/hero_slide_form.html'
    success_url = reverse_lazy('academy:admin_dashboard')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Slide actualizado exitosamente.")
        return super().form_valid(form)

class CategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'academy/category_form.html'
    success_url = reverse_lazy('academy:admin_dashboard')

    def test_func(self): return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Categoría creada exitosamente.")
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'academy/category_form.html'
    success_url = reverse_lazy('academy:admin_dashboard')

    def test_func(self): return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Categoría actualizada exitosamente.")
        return super().form_valid(form)

class CertificationCardCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = CertificationCard
    form_class = CertificationCardForm
    template_name = 'academy/certification_card_form.html'
    success_url = reverse_lazy('academy:admin_dashboard')

    def test_func(self): return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Certificación creada exitosamente.")
        return super().form_valid(form)

class CertificationCardUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = CertificationCard
    form_class = CertificationCardForm
    template_name = 'academy/certification_card_form.html'
    success_url = reverse_lazy('academy:admin_dashboard')

    def test_func(self): return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Certificación actualizada exitosamente.")
        return super().form_valid(form)

class AnnouncementCardCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = AnnouncementCard
    form_class = AnnouncementCardForm
    template_name = 'academy/announcement_form.html'
    success_url = reverse_lazy('academy:admin_dashboard')

    def test_func(self): return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Anuncio creado exitosamente.")
        return super().form_valid(form)

class AnnouncementCardUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = AnnouncementCard
    form_class = AnnouncementCardForm
    template_name = 'academy/announcement_form.html'
    success_url = reverse_lazy('academy:admin_dashboard')

    def test_func(self): return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Anuncio actualizado exitosamente.")
        return super().form_valid(form)

class InstitutionCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Institution
    form_class = InstitutionForm
    template_name = 'academy/institution_form.html'
    success_url = reverse_lazy('academy:admin_dashboard')

    def test_func(self): return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Institución creada exitosamente.")
        return super().form_valid(form)

class InstitutionUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Institution
    form_class = InstitutionForm
    template_name = 'academy/institution_form.html'
    success_url = reverse_lazy('academy:admin_dashboard')

    def test_func(self): return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Institución actualizada exitosamente.")
        return super().form_valid(form)

class PaymentMethodCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = PaymentMethod
    form_class = PaymentMethodForm
    template_name = 'academy/payment_method_form.html'
    success_url = reverse_lazy('academy:admin_dashboard')

    def test_func(self): return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Método de Pago creado exitosamente.")
        return super().form_valid(form)

class PaymentMethodUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = PaymentMethod
    form_class = PaymentMethodForm
    template_name = 'academy/payment_method_form.html'
    success_url = reverse_lazy('academy:admin_dashboard')

    def test_func(self): return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Método de Pago actualizado exitosamente.")
        return super().form_valid(form)

class TopBannerCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = TopBanner
    form_class = TopBannerForm
    template_name = 'academy/top_banner_form.html'
    success_url = reverse_lazy('academy:admin_dashboard')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Banner creado exitosamente.")
        return super().form_valid(form)

class TopBannerUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = TopBanner
    form_class = TopBannerForm
    template_name = 'academy/top_banner_form.html'
    success_url = reverse_lazy('academy:admin_dashboard')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Banner actualizado exitosamente.")
        return super().form_valid(form)

class AdminUserUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    template_name = 'academy/admin_user_edit.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        u_form = UserUpdateForm(instance=user)
        if not hasattr(user, 'profile'):
             Profile.objects.create(user=user)
        p_form = ProfileUpdateForm(instance=user.profile)

        return render(request, self.template_name, {
            'target_user': user,
            'u_form': u_form,
            'p_form': p_form
        })

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        u_form = UserUpdateForm(request.POST, instance=user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Usuario {user.username} actualizado correctamente.")
            return redirect('academy:admin_dashboard')

        return render(request, self.template_name, {
            'target_user': user,
            'u_form': u_form,
            'p_form': p_form
        })

class AdminUserDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = User
    template_name = 'academy/admin_user_confirm_delete.html'
    success_url = reverse_lazy('academy:admin_dashboard')

    def test_func(self):
        return self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            messages.error(request, "No puedes eliminar tu propio usuario.")
            return redirect('academy:admin_dashboard')
        messages.success(request, f"Usuario {user.username} eliminado.")
        return super().delete(request, *args, **kwargs)

# CLASES AÑADIDAS PARA GESTIÓN DE EVENTOS
class EventCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Event
    form_class = EventForm
    template_name = 'academy/event_form.html'
    success_url = reverse_lazy('academy:admin_dashboard')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Evento creado exitosamente.")
        return super().form_valid(form)

class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'academy/event_form.html'
    success_url = reverse_lazy('academy:admin_dashboard')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Evento actualizado exitosamente.")
        return super().form_valid(form)