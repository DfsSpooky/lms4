from rest_framework import serializers
from .models import *

# --- USUARIO ---
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['avatar', 'role', 'bio', 'dni', 'phone_number', 'address', 'facebook_url', 'website', 'academic_profile']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=False)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile = instance.profile

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()
        return instance

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
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'thumbnail', 'price', 'instructor_name', 'category_name', 'level', 'average_rating']

# --- FORUM ---
class ForumReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = ForumReply
        fields = ['id', 'user', 'content', 'created_at']

class ForumTopicSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    reply_count = serializers.IntegerField(source='replies.count', read_only=True)
    class Meta:
        model = ForumTopic
        fields = ['id', 'title', 'content', 'user', 'created_at', 'views', 'reply_count']

class ForumTopicCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumTopic
        fields = ['title', 'content', 'course']

# --- NOTIFICATIONS ---
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'link', 'is_read', 'notification_type', 'created_at']

class MyCourseSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'enrolled_at', 'status', 'progress_percent']

    def get_progress_percent(self, obj):
        # Calculate progress
        total_lessons = Lesson.objects.filter(module__course=obj.course).count()
        if total_lessons == 0: return 0
        completed = LessonProgress.objects.filter(user=obj.user, lesson__module__course=obj.course, is_completed=True).count()
        return int((completed / total_lessons) * 100)
