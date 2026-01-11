from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from ..models import *
from ..forms import LessonCommentForm, AssignmentSubmissionForm

class CourseListView(generic.ListView):
    model = Course
    template_name = 'academy/course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        queryset = Course.objects.filter(status='published').select_related(
            'category',
            'instructor__profile'
        ).prefetch_related(
            'reviews'
        ).all()

        query = self.request.GET.get('q')
        if query: queryset = queryset.filter(title__icontains=query)

        cat_slug = self.request.GET.get('category')
        if cat_slug: queryset = queryset.filter(category__slug=cat_slug)

        levels = self.request.GET.getlist('level')
        if levels: queryset = queryset.filter(level__in=levels)

        price_filter = self.request.GET.get('price')
        if price_filter == 'free':
            queryset = queryset.filter(price=0)
        elif price_filter == 'paid':
            queryset = queryset.filter(price__gt=0)

        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        ctx['selected_levels'] = self.request.GET.getlist('level')
        ctx['selected_price'] = self.request.GET.get('price')
        ctx['selected_category'] = self.request.GET.get('category')

        ctx['hero_slides'] = HeroSlide.objects.filter(is_active=True).order_by('order')
        ctx['certifications'] = CertificationCard.objects.filter(is_active=True).order_by('order')
        ctx['slide_range'] = range(ctx['hero_slides'].count())
        ctx['announcements'] = AnnouncementCard.objects.filter(is_active=True).order_by('order')
        return ctx

class CourseCatalogView(CourseListView):
    template_name = 'academy/course_catalog.html'

    def get_context_data(self, **kwargs):
        ctx = super(generic.ListView, self).get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        return ctx

class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'academy/course_detail.html'
    context_object_name = 'course'

    def get_object(self):
        # Restrict access to non-published courses for regular users
        obj = super().get_object()
        if obj.status != 'published':
            # Allow owner or superuser
            if self.request.user.is_authenticated and (self.request.user.is_superuser or self.request.user == obj.instructor):
                return obj
            # Otherwise 404 (or could be 403, but 404 hides existence)
            from django.http import Http404
            raise Http404("Course not found")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            enrollment = Enrollment.objects.filter(user=self.request.user, course=self.object).first()
            context['enrollment'] = enrollment
            context['is_enrolled'] = enrollment and enrollment.status == 'approved'

        context['reviews'] = self.object.reviews.all().order_by('-created_at')
        context['avg_rating'] = self.object.average_rating
        context['modules'] = self.object.modules.prefetch_related('lessons', 'quizzes').all()
        return context

@login_required
def course_play(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enrollment = Enrollment.objects.filter(user=request.user, course=course, status='approved').first()
    if not enrollment:
        messages.warning(request, "Debes estar inscrito para acceder al contenido.")
        return redirect('academy:course_detail', slug=slug)

    lessons = Lesson.objects.filter(module__course=course).order_by('module__order', 'order')
    if not lessons.exists():
        messages.info(request, "Este curso aún no tiene contenido.")
        return redirect('academy:course_detail', slug=slug)

    completed_lessons_ids = LessonProgress.objects.filter(
        user=request.user,
        lesson__in=lessons,
        is_completed=True
    ).values_list('lesson_id', flat=True)

    next_lesson = None
    for lesson in lessons:
        if lesson.id not in completed_lessons_ids:
            next_lesson = lesson
            break

    if not next_lesson:
        next_lesson = lessons.last()

    enrollment.last_accessed = timezone.now()
    enrollment.save()

    return redirect('academy:lesson_detail', pk=next_lesson.id)

class StudentDashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'academy/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        all_enrollments = Enrollment.objects.filter(user=user).select_related('course').order_by('-last_accessed')

        context['pending_enrollments'] = all_enrollments.filter(status__in=['pending', 'review', 'rejected'])
        context['active_enrollments'] = all_enrollments.filter(status='approved', is_completed=False)
        context['completed_enrollments'] = all_enrollments.filter(status='approved', is_completed=True)

        for enrollment in context['active_enrollments']:
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
        if course.is_upcoming and not (self.request.user.is_superuser or self.request.user == course.instructor):
            return False
        enrollment = Enrollment.objects.filter(user=self.request.user, course=course, status='approved').first()
        if not enrollment:
            return False
        if not enrollment.is_up_to_date:
            return False
        return True

    def handle_no_permission(self):
        lesson = self.get_object()
        course = lesson.module.course
        if course.is_upcoming and not (self.request.user.is_superuser or self.request.user == course.instructor):
            messages.warning(self.request, f"Este contenido estará disponible el {course.launch_date.strftime('%d/%m/%Y %H:%M')}")
            return redirect('academy:course_detail', slug=course.slug)
        enrollment = Enrollment.objects.filter(user=self.request.user, course=course, status='approved').first()
        if enrollment and not enrollment.is_up_to_date:
             messages.warning(self.request, "Tienes cuotas vencidas pendientes. Por favor regulariza tu pago para continuar.")
             return redirect('academy:student_payments')
        return redirect('academy:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
                    self.object.content = ""
                    self.object.video_url = None
                    self.object.file = None
        except ValueError:
            pass

        context['is_completed'] = LessonProgress.objects.filter(user=self.request.user, lesson=self.object, is_completed=True).exists()
        context['course'] = course
        context['modules'] = course.modules.prefetch_related('lessons', 'quizzes').all()

        try:
            curr_idx = all_lessons.index(self.object)
            context['prev_lesson'] = all_lessons[curr_idx - 1] if curr_idx > 0 else None
            context['next_lesson'] = all_lessons[curr_idx + 1] if curr_idx < len(all_lessons) - 1 else None
        except: pass

        Enrollment.objects.filter(user=self.request.user, course=course).update(last_accessed=timezone.now())

        context['comments'] = self.object.comments.filter(parent=None).select_related('user__profile').prefetch_related('replies__user__profile').order_by('-created_at')
        context['comment_form'] = LessonCommentForm()

        if self.object.lesson_type == 'assignment':
            progress, created = LessonProgress.objects.get_or_create(user=self.request.user, lesson=self.object)
            context['submission_form'] = AssignmentSubmissionForm(instance=progress)
            context['assignment_progress'] = progress

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
    if not Enrollment.objects.filter(user=request.user, course=lesson.module.course, status='approved').exists():
         return redirect('academy:dashboard')

    if request.method == 'POST':
        progress, created = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=progress)
        if form.is_valid():
            progress = form.save(commit=False)
            progress.is_completed = True
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

class CertificateView(LoginRequiredMixin, generic.DetailView):
    model = Course
    template_name = 'academy/certificate.html'
    context_object_name = 'course'
    def get_object(self): return get_object_or_404(Course, slug=self.kwargs['slug'])
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        total = Lesson.objects.filter(module__course=self.object).count()
        completed = LessonProgress.objects.filter(user=self.request.user, lesson__module__course=self.object, is_completed=True).count()
        ctx['is_completed'] = total > 0 and total == completed
        ctx['student'] = self.request.user
        return ctx

@login_required
def add_comment(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    if not Enrollment.objects.filter(user=request.user, course=lesson.module.course, status='approved').exists():
        messages.error(request, "No tienes permiso para comentar.")
        return redirect('academy:dashboard')

    if request.method == 'POST':
        form = LessonCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.lesson = lesson
            comment.user = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_comment = get_object_or_404(LessonComment, id=parent_id)
                comment.parent = parent_comment
            comment.save()
            messages.success(request, "Tu pregunta ha sido publicada.")
    return redirect('academy:lesson_detail', pk=lesson_id)

# --- QUIZ STUDENT VIEWS ---
class QuizDetailView(LoginRequiredMixin, generic.DetailView):
    model = Quiz
    template_name = 'academy/quiz_take.html'
    context_object_name = 'quiz'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.object.is_final_exam:
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
             module_lessons = Lesson.objects.filter(module=self.object.module).count()
             completed_module_lessons = LessonProgress.objects.filter(
                 user=self.request.user,
                 lesson__module=self.object.module,
                 is_completed=True
             ).count()
             if completed_module_lessons < module_lessons:
                 ctx['locked'] = True
                 ctx['lock_message'] = "Debes completar las lecciones de este módulo antes de tomar el examen."

        if not self.request.GET.get('retake'):
            ctx['submission'] = QuizSubmission.objects.filter(user=self.request.user, quiz=self.object).order_by('-score').first()
        else:
            ctx['submission'] = None

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
                if f'quiz_{self.object.id}_start_time' in self.request.session:
                    del self.request.session[f'quiz_{self.object.id}_start_time']

            questions = []
            for qid in question_ids:
                try:
                    questions.append(Question.objects.get(id=qid))
                except Question.DoesNotExist:
                    pass

        ctx['questions'] = questions

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
