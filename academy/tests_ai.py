from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from academy.views.ai_generator import AICourseGeneratorView
from academy.models import Course, Module, Lesson, Quiz, Question

class AICourseGeneratorTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='teacher', password='password')
        # Setup specific profile if needed, but the generator only uses user for ownership

    def test_create_db_objects(self):
        """Test parsing JSON and creating DB objects."""
        view = AICourseGeneratorView()

        mock_data = {
            "title": "Test AI Course",
            "description": "Desc",
            "short_description": "Short",
            "modules": [
                {
                    "title": "Mod 1",
                    "lessons": [
                        {"title": "L1", "type": "article", "content": "Content", "duration": 5}
                    ]
                }
            ],
            "quiz": {
                "title": "Quiz 1",
                "questions": [
                    {
                        "text": "Q1",
                        "type": "single_choice",
                        "answers": [{"text": "A1", "correct": True}]
                    }
                ]
            }
        }

        course = view._create_db_objects(mock_data, self.user, 'beginner')

        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(course.title, "Test AI Course")
        self.assertEqual(course.modules.count(), 2) # Mod 1 + Final Exam Module

        # Check Lesson
        lesson = Lesson.objects.first()
        self.assertEqual(lesson.title, "L1")

        # Check Quiz
        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(course.instructor, self.user)
