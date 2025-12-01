from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.utils import timezone
from django.db.models import Prefetch, Q, Count
from django.contrib import messages
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse

from .forms import SignUpForm, UserUpdateForm, ProfileUpdateForm, EnrollmentDataForm, VoucherUploadForm, ModuleForm, LessonForm, CourseForm, LessonCommentForm, AssignmentSubmissionForm, AssignmentGradingForm, QuizForm, QuestionForm, InstallmentVoucherForm
from .forms_admin import AdminUserCreationForm, HeroSlideForm, CategoryForm, CertificationCardForm, AnnouncementCardForm, InstitutionForm, PaymentMethodForm, TopBannerForm, SiteConfigurationForm
from .models import *
import json
from .serializers import *
from django.contrib.auth.mixins import UserPassesTestMixin

# --- ENDPOINT API ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    def get_serializer_class(self):
        if self.action == 'retrieve': return CourseDetailSerializer
        return CourseListSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def enroll(self, request, pk=None):
        # API simple enrollment (legacy)
        course = self.get_object()
        Enrollment.objects.get_or_create(user=request.user, course=course)
        return Response({'status': 'inscripto'})

class ProgressViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    @action(detail=False, methods=['post'], url_path='lesson/(?P<lesson_id>[^/.]+)/complete')
    def complete_lesson(self, request, lesson_id=None):
        lesson = Lesson.objects.get(pk=lesson_id)
        if not Enrollment.objects.filter(user=request.user, course=lesson.module.course, status='approved').exists():
             return Response({'error': 'Acceso denegado'}, status=403)
        LessonProgress.objects.get_or_create(user=request.user, lesson=lesson, defaults={'is_completed': True})
        LessonProgress.objects.filter(user=request.user, lesson=lesson).update(is_completed=True)
        return Response({'status': 'ok'})

    @action(detail=False, methods=['post'], url_path='quiz/(?P<quiz_id>[^/.]+)/submit')
    def submit_quiz(self, request, quiz_id=None):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        # Check enrollment approved
        if not Enrollment.objects.filter(user=request.user, course=quiz.module.course, status='approved').exists():
             return Response({'error': 'Acceso denegado'}, status=403)

        # data format: {'question_id': value}
        # value can be: answer_id (int), list of answer_ids (list), or text (str)
        data = request.data.get('answers', {}) 

        # Validate Time Limit
        if quiz.duration > 0:
            import time
            session_start_key = f'quiz_{quiz.id}_start_time'
            start_time = request.session.get(session_start_key)
            if start_time:
                elapsed = time.time() - start_time
                # Allow 60 seconds grace period
                if elapsed > (quiz.duration * 60) + 60:
                     # Late submission? We can mark it as failed or just warn.
                     # For now, we will proceed but you might want to penalize.
                     pass

            # Clean up session
            if session_start_key in request.session:
                del request.session[session_start_key]

        # Create submission object first
        submission = QuizSubmission.objects.create(
            user=request.user,
            quiz=quiz,
            score=0,
            passed=False
        )

        total_points = 0
        earned_points = 0
        needs_grading = False

        # Determine which questions to grade
        questions = []
        if quiz.randomize_questions:
            session_key = f'quiz_{quiz.id}_questions'
            question_ids = request.session.get(session_key)
            if question_ids:
                questions = list(Question.objects.filter(id__in=question_ids))
                # Cleanup
                del request.session[session_key]
            else:
                 # Fallback: Grade based on submitted keys if valid? Or all?
                 # If session expired, this is tricky. We'll fallback to grading what was sent.
                 # Security risk: User sends only questions they know.
                 # Better: Load all questions? No, we don't want to grade questions they didn't see.
                 # Compromise: Load questions from keys in 'data' that belong to this quiz.
                 submitted_ids = [int(k) for k in data.keys() if k.isdigit()]
                 questions = list(Question.objects.filter(id__in=submitted_ids, quiz=quiz))
        else:
            questions = list(quiz.questions.all())

        if not questions: return Response({'error': 'Examen vacío o error de sesión'}, status=400)

        for question in questions:
            total_points += question.points
            answer_data = data.get(str(question.id))

            student_answer = StudentAnswer.objects.create(
                submission=submission,
                question=question
            )

            if not answer_data:
                continue

            q_points = 0
            is_correct = False

            if question.question_type == 'single_choice' or question.question_type == 'true_false':
                try:
                    ans_id = int(answer_data)
                    answer = Answer.objects.get(id=ans_id, question=question)
                    student_answer.selected_answers.add(answer)
                    if answer.is_correct:
                        q_points = question.points
                        is_correct = True
                except (ValueError, Answer.DoesNotExist):
                    pass

            elif question.question_type == 'multiple_choice':
                # answer_data should be a list of IDs
                if isinstance(answer_data, list):
                    correct_answers = set(question.answers.filter(is_correct=True).values_list('id', flat=True))
                    selected_ids = set()
                    for aid in answer_data:
                        try:
                            a_obj = Answer.objects.get(id=int(aid), question=question)
                            student_answer.selected_answers.add(a_obj)
                            selected_ids.add(a_obj.id)
                        except: pass

                    if selected_ids == correct_answers:
                        q_points = question.points
                        is_correct = True

            elif question.question_type == 'short_answer':
                text_input = str(answer_data).strip().lower()
                student_answer.text_answer = str(answer_data)

                # Check against possible correct answers
                possible_answers = question.answers.all()
                if possible_answers.exists():
                    # Auto-grade if there are defined answers
                    match = False
                    for ans in possible_answers:
                        if ans.text.strip().lower() == text_input:
                            match = True
                            break

                    if match:
                        q_points = question.points
                        is_correct = True
                    else:
                        is_correct = False
                else:
                    # No defined answers, manual grading
                    is_correct = None
                    needs_grading = True

            elif question.question_type == 'ordering':
                # answer_data expected: list of answer_ids in submitted order
                submitted_order_ids = [int(x) for x in answer_data if x] if isinstance(answer_data, list) else []
                correct_order_ids = list(question.answers.order_by('order').values_list('id', flat=True))

                # Save the submitted order as text for reference
                student_answer.text_answer = json.dumps(submitted_order_ids)

                matches = 0
                if len(submitted_order_ids) == len(correct_order_ids):
                    for idx, val in enumerate(submitted_order_ids):
                        if val == correct_order_ids[idx]:
                            matches += 1

                if matches == len(correct_order_ids) and len(correct_order_ids) > 0:
                        q_points = question.points
                        is_correct = True
                elif len(correct_order_ids) > 0:
                    q_points = (matches / len(correct_order_ids)) * question.points
                    is_correct = False

            elif question.question_type == 'matching':
                # answer_data expected: dict { answer_id: matched_text }
                pairs = answer_data if isinstance(answer_data, dict) else {}
                student_answer.text_answer = json.dumps(pairs)

                correct_pairs = 0
                total_pairs = question.answers.count()

                for ans in question.answers.all():
                    submitted_val = pairs.get(str(ans.id))
                    if submitted_val and submitted_val.strip() == ans.match_text.strip():
                        correct_pairs += 1

                if total_pairs > 0:
                    q_points = (correct_pairs / total_pairs) * question.points
                    is_correct = (correct_pairs == total_pairs)

            student_answer.is_correct = is_correct
            student_answer.points_awarded = q_points
            student_answer.save()
            earned_points += q_points

        # Calculate final score
        # Note: If needs_grading is True, the score is provisional
        final_score = (earned_points / total_points) * 100 if total_points > 0 else 0
        
        submission.score = final_score
        submission.passed = final_score >= quiz.pass_mark
        submission.save()

        # Update best score logic?
        # Usually we keep history. But if we want to track "best" for progress:
        # We might want to keep the highest score submission as the "official" one for certificate.
        # But here we just return the result of THIS attempt.

        return Response({
            'score': final_score,
            'passed': submission.passed,
            'needs_grading': needs_grading,
            'submission_id': submission.id
        })

# --- VISTAS STANDARD ---

class CourseListView(generic.ListView):
    model = Course
    template_name = 'academy/course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        # --- CAMBIO AQUÍ: Optimización de consultas ---
        # Usamos select_related para claves foráneas (categoría, instructor, perfil)
        # Usamos prefetch_related para relaciones inversas (reviews)
        queryset = Course.objects.select_related(
            'category',
            'instructor__profile'
        ).prefetch_related(
            'reviews'
        ).all()

        # 1. Search Query
        query = self.request.GET.get('q')
        if query: queryset = queryset.filter(title__icontains=query)

        # 2. Category Filter
        cat_slug = self.request.GET.get('category')
        if cat_slug: queryset = queryset.filter(category__slug=cat_slug)

        # 3. Level Filter (Multiple selection)
        levels = self.request.GET.getlist('level')
        if levels:
            queryset = queryset.filter(level__in=levels)

        # 4. Price Filter
        price_filter = self.request.GET.get('price')
        if price_filter == 'free':
            queryset = queryset.filter(price=0)
        elif price_filter == 'paid':
            queryset = queryset.filter(price__gt=0)

        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()

        # Pass current filters to context to maintain state in checkboxes
        ctx['selected_levels'] = self.request.GET.getlist('level')
        ctx['selected_price'] = self.request.GET.get('price')
        ctx['selected_category'] = self.request.GET.get('category')
        
        # --- DATOS DINÁMICOS PARA EL HOME (CMS) ---
        # Recuperamos solo los slides y certificaciones activos, ordenados por 'order'
        ctx['hero_slides'] = HeroSlide.objects.filter(is_active=True).order_by('order')
        ctx['certifications'] = CertificationCard.objects.filter(is_active=True).order_by('order')
        
        # Creamos un rango numérico para los indicadores (dots) del slider en AlpineJS
        # Ejemplo: si hay 3 slides, esto genera [0, 1, 2]
        ctx['slide_range'] = range(ctx['hero_slides'].count())

        ctx['announcements'] = AnnouncementCard.objects.filter(is_active=True).order_by('order')
        
        return ctx

class CourseCatalogView(CourseListView):
    template_name = 'academy/course_catalog.html'

    def get_context_data(self, **kwargs):
        # Override to remove Hero Slides and Certifications if we want to save DB queries,
        # or simply rely on the template not using them.
        # Let's keep it clean and only fetch what's needed for the catalog.
        ctx = super(generic.ListView, self).get_context_data(**kwargs) # Call grandparent ListView to skip CourseListView additions?
        # Actually CourseListView logic is:
        # ctx = super().get_context_data(**kwargs) -> This calls ListView's
        # ctx['categories'] = ...
        # ctx['hero_slides'] = ...

        # We want Categories, but not Hero Slides.
        # So we can just re-implement get_context_data or call super() and remove keys.

        # Let's just implement it cleanly.
        ctx['categories'] = Category.objects.all()
        return ctx

class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'academy/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Check enrollment status
            enrollment = Enrollment.objects.filter(user=self.request.user, course=self.object).first()
            context['enrollment'] = enrollment
            context['is_enrolled'] = enrollment and enrollment.status == 'approved'
        
        context['reviews'] = self.object.reviews.all().order_by('-created_at')
        context['avg_rating'] = self.object.average_rating
        context['modules'] = self.object.modules.prefetch_related('lessons', 'quizzes').all()
        return context

# --- FORUM VIEWS ---

class ForumTopicListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = ForumTopic
    template_name = 'academy/forum_list.html'
    context_object_name = 'topics'
    paginate_by = 20

    def test_func(self):
        # Allow access only if user is enrolled in at least one course (status='approved')
        return Enrollment.objects.filter(user=self.request.user, status='approved').exists()

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.warning(self.request, "El foro es exclusivo para estudiantes inscritos en al menos un curso.")
            return redirect('academy:course_catalog')
        return super().handle_no_permission()

    def get_queryset(self):
        return ForumTopic.objects.all().select_related('user', 'user__profile').order_by('-created_at')

class ForumTopicDetailView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    model = ForumTopic
    template_name = 'academy/forum_detail.html'
    context_object_name = 'topic'

    def test_func(self):
        # Allow access only if user is enrolled in at least one course
        return Enrollment.objects.filter(user=self.request.user, status='approved').exists()

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
             messages.warning(self.request, "El foro es exclusivo para estudiantes inscritos.")
             return redirect('academy:course_catalog')
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['replies'] = self.object.replies.select_related('user', 'user__profile').order_by('created_at')

        # Increment views (simple count)
        # To avoid counting refresh, we could use session keys, but simple count is fine for now.
        self.object.views += 1
        self.object.save(update_fields=['views'])

        return ctx

    def post(self, request, *args, **kwargs):
        topic = self.get_object()
        content = request.POST.get('content')
        if content:
            reply = ForumReply.objects.create(topic=topic, user=request.user, content=content)
            messages.success(request, "Respuesta publicada.")
            return redirect('academy:forum_topic_detail', pk=topic.id)
        return redirect('academy:forum_topic_detail', pk=topic.id)

class CreateTopicView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = ForumTopic
    fields = ['title', 'content', 'course']
    template_name = 'academy/forum_topic_form.html'
    success_url = reverse_lazy('academy:forum_list')

    def test_func(self):
        # Allow access only if user is enrolled in at least one course
        return Enrollment.objects.filter(user=self.request.user, status='approved').exists()

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
             messages.warning(self.request, "Debes estar inscrito en un curso para crear temas.")
             return redirect('academy:course_catalog')
        return super().handle_no_permission()

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Tema creado exitosamente.")
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Optional: Filter courses to only those user is enrolled in?
        # For simplicity, let's leave as is or make course optional.
        return form

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

# --- INICIAR CURSO ---

@login_required
def course_play(request, slug):
    """
    Redirige a la primera lección no completada del curso, 
    o a la primera lección si el curso no se ha empezado.
    """
    course = get_object_or_404(Course, slug=slug)
    
    # Verificar inscripción aprobada
    enrollment = Enrollment.objects.filter(user=request.user, course=course, status='approved').first()
    if not enrollment:
        messages.warning(request, "Debes estar inscrito para acceder al contenido.")
        return redirect('academy:course_detail', slug=slug)

    # Buscar la primera lección NO completada
    # Obtenemos todas las lecciones del curso ordenadas
    lessons = Lesson.objects.filter(module__course=course).order_by('module__order', 'order')
    
    if not lessons.exists():
        messages.info(request, "Este curso aún no tiene contenido.")
        return redirect('academy:course_detail', slug=slug)

    # Obtenemos los IDs de las lecciones completadas por el usuario
    completed_lessons_ids = LessonProgress.objects.filter(
        user=request.user, 
        lesson__in=lessons, 
        is_completed=True
    ).values_list('lesson_id', flat=True)

    # Encontramos la primera lección que NO está en la lista de completadas
    next_lesson = None
    for lesson in lessons:
        if lesson.id not in completed_lessons_ids:
            next_lesson = lesson
            break
    
    # Si todas están completadas, ir a la última lección (o al certificado)
    if not next_lesson:
        next_lesson = lessons.last()

    # Actualizar fecha de último acceso
    enrollment.last_accessed = timezone.now()
    enrollment.save()

    return redirect('academy:lesson_detail', pk=next_lesson.id)



# --- NUEVO FLUJO DE INSCRIPCIÓN Y PAGO ---

@login_required
def enroll_course_step1(request, slug):
    """
    Paso 1: Validación de Datos Personales (DNI, Dirección, etc.)
    """
    course = get_object_or_404(Course, slug=slug)
    
    # Verificar si ya existe inscripción
    existing_enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    if existing_enrollment:
        if existing_enrollment.status == 'approved':
            return redirect('academy:dashboard')
        elif existing_enrollment.status in ['pending', 'review']:
            return redirect('academy:payment_gateway', pk=existing_enrollment.id)

    # Pre-llenar formulario con datos del perfil
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
            # Actualizar datos del usuario/perfil
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.save()
            
            profile.dni = form.cleaned_data['dni']
            profile.address = form.cleaned_data['address']
            profile.academic_profile = form.cleaned_data['academic_profile']
            profile.save()

            # Crear Inscripción PENDIENTE
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
    """
    Paso 2: Pasarela de Pago Manual (Yape/Banco) y Subida de Voucher
    """
    enrollment = get_object_or_404(Enrollment, pk=pk, user=request.user)

    if enrollment.status == 'approved':
        messages.success(request, "¡Ya estás inscrito en este curso!")
        return redirect('academy:dashboard')

    if request.method == 'POST':
        form = VoucherUploadForm(request.POST, request.FILES, instance=enrollment)
        if form.is_valid():
            enrollment.status = 'review' # Cambiar estado a revisión

            # Save selected payment plan
            plan = request.POST.get('payment_plan')
            if plan in ['full', 'monthly']:
                enrollment.selected_payment_plan = plan

            enrollment.save()
            messages.success(request, "Tu constancia ha sido enviada. Un administrador la revisará pronto.")
            return redirect('academy:dashboard')
    else:
        form = VoucherUploadForm(instance=enrollment)

    # Obtener métodos de pago permitidos para este curso
    payment_methods = enrollment.course.allowed_payment_methods.all()

    return render(request, 'academy/payment_gateway.html', {
        'enrollment': enrollment,
        'course': enrollment.course,
        'form': form,
        'payment_methods': payment_methods
    })

# --- DASHBOARD & LEARNING ---

class StudentPaymentsView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'academy/student_payments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get all monthly enrollments
        enrollments = Enrollment.objects.filter(user=user, selected_payment_plan='monthly', status__in=['approved', 'pending']).select_related('course')

        installments_data = []

        for enrollment in enrollments:
            course = enrollment.course
            if not course.duration_months or not course.monthly_price:
                continue

            # Check if installments exist. If not, try to generate them (backward compatibility / safety net)
            # though the signal should handle it now.
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

class StudentDashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'academy/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Agrupamos inscripciones por estado
        all_enrollments = Enrollment.objects.filter(user=user).select_related('course').order_by('-last_accessed')
        
        context['pending_enrollments'] = all_enrollments.filter(status__in=['pending', 'review', 'rejected'])
        context['active_enrollments'] = all_enrollments.filter(status='approved', is_completed=False)
        context['completed_enrollments'] = all_enrollments.filter(status='approved', is_completed=True)
        
        # Calcular progreso para cursos activos
        for enrollment in context['active_enrollments']:
            # Lógica simple de progreso
            total = Lesson.objects.filter(module__course=enrollment.course).count()
            completed = LessonProgress.objects.filter(user=user, lesson__module__course=enrollment.course, is_completed=True).count()
            enrollment.progress = int((completed / total) * 100) if total > 0 else 0

        return context

class LessonDetailView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    model = Lesson
    template_name = 'academy/lesson_detail.html'
    context_object_name = 'lesson'

    def test_func(self):
        lesson = self.get_object()
        course = lesson.module.course
        
        # 1. Verificar si el curso está en lanzamiento (bloqueado)
        # Nota: Permitimos acceso a profesores/admins incluso si es "upcoming"
        if course.is_upcoming and not (self.request.user.is_superuser or self.request.user == course.instructor):
            return False

        # 2. Verificar inscripción aprobada (Lógica original)
        enrollment = Enrollment.objects.filter(user=self.request.user, course=course, status='approved').first()
        if not enrollment:
            return False

        # 3. Verificar si está al día con los pagos
        if not enrollment.is_up_to_date:
            return False

        return True

    def handle_no_permission(self):
        # Si el usuario no tiene permiso, verificamos por qué
        lesson = self.get_object()
        course = lesson.module.course
        
        # Si es por fecha de lanzamiento, lo mandamos a la página de venta (donde verá el contador)
        if course.is_upcoming and not (self.request.user.is_superuser or self.request.user == course.instructor):
            messages.warning(self.request, f"Este contenido estará disponible el {course.launch_date.strftime('%d/%m/%Y %H:%M')}")
            return redirect('academy:course_detail', slug=course.slug)

        # Verificar si está inscrito pero con deuda
        enrollment = Enrollment.objects.filter(user=self.request.user, course=course, status='approved').first()
        if enrollment and not enrollment.is_up_to_date:
             messages.warning(self.request, "Tienes cuotas vencidas pendientes. Por favor regulariza tu pago para continuar.")
             return redirect('academy:student_payments')
            
        # Si no está inscrito, al dashboard
        return redirect('academy:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # --- LÓGICA DE PRERREQUISITOS (Lección anterior completada) ---
        # "Impedir ver la Lección 2 hasta que la Lección 1 esté marcada como is_completed."
        course = self.object.module.course
        all_lessons = list(Lesson.objects.filter(module__course=course).order_by('module__order', 'order'))

        try:
            curr_idx = all_lessons.index(self.object)
            if curr_idx > 0:
                prev_lesson = all_lessons[curr_idx - 1]
                prev_completed = LessonProgress.objects.filter(
                    user=self.request.user,
                    lesson=prev_lesson,
                    is_completed=True
                ).exists()
                if not prev_completed:
                    context['locked'] = True
                    context['lock_message'] = f"Debes completar la lección '{prev_lesson.title}' para acceder a este contenido."
                    # Limpiamos el contenido si está bloqueado para que no se vea en el HTML
                    self.object.content = ""
                    self.object.video_url = None
                    self.object.file = None
        except ValueError:
            pass

        # Datos básicos
        context['is_completed'] = LessonProgress.objects.filter(user=self.request.user, lesson=self.object, is_completed=True).exists()
        context['course'] = course
        context['modules'] = course.modules.prefetch_related('lessons', 'quizzes').all()
        
        # Navegación (Anterior / Siguiente)
        try:
            curr_idx = all_lessons.index(self.object)
            context['prev_lesson'] = all_lessons[curr_idx - 1] if curr_idx > 0 else None
            context['next_lesson'] = all_lessons[curr_idx + 1] if curr_idx < len(all_lessons) - 1 else None
        except: pass
        
        # Actualizar "último acceso"
        Enrollment.objects.filter(user=self.request.user, course=course).update(last_accessed=timezone.now())

        # --- COMENTARIOS ---
        # Obtenemos solo los comentarios principales (sin padres) ordenados
        context['comments'] = self.object.comments.filter(parent=None).select_related('user__profile').prefetch_related('replies__user__profile').order_by('-created_at')
        context['comment_form'] = LessonCommentForm()

        # --- TAREA / ASIGNACIÓN ---
        if self.object.lesson_type == 'assignment':
            progress, created = LessonProgress.objects.get_or_create(user=self.request.user, lesson=self.object)
            context['submission_form'] = AssignmentSubmissionForm(instance=progress)
            context['assignment_progress'] = progress
        
        # --- PROGRESO DEL CURSO (%) ---
        total_lessons = Lesson.objects.filter(module__course=course).count()
        completed_lessons_count = LessonProgress.objects.filter(
            user=self.request.user,
            lesson__module__course=course,
            is_completed=True
        ).count()

        context['progress_percentage'] = int((completed_lessons_count / total_lessons) * 100) if total_lessons > 0 else 0

        return context

@login_required
def submit_assignment(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    # Check enrollment
    if not Enrollment.objects.filter(user=request.user, course=lesson.module.course, status='approved').exists():
         return redirect('academy:dashboard')

    if request.method == 'POST':
        progress, created = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=progress)
        if form.is_valid():
            progress = form.save(commit=False)
            progress.is_completed = True # Submit marks as done for progress tracking (or wait for grade)
            # We will mark as completed upon submission for now so it shows in progress
            progress.save()
            messages.success(request, "Tarea enviada correctamente.")

    return redirect('academy:lesson_detail', pk=lesson_id)

@login_required
def mark_lesson_complete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if not Enrollment.objects.filter(user=request.user, course=lesson.module.course, status='approved').exists():
        return redirect('academy:dashboard')
    
    LessonProgress.objects.get_or_create(user=request.user, lesson=lesson, defaults={'is_completed': True})
    LessonProgress.objects.filter(user=request.user, lesson=lesson).update(is_completed=True)
    return redirect('academy:lesson_detail', pk=pk)

# --- AUTH & TEACHER ---

# --- LOGIN MODERNO (AÑADIR ESTA CLASE) ---
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

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

# ... (Aquí sigue tu SignUpView existente. OJO: Cambia su success_url) ...


# --- SIGNUP VIEW (CORREGIDA PARA REACT) ---
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
        # --- AQUÍ ESTÁ LA CLAVE PARA EL ERROR 400 ---
        errors = dict(form.errors)
        
        # Esto imprimirá el error REAL en tu terminal (pantalla negra)
        print("❌ ERRORES DE REGISTRO DETECTADOS:", errors) 
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Devolvemos los errores al React para que los muestre
            return JsonResponse({
                'success': False,
                'errors': errors
            }, status=400)
            
        return super().form_invalid(form)

@login_required
@login_required
def profile_edit(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Perfil actualizado correctamente")
            return redirect('academy:profile_edit') # Recargamos la misma página para ver cambios
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    # Obtenemos todo el historial para las pestañas de Pagos y Certificados
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course').order_by('-enrolled_at')

    return render(request, 'academy/profile_edit.html', {
        'u_form': u_form, 
        'p_form': p_form,
        'enrollments': enrollments
    })

class QuizDetailView(LoginRequiredMixin, generic.DetailView):
    model = Quiz
    template_name = 'academy/quiz_take.html'
    context_object_name = 'quiz'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Check prerequisites
        if self.object.is_final_exam:
             # Check if all lessons in the course are completed
             total_lessons = Lesson.objects.filter(module__course=self.object.module.course).count()
             completed_lessons = LessonProgress.objects.filter(
                 user=self.request.user,
                 lesson__module__course=self.object.module.course,
                 is_completed=True
             ).count()
             if completed_lessons < total_lessons:
                 ctx['locked'] = True
                 ctx['lock_message'] = "Debes completar todas las lecciones del curso antes de tomar el examen final."
        else:
             # Check if lessons in current module (and previous modules) are completed?
             # Requirement: "Prevent making the final exam until completing all modules".
             # For normal quizzes, maybe just module completion?
             # Let's enforce that lessons in THIS module must be completed.
             module_lessons = Lesson.objects.filter(module=self.object.module).count()
             completed_module_lessons = LessonProgress.objects.filter(
                 user=self.request.user,
                 lesson__module=self.object.module,
                 is_completed=True
             ).count()
             if completed_module_lessons < module_lessons:
                 ctx['locked'] = True
                 ctx['lock_message'] = "Debes completar las lecciones de este módulo antes de tomar el examen."

        # --- CAMBIO AQUÍ: Lógica de Reintento ---
        # Solo buscamos la submission si NO estamos en modo 'retake'
        if not self.request.GET.get('retake'):
            ctx['submission'] = QuizSubmission.objects.filter(user=self.request.user, quiz=self.object).order_by('-score').first()
        else:
            ctx['submission'] = None

        # Question Randomization Logic
        questions = self.object.questions.all().order_by('order')

        if self.object.randomize_questions and not ctx.get('locked') and not ctx['submission']:
            session_key = f'quiz_{self.object.id}_questions'
            question_ids = self.request.session.get(session_key)

            if not question_ids:
                import random
                all_q_ids = list(questions.values_list('id', flat=True))
                count = min(len(all_q_ids), self.object.questions_to_show)
                question_ids = random.sample(all_q_ids, count)
                self.request.session[session_key] = question_ids
                # Clear start time on new question set generation
                if f'quiz_{self.object.id}_start_time' in self.request.session:
                    del self.request.session[f'quiz_{self.object.id}_start_time']

            # Fetch specific questions in order (or preserved random order?)
            # If we want to preserve random order:
            questions = []
            for qid in question_ids:
                try:
                    questions.append(Question.objects.get(id=qid))
                except Question.DoesNotExist:
                    pass

        ctx['questions'] = questions

        # Time Limit Logic
        if self.object.duration > 0 and not ctx.get('locked') and not ctx['submission']:
            import time
            session_start_key = f'quiz_{self.object.id}_start_time'
            start_time = self.request.session.get(session_start_key)

            if not start_time:
                start_time = time.time()
                self.request.session[session_start_key] = start_time

            elapsed = time.time() - start_time
            remaining = (self.object.duration * 60) - elapsed
            ctx['remaining_seconds'] = max(0, int(remaining))

        return ctx

@login_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if not Enrollment.objects.filter(user=request.user, course=quiz.module.course, status='approved').exists():
        return redirect('academy:dashboard')
    
    return redirect('academy:quiz_detail', pk=pk)

class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.profile.role == 'teacher' or self.request.user.is_superuser)

class TeacherDashboardView(LoginRequiredMixin, TeacherRequiredMixin, generic.ListView):
    model = Course
    template_name = 'academy/teacher_dashboard.html'
    context_object_name = 'courses'
    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user).annotate(
            student_count=Count('enrollments', filter=Q(enrollments__status='approved'))
        )

class TeacherCourseStudentsView(LoginRequiredMixin, TeacherRequiredMixin, generic.DetailView):
    model = Course
    template_name = 'academy/teacher_course_students.html'
    context_object_name = 'course'

    def test_func(self):
        # Primero verifica rol de profesor (del mixin, pero DetailView sobreescribe test_func si no cuidamos el orden o llamamos super)
        # UserPassesTestMixin solo permite un test_func.
        # Combinemos lógica: Debe ser teacher Y ser el instructor del curso.
        is_teacher = self.request.user.is_authenticated and (self.request.user.profile.role == 'teacher' or self.request.user.is_superuser)
        if not is_teacher: return False

        course = self.get_object()
        return self.request.user == course.instructor or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # List approved students
        context['enrollments'] = Enrollment.objects.filter(
            course=self.object,
            status='approved'
        ).select_related('user', 'user__profile').order_by('-enrolled_at')
        return context

class CourseCreateView(LoginRequiredMixin, TeacherRequiredMixin, generic.CreateView):
    model = Course
    form_class = CourseForm # <--- USAR EL FORMULARIO PERSONALIZADO
    # fields = [...]  <--- ELIMINA ESTA LÍNEA (fields no se usa si usas form_class)
    template_name = 'academy/course_form.html'
    success_url = reverse_lazy('academy:teacher_dashboard')

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        return super().form_valid(form)

class CourseUpdateView(LoginRequiredMixin, TeacherRequiredMixin, generic.UpdateView):
    model = Course
    form_class = CourseForm # <--- USAR EL FORMULARIO PERSONALIZADO
    # fields = [...] <--- ELIMINA ESTA LÍNEA
    template_name = 'academy/course_form.html'
    success_url = reverse_lazy('academy:teacher_dashboard')
    
    def get_queryset(self): 
        return Course.objects.filter(instructor=self.request.user)

@login_required
def course_content_manage(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    modules = course.modules.prefetch_related('lessons').all()

    return render(request, 'academy/course_content_manage.html', {
        'course': course,
        'modules': modules,
        'module_form': ModuleForm(),
        'lesson_form': LessonForm()
    })

@login_required
def add_module(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, "Módulo agregado")
    return redirect('academy:course_content', slug=slug)

@login_required
def add_lesson(request):
    if request.method == 'POST':
        module_id = request.POST.get('module_id')
        module = get_object_or_404(Module, id=module_id, course__instructor=request.user)
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            messages.success(request, "Lección agregada")
            return redirect('academy:course_content', slug=module.course.slug)
    return redirect('academy:teacher_dashboard')

@login_required
def delete_module(request, pk):
    module = get_object_or_404(Module, pk=pk, course__instructor=request.user)
    slug = module.course.slug

    # --- PROTECCIÓN ---
    if module.course.enrollments.exists():
        messages.error(request, "No puedes eliminar módulos de un curso con estudiantes inscritos. Archiva el curso o contacta al admin.")
        return redirect('academy:course_content', slug=slug)
    # ------------------

    module.delete()
    messages.success(request, "Módulo eliminado")
    return redirect('academy:course_content', slug=slug)

@login_required
def add_quiz(request):
    if request.method == 'POST':
        module_id = request.POST.get('module_id')
        module = get_object_or_404(Module, id=module_id, course__instructor=request.user)
        # Create a basic quiz
        quiz = Quiz.objects.create(
            module=module,
            title="Nuevo Examen",
            description="Descripción del examen"
        )
        return redirect('academy:edit_quiz', pk=quiz.id)
    return redirect('academy:teacher_dashboard')

@login_required
def edit_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, module__course__instructor=request.user)

    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, "Examen actualizado")
            return redirect('academy:edit_quiz', pk=quiz.id)
    else:
        form = QuizForm(instance=quiz)

    questions = quiz.questions.all().order_by('order')
    return render(request, 'academy/quiz_edit.html', {
        'quiz': quiz,
        'form': form,
        'questions': questions
    })

@login_required
def delete_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, module__course__instructor=request.user)
    slug = quiz.module.course.slug

    # --- PROTECCIÓN ---
    if quiz.module.course.enrollments.exists():
        messages.error(request, "No puedes eliminar exámenes de un curso con estudiantes inscritos.")
        return redirect('academy:course_content', slug=slug)
    # ------------------

    quiz.delete()
    messages.success(request, "Examen eliminado")
    return redirect('academy:course_content', slug=slug)

@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, module__course__instructor=request.user)

    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
             # Handle JSON payload for questions from AlpineJS
            data = json.loads(request.body)
            question_id = data.get('id')

            if question_id:
                question = get_object_or_404(Question, pk=question_id, quiz=quiz)
            else:
                question = Question(quiz=quiz)

            question.text = data.get('text')
            question.question_type = data.get('question_type')
            question.points = float(data.get('points', 1))
            question.explanation = data.get('explanation', '')
            question.save()

            # Handle answers: Update existing, create new, delete missing
            incoming_answers = data.get('answers', [])
            incoming_ids = [int(a.get('id')) for a in incoming_answers if a.get('id')]

            # Delete answers that are not in the incoming list
            question.answers.exclude(id__in=incoming_ids).delete()

            for i, ans_data in enumerate(incoming_answers):
                ans_id = ans_data.get('id')
                defaults = {
                    'text': ans_data.get('text'),
                    'is_correct': ans_data.get('is_correct', False),
                    'match_text': ans_data.get('match_text', ''),
                    'order': ans_data.get('order', i)
                }

                if ans_id:
                    Answer.objects.filter(id=ans_id, question=question).update(**defaults)
                else:
                    Answer.objects.create(question=question, **defaults)

            return JsonResponse({'status': 'ok', 'question_id': question.id})

    return JsonResponse({'status': 'error'}, status=400)

@login_required
def delete_question(request, pk):
    question = get_object_or_404(Question, pk=pk, quiz__module__course__instructor=request.user)
    quiz_id = question.quiz.id
    question.delete()
    return redirect('academy:edit_quiz', pk=quiz_id)

@login_required
def quiz_submissions(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, module__course__instructor=request.user)

    # Get all submissions for this quiz
    submissions = QuizSubmission.objects.filter(quiz=quiz).select_related('user', 'user__profile').order_by('-submitted_at')

    return render(request, 'academy/quiz_submissions.html', {
        'quiz': quiz,
        'submissions': submissions
    })

@login_required
def quiz_grade_submission(request, submission_id):
    submission = get_object_or_404(QuizSubmission, pk=submission_id, quiz__module__course__instructor=request.user)

    if request.method == 'POST':
        # Handle feedback and manual grading
        submission.teacher_feedback = request.POST.get('feedback', '')

        # Calculate new score based on potential manual overrides
        total_points = 0
        earned_points = 0

        # Iterate through POST data to find manual grades
        # Expected format: grade_answer_<answer_id> = points OR correct/incorrect

        for answer in submission.answers.all():
            total_points += answer.question.points

            # Check if there's a manual override in POST
            # For short answers or manual correction
            manual_points = request.POST.get(f'points_{answer.id}')
            is_correct = request.POST.get(f'correct_{answer.id}')

            if manual_points is not None:
                try:
                    answer.points_awarded = float(manual_points)
                    answer.is_correct = (answer.points_awarded >= answer.question.points) # Simple logic, can be refined
                    if is_correct == 'true': answer.is_correct = True
                    elif is_correct == 'false': answer.is_correct = False

                    answer.save()
                except ValueError: pass

            earned_points += answer.points_awarded

        # Update final score
        submission.score = (earned_points / total_points) * 100 if total_points > 0 else 0
        submission.passed = submission.score >= submission.quiz.pass_mark
        submission.graded_by = request.user
        submission.save()

        messages.success(request, f"Calificación guardada. Nota final: {submission.score:.1f}")
        return redirect('academy:quiz_grade_submission', submission_id=submission.id)

    return render(request, 'academy/quiz_grade.html', {
        'submission': submission,
        'quiz': submission.quiz,
        'answers': submission.answers.select_related('question').prefetch_related('selected_answers').all()
    })

@login_required
def delete_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk, module__course__instructor=request.user)
    slug = lesson.module.course.slug

    # --- PROTECCIÓN ---
    if lesson.module.course.enrollments.exists():
        messages.error(request, "Curso con alumnos activos: No se puede eliminar contenido. Puedes editarlo para ocultar información.")
        return redirect('academy:course_content', slug=slug)
    # ------------------

    lesson.delete()
    messages.success(request, "Lección eliminada")
    return redirect('academy:course_content', slug=slug)

@login_required
def edit_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk, module__course__instructor=request.user)
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "Lección actualizada")
            return redirect('academy:course_content', slug=lesson.module.course.slug)
    else:
        form = LessonForm(instance=lesson)

    return render(request, 'academy/lesson_edit.html', {'form': form, 'lesson': lesson})

@login_required
def lesson_submissions(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id, module__course__instructor=request.user)

    # Get all "completed" progress entries for this lesson (submissions)
    submissions = LessonProgress.objects.filter(lesson=lesson, is_completed=True).select_related('user', 'user__profile').order_by('-updated_at')

    total_enrolled = Enrollment.objects.filter(course=lesson.module.course, status='approved').count()
    submitted_count = submissions.count()
    graded_count = submissions.filter(score__isnull=False).count()
    pending_grading_count = submitted_count - graded_count

    # Calculate average
    scores = [p.score for p in submissions if p.score is not None]
    average_score = sum(scores) / len(scores) if scores else 0

    return render(request, 'academy/lesson_submissions.html', {
        'lesson': lesson,
        'submissions': submissions,
        'total_enrolled': total_enrolled,
        'submitted_count': submitted_count,
        'graded_count': graded_count,
        'pending_grading_count': pending_grading_count,
        'average_score': round(average_score, 1) if scores else None
    })

@login_required
def grade_submission(request, progress_id):
    progress = get_object_or_404(LessonProgress, pk=progress_id, lesson__module__course__instructor=request.user)

    if request.method == 'POST':
        form = AssignmentGradingForm(request.POST, instance=progress)
        if form.is_valid():
            form.save()
            messages.success(request, f"Calificación guardada para {progress.user.username}")
            return redirect('academy:lesson_submissions', lesson_id=progress.lesson.id)
    else:
        form = AssignmentGradingForm(instance=progress)

    return render(request, 'academy/submission_grade.html', {
        'form': form,
        'progress': progress
    })

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, generic.TemplateView):
    template_name = 'academy/admin_dashboard.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Inscripciones
        ctx['pending_enrollments'] = Enrollment.objects.filter(status='review').select_related('user', 'course')
        ctx['history_enrollments'] = Enrollment.objects.filter(status__in=['approved', 'rejected']).select_related('user', 'course').order_by('-enrolled_at')[:50]
        
        # Cuotas Pendientes (Installments)
        ctx['pending_installments'] = Installment.objects.filter(status='review').select_related('enrollment__user', 'enrollment__course')

        # Usuarios y Cursos
        ctx['users'] = User.objects.select_related('profile').all().order_by('-date_joined')
        ctx['all_courses'] = Course.objects.select_related('instructor', 'category').annotate(
            student_count=Count('enrollments', filter=Q(enrollments__status='approved'))
        ).order_by('-created_at')
        
        # CMS (Contenido del Home)
        ctx['hero_slides'] = HeroSlide.objects.all().order_by('order')
        ctx['categories'] = Category.objects.all().order_by('name')
        ctx['certifications'] = CertificationCard.objects.all().order_by('order')
        ctx['announcements'] = AnnouncementCard.objects.all().order_by('order')
        
        # Configuración Global
        ctx['institutions'] = Institution.objects.all()
        ctx['payment_methods'] = PaymentMethod.objects.all()
        ctx['top_banners'] = TopBanner.objects.all().order_by('-created_at')  # <--- Nuevo: Banners
        
        # Site Config
        ctx['site_config'] = SiteConfiguration.get_solo()
        ctx['site_config_form'] = SiteConfigurationForm(instance=ctx['site_config'])

        return ctx

    def post(self, request, *args, **kwargs):
        # --- GESTIÓN DE CONFIGURACIÓN DEL SITIO ---
        if 'site_config_update' in request.POST:
            config = SiteConfiguration.get_solo()
            form = SiteConfigurationForm(request.POST, request.FILES, instance=config)
            if form.is_valid():
                form.save()
                messages.success(request, "Configuración del sitio actualizada.")
            else:
                messages.error(request, "Error al actualizar configuración.")
            return redirect('academy:admin_dashboard')

        # --- GESTIÓN DE INSCRIPCIONES ---
        if 'enrollment_id' in request.POST:
            enrollment = get_object_or_404(Enrollment, id=request.POST.get('enrollment_id'))
            action = request.POST.get('action')
            if action == 'approve':
                enrollment.status = 'approved'
                enrollment.save()

                # Si es mensual, aprobar automáticamente la cuota 1
                if enrollment.selected_payment_plan == 'monthly':
                    enrollment.generate_installments() # Asegura que existan
                    Installment.objects.filter(enrollment=enrollment, installment_number=1).update(
                        status='approved',
                        paid_at=timezone.now()
                    )

                messages.success(request, f"Inscripción de {enrollment.user.username} aprobada.")
            elif action == 'reject':
                enrollment.status = 'rejected'
                enrollment.save()
                messages.warning(request, f"Inscripción de {enrollment.user.username} rechazada.")

        # --- GESTIÓN DE CUOTAS (INSTALLMENTS) ---
        elif 'installment_id' in request.POST:
            inst = get_object_or_404(Installment, id=request.POST.get('installment_id'))
            action = request.POST.get('action')

            if action == 'approve':
                inst.status = 'approved'
                inst.paid_at = timezone.now()
                inst.save()
                # Opcional: Actualizar el contador en Enrollment
                inst.enrollment.installments_paid += 1
                inst.enrollment.save()
                messages.success(request, f"Cuota #{inst.installment_number} de {inst.enrollment.user.username} aprobada.")

            elif action == 'reject':
                inst.status = 'rejected'
                inst.feedback = "Voucher rechazado."
                inst.save()
                messages.warning(request, f"Cuota #{inst.installment_number} rechazada.")

        # --- GESTIÓN DE USUARIOS (ROLES) ---
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

        # --- GESTIÓN DE SLIDES (HOME) ---
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

        # --- GESTIÓN DE CERTIFICACIONES ---
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

        # --- GESTIÓN DE ANUNCIOS (CARDS) ---
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

        # --- GESTIÓN DE INSTITUCIONES ---
        elif 'institution_id' in request.POST:
            inst = get_object_or_404(Institution, id=request.POST.get('institution_id'))
            action = request.POST.get('action')
            if action == 'delete':
                inst.delete()
                messages.success(request, "Institución eliminada.")

        # --- GESTIÓN DE MÉTODOS DE PAGO ---
        elif 'payment_method_id' in request.POST:
            pm = get_object_or_404(PaymentMethod, id=request.POST.get('payment_method_id'))
            action = request.POST.get('action')
            if action == 'delete':
                pm.delete()
                messages.success(request, "Método de Pago eliminado.")

        # --- GESTIÓN DE CATEGORÍAS ---
        elif 'category_id' in request.POST:
            cat = get_object_or_404(Category, id=request.POST.get('category_id'))
            action = request.POST.get('action')
            if action == 'delete':
                cat.delete()
                messages.success(request, "Categoría eliminada.")

        # --- GESTIÓN DE CURSOS (ELIMINACIÓN) ---
        elif 'course_id' in request.POST:
            course = get_object_or_404(Course, id=request.POST.get('course_id'))
            action = request.POST.get('action')
            if action == 'delete':
                # --- NUEVA PROTECCIÓN ---
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

        # --- GESTIÓN DE BANNERS SUPERIORES (TOP BANNER) ---
        elif 'banner_id' in request.POST:
            banner = get_object_or_404(TopBanner, id=request.POST.get('banner_id'))
            action = request.POST.get('action')
            if action == 'toggle_active':
                # Opcional: Asegurar que solo un banner esté activo a la vez
                if not banner.is_active:
                    TopBanner.objects.update(is_active=False)
                
                banner.is_active = not banner.is_active
                banner.save()
                status = "activado" if banner.is_active else "desactivado"
                messages.success(request, f"Banner '{banner.message}' {status}.")
            elif action == 'delete':
                banner.delete()
                messages.success(request, "Banner eliminado.")

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

# --- CATEGORY MANAGEMENT ---
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

# --- CERTIFICATION CARD MANAGEMENT ---
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

# --- ANNOUNCEMENT CARD MANAGEMENT ---
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

# --- INSTITUTION MANAGEMENT ---
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

# --- PAYMENT METHOD MANAGEMENT ---
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

class CertificateView(LoginRequiredMixin, generic.DetailView):
    model = Course
    template_name = 'academy/certificate.html'
    context_object_name = 'course'
    def get_object(self): return get_object_or_404(Course, slug=self.kwargs['slug'])
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Check completion
        total = Lesson.objects.filter(module__course=self.object).count()
        completed = LessonProgress.objects.filter(user=self.request.user, lesson__module__course=self.object, is_completed=True).count()
        ctx['is_completed'] = total > 0 and total == completed
        ctx['student'] = self.request.user
        return ctx
    
@login_required
def add_comment(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    
    # Verificar seguridad: El usuario debe estar inscrito
    if not Enrollment.objects.filter(user=request.user, course=lesson.module.course, status='approved').exists():
        messages.error(request, "No tienes permiso para comentar.")
        return redirect('academy:dashboard')

    if request.method == 'POST':
        form = LessonCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.lesson = lesson
            comment.user = request.user
            
            # Verificar si es una respuesta a otro comentario
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_comment = get_object_or_404(LessonComment, id=parent_id)
                comment.parent = parent_comment
                
            comment.save()
            messages.success(request, "Tu pregunta ha sido publicada.")
            
    return redirect('academy:lesson_detail', pk=lesson_id)

class PublicProfileView(generic.DetailView):
    model = User
    template_name = 'academy/public_profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object

        # Get completed courses (certs)
        # We assume a course is completed if Enrollment.is_completed is True
        # Or if all lessons are done. Let's stick to Enrollment.is_completed for certificates
        completed_enrollments = Enrollment.objects.filter(user=user, status='approved', is_completed=True).select_related('course')

        context['completed_courses'] = completed_enrollments
        context['certificates_count'] = completed_enrollments.count()

        # Calculate total learning hours?
        total_minutes = 0
        for enrollment in completed_enrollments:
             # This is rough, assumes course duration. Better to store in Enrollment.
             pass

        return context
    
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
        # Ensure profile exists
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