from rest_framework import serializers
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
