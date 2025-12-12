from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.contrib import messages
from django.http import JsonResponse
from django.utils.text import slugify
from django.conf import settings
import json
import random
import os
import openai
from ..models import Course, Module, Lesson, Quiz, Question, Answer

class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.profile.role == 'teacher' or self.request.user.is_superuser)

class AICourseGeneratorView(LoginRequiredMixin, TeacherRequiredMixin, generic.TemplateView):
    template_name = 'academy/course_generate_ai.html'

    def post(self, request, *args, **kwargs):
        topic = request.POST.get('topic')
        level = request.POST.get('level', 'beginner')
        
        if not topic:
            messages.error(request, "Por favor ingresa un tema para el curso.")
            return redirect('academy:ai_course_generator')

        try:
            # Check for API Key
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                # Fallback to Mock if no key (for demo/dev without keys)
                messages.warning(request, "API Key no encontrada. Usando modo simulación.")
                course = self.generate_mock_course(topic, level, request.user)
            else:
                course = self.generate_ai_course(topic, level, request.user, api_key)

            messages.success(request, f"¡Curso '{course.title}' generado exitosamente con IA!")
            return redirect('academy:course_content', slug=course.slug)

        except Exception as e:
            print(f"Error generating course: {e}")
            messages.error(request, f"Error al generar el curso: {str(e)}")
            return redirect('academy:ai_course_generator')

    def generate_ai_course(self, topic, level, user, api_key):
        client = openai.OpenAI(api_key=api_key)

        prompt = f"""
        Act as an expert curriculum designer. Create a detailed course structure for "{topic}" (Level: {level}).
        Return ONLY valid JSON with this structure:
        {{
            "title": "Engaging Course Title",
            "description": "Comprehensive course description (html allowed)",
            "short_description": "Short summary (max 300 chars)",
            "modules": [
                {{
                    "title": "Module Title",
                    "lessons": [
                        {{
                            "title": "Lesson Title",
                            "type": "article",
                            "content": "Detailed educational content in HTML format. At least 3 paragraphs.",
                            "duration": 10
                        }}
                    ]
                }}
            ],
            "quiz": {{
                "title": "Final Exam Title",
                "questions": [
                    {{
                        "text": "Question text?",
                        "type": "single_choice",
                        "answers": [
                            {{"text": "Option A", "correct": true}},
                            {{"text": "Option B", "correct": false}}
                        ]
                    }}
                ]
            }}
        }}
        Ensure the course has at least 3 modules, 3 lessons per module, and 5 quiz questions.
        """

        response = client.chat.completions.create(
            model="gpt-4o", # Or gpt-3.5-turbo
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)
        
        return self._create_db_objects(data, user, level)

    def generate_mock_course(self, topic, level, user):
        """Fallback mock generator"""
        # ... (Existing mock logic, re-implemented here or we can just reuse the previous structure logic if we wanted to keep it DRY, but for now I'll just keep the mock logic simple for fallback)
        titles = [
            f"Mastering {topic}: From Zero to Hero (Mock)",
            f"{topic} Fundamentals (Mock)",
        ]
        course_title = random.choice(titles)
        
        data = {
            "title": course_title,
            "description": f"Mock course about {topic}.",
            "short_description": f"Learn {topic} fast.",
            "modules": [
                {
                    "title": "Intro (Mock)",
                    "lessons": [
                        {"title": "Lesson 1", "type": "article", "content": "<p>Mock Content</p>", "duration": 10},
                        {"title": "Lesson 2", "type": "video", "content": "<p>Watch this</p>", "duration": 5},
                    ]
                }
            ],
            "quiz": {
                "title": f"Exam {topic}",
                "questions": [
                    {
                        "text": "Is this a mock?",
                        "type": "true_false",
                        "answers": [{"text": "True", "correct": True}, {"text": "False", "correct": False}]
                    }
                ]
            }
        }
        return self._create_db_objects(data, user, level)

    def _create_db_objects(self, data, user, level):
        slug = slugify(data['title'])
        if Course.objects.filter(slug=slug).exists():
            slug = f"{slug}-{random.randint(100, 999)}"

        course = Course.objects.create(
            title=data['title'],
            slug=slug,
            description=data['description'],
            short_description=data['short_description'],
            level=level,
            instructor=user,
            status='draft',
            price=29.99
        )

        for i, mod_data in enumerate(data.get('modules', []), 1):
            module = Module.objects.create(course=course, title=mod_data['title'], order=i)
            for j, lesson_data in enumerate(mod_data.get('lessons', []), 1):
                Lesson.objects.create(
                    module=module,
                    title=lesson_data['title'],
                    order=j,
                    lesson_type=lesson_data.get('type', 'article'),
                    content=lesson_data.get('content', ''),
                    duration=lesson_data.get('duration', 10)
                )

        if 'quiz' in data:
            q_data = data['quiz']
            final_module = Module.objects.create(course=course, title="Evaluación Final", order=99)
            quiz = Quiz.objects.create(
                module=final_module,
                title=q_data['title'],
                description="Examen generado por IA",
                pass_mark=70,
                duration=30
            )

            for k, quest in enumerate(q_data.get('questions', []), 1):
                q = Question.objects.create(
                    quiz=quiz,
                    text=quest['text'],
                    question_type=quest.get('type', 'single_choice'),
                    points=10,
                    order=k
                )
                for ans in quest.get('answers', []):
                    Answer.objects.create(
                        question=q,
                        text=ans['text'],
                        is_correct=ans['correct']
                    )

        return course
