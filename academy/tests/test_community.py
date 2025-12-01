from django.test import TestCase
from django.contrib.auth import get_user_model
from academy.models import Course, Module, Lesson, LessonComment, ForumTopic, ForumReply, Notification, LessonProgress

User = get_user_model()

class CommunitySignalsTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='student', password='password')
        self.teacher = User.objects.create_user(username='teacher', password='password')

        # Setup Course Structure
        self.course = Course.objects.create(title="Test Course", instructor=self.teacher, price=100)
        self.module = Module.objects.create(course=self.course, title="Module 1")
        # Ensure lesson_type is assignment for the grading test
        self.lesson_assignment = Lesson.objects.create(module=self.module, title="Assignment 1", order=1, lesson_type='assignment')
        self.lesson = Lesson.objects.create(module=self.module, title="Lesson 1", order=2)

    def test_notification_on_comment_reply(self):
        # 1. Student comments on a lesson
        comment = LessonComment.objects.create(lesson=self.lesson, user=self.student, content="I have a question")

        # 2. Teacher replies
        reply = LessonComment.objects.create(lesson=self.lesson, user=self.teacher, content="Here is the answer", parent=comment)

        # 3. Check notification for student
        # Signal uses 'reply' type
        self.assertTrue(Notification.objects.filter(user=self.student, notification_type='reply').exists())
        notif = Notification.objects.filter(user=self.student, notification_type='reply').latest('created_at')
        self.assertIn("respondió a tu comentario", notif.message)

    def test_notification_on_forum_reply(self):
        # 1. Student creates a topic
        topic = ForumTopic.objects.create(user=self.student, title="Help", content="Need help")

        # 2. Teacher replies
        ForumReply.objects.create(topic=topic, user=self.teacher, content="Solution")

        # 3. Check notification for student
        # Signal uses 'reply' type
        self.assertTrue(Notification.objects.filter(user=self.student, notification_type='reply').exists())
        notif = Notification.objects.filter(user=self.student, notification_type='reply').latest('created_at')
        self.assertIn("respondió a tu tema", notif.message)

    def test_notification_on_assignment_grade(self):
        # 1. Student submits assignment (Progress created)
        progress = LessonProgress.objects.create(user=self.student, lesson=self.lesson_assignment, is_completed=True)

        # 2. Teacher grades it
        # Trigger post_save by updating score
        progress.score = 90
        progress.save()

        # 3. Check notification
        self.assertTrue(Notification.objects.filter(user=self.student, notification_type='grade').exists())
        notif = Notification.objects.get(user=self.student, notification_type='grade')
        self.assertIn("Tu tarea en", notif.message)
