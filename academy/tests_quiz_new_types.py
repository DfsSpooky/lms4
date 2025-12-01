from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Course, Category, Module, Lesson, Enrollment, Profile, Quiz, Question, Answer, QuizSubmission
import json

class QuizNewTypesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='student', password='password')
        self.instructor = User.objects.create_user(username='teacher', password='password')
        Profile.objects.filter(user=self.instructor).update(role='teacher')

        self.category = Category.objects.create(name='Test Cat')
        self.course = Course.objects.create(
            title='Test Course',
            category=self.category,
            description='Desc',
            instructor=self.instructor
        )
        self.module = Module.objects.create(course=self.course, title='Module 1')
        self.quiz = Quiz.objects.create(module=self.module, title='Test Quiz', pass_mark=50)

        # Enroll user
        Enrollment.objects.create(user=self.user, course=self.course, status='approved')

    def test_short_answer_auto_grading(self):
        q = Question.objects.create(quiz=self.quiz, text="Capital of France?", question_type='short_answer', points=10)
        Answer.objects.create(question=q, text="Paris", is_correct=True)
        Answer.objects.create(question=q, text="La ville lumiere", is_correct=True)

        self.client.login(username='student', password='password')

        # Correct answer (case insensitive)
        data = {'answers': {str(q.id): "paris "}} # Extra space to test strip()
        response = self.client.post(f'/api/progress/quiz/{self.quiz.id}/submit/', data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['score'], 100)

        # Incorrect answer
        data = {'answers': {str(q.id): "London"}}
        response = self.client.post(f'/api/progress/quiz/{self.quiz.id}/submit/', data, content_type='application/json')
        self.assertEqual(response.json()['score'], 0)

    def test_matching_grading(self):
        q = Question.objects.create(quiz=self.quiz, text="Match these", question_type='matching', points=10)
        a1 = Answer.objects.create(question=q, text="Cat", match_text="Meow")
        a2 = Answer.objects.create(question=q, text="Dog", match_text="Woof")

        self.client.login(username='student', password='password')

        # Correct submission
        # Format: { answer_id: match_text }
        answers = {
            str(a1.id): "Meow",
            str(a2.id): "Woof"
        }
        data = {'answers': {str(q.id): answers}}

        response = self.client.post(f'/api/progress/quiz/{self.quiz.id}/submit/', data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['score'], 100)

        # Partial correct (1/2) -> 50%
        answers = {
            str(a1.id): "Meow",
            str(a2.id): "Moo"
        }
        data = {'answers': {str(q.id): answers}}
        response = self.client.post(f'/api/progress/quiz/{self.quiz.id}/submit/', data, content_type='application/json')
        self.assertEqual(response.json()['score'], 50.0)

    def test_ordering_grading(self):
        q = Question.objects.create(quiz=self.quiz, text="Order 1, 2, 3", question_type='ordering', points=10)
        a1 = Answer.objects.create(question=q, text="One", order=1)
        a2 = Answer.objects.create(question=q, text="Two", order=2)
        a3 = Answer.objects.create(question=q, text="Three", order=3)

        self.client.login(username='student', password='password')

        # Correct order (sending IDs in order)
        submitted_ids = [a1.id, a2.id, a3.id]
        data = {'answers': {str(q.id): submitted_ids}}

        response = self.client.post(f'/api/progress/quiz/{self.quiz.id}/submit/', data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['score'], 100)

        # Incorrect order
        submitted_ids = [a3.id, a2.id, a1.id]
        data = {'answers': {str(q.id): submitted_ids}}
        response = self.client.post(f'/api/progress/quiz/{self.quiz.id}/submit/', data, content_type='application/json')

        # My logic for ordering was strict match for position.
        # [3, 2, 1] vs [1, 2, 3]. Position 1 match (Two == Two).
        # Score should be 1/3 * 10 = 3.333

        score = response.json()['score']
        self.assertAlmostEqual(score, 33.33, delta=1.0)
