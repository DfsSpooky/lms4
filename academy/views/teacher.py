from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.urls import reverse_lazy
import json
from ..models import Course, Enrollment, Module, Lesson, Quiz, Question, Answer, QuizSubmission, LessonProgress
from ..forms import CourseForm, ModuleForm, LessonForm, QuizForm, AssignmentGradingForm

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
        is_teacher = self.request.user.is_authenticated and (self.request.user.profile.role == 'teacher' or self.request.user.is_superuser)
        if not is_teacher: return False
        course = self.get_object()
        return self.request.user == course.instructor or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enrollments'] = Enrollment.objects.filter(
            course=self.object,
            status='approved'
        ).select_related('user', 'user__profile').order_by('-enrolled_at')
        return context

class CourseCreateView(LoginRequiredMixin, TeacherRequiredMixin, generic.CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'academy/course_form.html'
    success_url = reverse_lazy('academy:teacher_dashboard')

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        return super().form_valid(form)

class CourseUpdateView(LoginRequiredMixin, TeacherRequiredMixin, generic.UpdateView):
    model = Course
    form_class = CourseForm
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
    if module.course.enrollments.exists():
        messages.error(request, "No puedes eliminar módulos de un curso con estudiantes inscritos. Archiva el curso o contacta al admin.")
        return redirect('academy:course_content', slug=slug)
    module.delete()
    messages.success(request, "Módulo eliminado")
    return redirect('academy:course_content', slug=slug)

@login_required
def add_quiz(request):
    if request.method == 'POST':
        module_id = request.POST.get('module_id')
        module = get_object_or_404(Module, id=module_id, course__instructor=request.user)
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
    if quiz.module.course.enrollments.exists():
        messages.error(request, "No puedes eliminar exámenes de un curso con estudiantes inscritos.")
        return redirect('academy:course_content', slug=slug)
    quiz.delete()
    messages.success(request, "Examen eliminado")
    return redirect('academy:course_content', slug=slug)

@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, module__course__instructor=request.user)

    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
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

            incoming_answers = data.get('answers', [])
            incoming_ids = [int(a.get('id')) for a in incoming_answers if a.get('id')]

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
    submissions = QuizSubmission.objects.filter(quiz=quiz).select_related('user', 'user__profile').order_by('-submitted_at')
    return render(request, 'academy/quiz_submissions.html', {
        'quiz': quiz,
        'submissions': submissions
    })

@login_required
def quiz_grade_submission(request, submission_id):
    submission = get_object_or_404(QuizSubmission, pk=submission_id, quiz__module__course__instructor=request.user)

    if request.method == 'POST':
        submission.teacher_feedback = request.POST.get('feedback', '')
        total_points = 0
        earned_points = 0

        for answer in submission.answers.all():
            total_points += answer.question.points
            manual_points = request.POST.get(f'points_{answer.id}')
            is_correct = request.POST.get(f'correct_{answer.id}')

            if manual_points is not None:
                try:
                    answer.points_awarded = float(manual_points)
                    answer.is_correct = (answer.points_awarded >= answer.question.points)
                    if is_correct == 'true': answer.is_correct = True
                    elif is_correct == 'false': answer.is_correct = False
                    answer.save()
                except ValueError: pass
            earned_points += answer.points_awarded

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
    if lesson.module.course.enrollments.exists():
        messages.error(request, "Curso con alumnos activos: No se puede eliminar contenido. Puedes editarlo para ocultar información.")
        return redirect('academy:course_content', slug=slug)
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
    submissions = LessonProgress.objects.filter(lesson=lesson, is_completed=True).select_related('user', 'user__profile').order_by('-updated_at')

    total_enrolled = Enrollment.objects.filter(course=lesson.module.course, status='approved').count()
    submitted_count = submissions.count()
    graded_count = submissions.filter(score__isnull=False).count()
    pending_grading_count = submitted_count - graded_count

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
