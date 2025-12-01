from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.contrib import messages
from ..models import Enrollment, Installment, Course
from ..forms import EnrollmentDataForm, VoucherUploadForm, InstallmentVoucherForm

@login_required
def enroll_course_step1(request, slug):
    course = get_object_or_404(Course, slug=slug)

    existing_enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    if existing_enrollment:
        if existing_enrollment.status == 'approved':
            return redirect('academy:dashboard')
        elif existing_enrollment.status in ['pending', 'review']:
            return redirect('academy:payment_gateway', pk=existing_enrollment.id)

    profile = request.user.profile
    initial_data = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'dni': profile.dni,
        'address': profile.address,
        'academic_profile': profile.academic_profile
    }

    if request.method == 'POST':
        form = EnrollmentDataForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.save()

            profile.dni = form.cleaned_data['dni']
            profile.address = form.cleaned_data['address']
            profile.academic_profile = form.cleaned_data['academic_profile']
            profile.save()

            enrollment = Enrollment.objects.create(
                user=request.user,
                course=course,
                status='pending'
            )
            return redirect('academy:payment_gateway', pk=enrollment.id)
    else:
        form = EnrollmentDataForm(initial=initial_data)

    return render(request, 'academy/enroll_step1.html', {'course': course, 'form': form})

@login_required
def payment_gateway(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk, user=request.user)

    if enrollment.status == 'approved':
        messages.success(request, "¡Ya estás inscrito en este curso!")
        return redirect('academy:dashboard')

    if request.method == 'POST':
        form = VoucherUploadForm(request.POST, request.FILES, instance=enrollment)
        if form.is_valid():
            enrollment.status = 'review'
            plan = request.POST.get('payment_plan')
            if plan in ['full', 'monthly']:
                enrollment.selected_payment_plan = plan

            enrollment.save()
            messages.success(request, "Tu constancia ha sido enviada. Un administrador la revisará pronto.")
            return redirect('academy:dashboard')
    else:
        form = VoucherUploadForm(instance=enrollment)

    payment_methods = enrollment.course.allowed_payment_methods.all()

    return render(request, 'academy/payment_gateway.html', {
        'enrollment': enrollment,
        'course': enrollment.course,
        'form': form,
        'payment_methods': payment_methods
    })

class StudentPaymentsView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'academy/student_payments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        enrollments = Enrollment.objects.filter(user=user, selected_payment_plan='monthly', status__in=['approved', 'pending']).select_related('course')

        installments_data = []

        for enrollment in enrollments:
            course = enrollment.course
            if not course.duration_months or not course.monthly_price:
                continue

            if not enrollment.installments.exists():
                enrollment.generate_installments()

            created_installments = list(enrollment.installments.all().order_by('installment_number'))

            installments_data.append({
                'enrollment': enrollment,
                'course': course,
                'installments': created_installments
            })

        context['payments_data'] = installments_data
        return context

@login_required
def upload_installment_voucher(request, installment_id):
    installment = get_object_or_404(Installment, id=installment_id, enrollment__user=request.user)

    if request.method == 'POST':
        form = InstallmentVoucherForm(request.POST, request.FILES, instance=installment)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.status = 'review'
            inst.save()
            messages.success(request, "Voucher enviado para revisión.")
            return redirect('academy:student_payments')

    return redirect('academy:student_payments')
