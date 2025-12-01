import os
import subprocess
import sys
from pathlib import Path

# --- CONFIGURACIÓN ---
PROJECT_NAME = "lms_final"
APP_NAME = "academy"
VENV_NAME = "venv"

if sys.platform == "win32":
    venv_python = os.path.join(VENV_NAME, "Scripts", "python.exe")
else:
    venv_python = os.path.join(VENV_NAME, "bin", "python")

def run_command(command, cwd=None):
    try:
        subprocess.check_call(command, shell=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"[Error] {e}")
        sys.exit(1)

def create_file(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Creado] {path}")

def main():
    print("=== FINALIZANDO BACKEND LMS (V. DEFINITIVA) ===")

    # 1. Entorno y Dependencias (Aseguramos Pillow para imágenes)
    if not os.path.exists(VENV_NAME):
        run_command(f"{sys.executable} -m venv {VENV_NAME}")
    
    run_command(f'"{venv_python}" -m pip install django djangorestframework django-cors-headers Pillow')

    if not os.path.exists(PROJECT_NAME):
        run_command(f'"{venv_python}" -m django startproject {PROJECT_NAME} .')
    
    if not os.path.exists(APP_NAME):
        run_command(f'"{venv_python}" manage.py startapp {APP_NAME}')

    # 2. Settings
    settings_path = Path(PROJECT_NAME) / "settings.py"
    settings_content = settings_path.read_text(encoding="utf-8")
    
    if "'rest_framework'" not in settings_content:
        settings_content = settings_content.replace(
            "'django.contrib.staticfiles',",
            f"'django.contrib.staticfiles',\n    'rest_framework',\n    'corsheaders',\n    '{APP_NAME}',"
        )
        settings_content = settings_content.replace(
            "'django.middleware.common.CommonMiddleware',",
            "'corsheaders.middleware.CorsMiddleware',\n    'django.middleware.common.CommonMiddleware',"
        )
        settings_content += """
CORS_ALLOW_ALL_ORIGINS = True
import os
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
LOGIN_REDIRECT_URL = '/'
"""
    create_file(settings_path, settings_content)

    # 3. MODELOS (Con Perfil y Notas de Examen)
    models_code = """from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

# --- USUARIO EXTENDIDO ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=20, choices=[('student', 'Estudiante'), ('teacher', 'Profesor')], default='student')

    def __str__(self): return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created: Profile.objects.create(user=instance)

# --- CURSOS ---
class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='courses/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.title

class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta: ordering = ['order']
    def __str__(self): return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    module = models.ForeignKey(Module, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    video_url = models.URLField(blank=True, null=True)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta: ordering = ['order']
    def __str__(self): return self.title

# --- EXÁMENES ---
class Quiz(models.Model):
    module = models.ForeignKey(Module, related_name='quizzes', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    pass_mark = models.IntegerField(default=70) # Porcentaje para aprobar

    def __str__(self): return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    
    def __str__(self): return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self): return self.text

class QuizSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField() # Nota obtenida (0 a 100)
    passed = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

# --- PROGRESO ---
class Enrollment(models.Model):
    user = models.ForeignKey(User, related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
"""
    create_file(f"{APP_NAME}/models.py", models_code)

    # 4. ADMIN
    admin_code = """from django.contrib import admin
from .models import *

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]

class ModuleInline(admin.StackedInline):
    model = Module
    extra = 0

class CourseAdmin(admin.ModelAdmin):
    inlines = [ModuleInline]

admin.site.register(Profile)
admin.site.register(Course, CourseAdmin)
admin.site.register(Module)
admin.site.register(Lesson)
admin.site.register(Quiz)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizSubmission)
admin.site.register(Enrollment)
"""
    create_file(f"{APP_NAME}/admin.py", admin_code)

    # 5. SERIALIZERS (Aquí está la clave de la comunicación con React)
    serializers_code = """from rest_framework import serializers
from .models import *

# --- USUARIO ---
class ProfileSerializer(serializers.ModelSerializer):
    class Meta: model = Profile; fields = ['avatar', 'role', 'bio']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

# --- CONTENIDO ---
class AnswerSerializer(serializers.ModelSerializer):
    class Meta: model = Answer; fields = ['id', 'text'] # Ocultamos is_correct

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    class Meta: model = Question; fields = ['id', 'text', 'answers']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    user_score = serializers.SerializerMethodField()

    class Meta: model = Quiz; fields = ['id', 'title', 'pass_mark', 'questions', 'user_score']

    def get_user_score(self, obj):
        # Si el usuario ya dio el examen, devolvemos su nota
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            sub = QuizSubmission.objects.filter(user=request.user, quiz=obj).order_by('-score').first()
            if sub: return {'score': sub.score, 'passed': sub.passed}
        return None

class LessonSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()
    class Meta: model = Lesson; fields = ['id', 'title', 'video_url', 'content', 'order', 'is_completed']

    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return LessonProgress.objects.filter(user=request.user, lesson=obj, is_completed=True).exists()
        return False

class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    quizzes = QuizSerializer(many=True, read_only=True)
    class Meta: model = Module; fields = ['id', 'title', 'lessons', 'quizzes']

class CourseDetailSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    is_enrolled = serializers.SerializerMethodField()

    class Meta: model = Course; fields = ['id', 'title', 'description', 'price', 'modules', 'is_enrolled']

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(user=request.user, course=obj).exists()
        return False

class CourseListSerializer(serializers.ModelSerializer):
    class Meta: model = Course; fields = ['id', 'title', 'slug', 'thumbnail', 'price']
"""
    create_file(f"{APP_NAME}/serializers.py", serializers_code)

    # 6. VIEWS (Lógica de Negocio y Exámenes)
    views_code = """from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *

# --- ENDPOINT ESPECIAL: QUIÉN SOY ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

# --- VIEWSETS ---
class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve': return CourseDetailSerializer
        return CourseListSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def enroll(self, request, pk=None):
        course = self.get_object()
        Enrollment.objects.get_or_create(user=request.user, course=course)
        return Response({'status': 'inscripto'})

class ProgressViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # Completar Lección
    @action(detail=False, methods=['post'], url_path='lesson/(?P<lesson_id>[^/.]+)/complete')
    def complete_lesson(self, request, lesson_id=None):
        lesson = Lesson.objects.get(pk=lesson_id)
        LessonProgress.objects.get_or_create(user=request.user, lesson=lesson, is_completed=True)
        return Response({'status': 'ok'})

    # ENVIAR EXAMEN (Lógica de Calificación)
    @action(detail=False, methods=['post'], url_path='quiz/(?P<quiz_id>[^/.]+)/submit')
    def submit_quiz(self, request, quiz_id=None):
        quiz = Quiz.objects.get(pk=quiz_id)
        data = request.data.get('answers', {}) # Esperamos un JSON {pregunta_id: respuesta_id}
        
        correct_count = 0
        total_questions = quiz.questions.count()

        if total_questions == 0:
            return Response({'error': 'Examen vacío'}, status=400)

        for q_id, a_id in data.items():
            try:
                # Verificamos si la respuesta enviada es la correcta en la BD
                answer = Answer.objects.get(pk=a_id, question_id=q_id, is_correct=True)
                correct_count += 1
            except Answer.DoesNotExist:
                pass # Respuesta incorrecta
        
        score = (correct_count / total_questions) * 100
        passed = score >= quiz.pass_mark

        # Guardamos la nota
        QuizSubmission.objects.create(user=request.user, quiz=quiz, score=score, passed=passed)

        return Response({'score': score, 'passed': passed, 'correct_count': correct_count})
"""
    create_file(f"{APP_NAME}/views.py", views_code)

    # 7. URLS
    urls_code = """from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from academy.views import CourseViewSet, ProgressViewSet, current_user

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'progress', ProgressViewSet, basename='progress')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/me/', current_user), # URL vital para React
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""
    create_file(f"{PROJECT_NAME}/urls.py", urls_code)

    # 8. MIGRAR Y POBLAR
    print("Migrando Base de Datos...")
    run_command(f'"{venv_python}" manage.py makemigrations {APP_NAME}')
    run_command(f'"{venv_python}" manage.py migrate')

    populate_code = """
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_final.settings')
django.setup()
from django.contrib.auth.models import User
from academy.models import Course, Module, Lesson, Quiz, Question, Answer, Profile

# 1. Admin y Profesor
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@lms.com', 'admin123')
    Profile.objects.filter(user=admin).update(role='teacher', bio='Director del LMS')

u_admin = User.objects.get(username='admin')

# 2. Curso con Examen
c = Course.objects.create(title="Robótica con ESP32", slug="robotica-esp32", description="Controla brazos robóticos.", instructor=u_admin, price=50)
m = Module.objects.create(course=c, title="Fundamentos de Electrónica", order=1)
l = Lesson.objects.create(module=m, title="Qué es un Microcontrolador", order=1)

# Crear Examen Real
q = Quiz.objects.create(module=m, title="Test de Conocimientos Básicos", pass_mark=50)

# Pregunta 1
p1 = Question.objects.create(quiz=q, text="¿Cuál es el voltaje lógico del ESP32?")
Answer.objects.create(question=p1, text="3.3V", is_correct=True)
Answer.objects.create(question=p1, text="5V", is_correct=False)
Answer.objects.create(question=p1, text="12V", is_correct=False)

# Pregunta 2
p2 = Question.objects.create(quiz=q, text="¿Qué significa GPIO?")
Answer.objects.create(question=p2, text="General Purpose Input Output", is_correct=True)
Answer.objects.create(question=p2, text="Global Position Input Output", is_correct=False)

print("Datos generados. Usuario: admin / admin123")
"""
    create_file("populate_final.py", populate_code)
    run_command(f'"{venv_python}" populate_final.py')

    print("\n=== ¡BACKEND 100% LISTO! ===")
    print(f"Ejecuta: {venv_python} manage.py runserver")
    print("Login Admin: http://127.0.0.1:8000/admin/")
    print("API Cursos: http://127.0.0.1:8000/api/courses/")
    print("API Usuario Actual: http://127.0.0.1:8000/api/me/")

if __name__ == "__main__":
    main()