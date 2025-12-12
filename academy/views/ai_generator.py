from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.contrib import messages
from django.http import JsonResponse
from django.utils.text import slugify
import json
import random
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

        # --- MOCK AI SERVICE ---
        # In a real scenario, this would call OpenAI/Gemini API
        course = self.generate_mock_course(topic, level, request.user)
        
        messages.success(request, f"¡Curso '{course.title}' generado exitosamente con IA!")
        return redirect('academy:course_content', slug=course.slug)

    def generate_mock_course(self, topic, level, user):
        """
        Simulates AI generation logic.
        Creates a Course structure with Modules, Lessons, and a Quiz.
        """
        
        # 1. Create Course
        titles = [
            f"Mastering {topic}: From Zero to Hero",
            f"{topic} Fundamentals",
            f"Advanced {topic} Strategies",
            f"The Complete {topic} Bootcamp"
        ]
        
        course_title = random.choice(titles)
        slug = slugify(course_title)
        
        # Unique slug check
        if Course.objects.filter(slug=slug).exists():
            slug = f"{slug}-{random.randint(100, 999)}"

        course = Course.objects.create(
            title=course_title,
            slug=slug,
            description=f"Un curso completo generado automáticamente sobre {topic}. Aprenderás los fundamentos y técnicas avanzadas.",
            short_description=f"Aprende {topic} de manera rápida y efectiva.",
            level=level,
            instructor=user,
            status='draft', # Start as draft for review
            price=29.99
        )

        # 2. Create Modules & Lessons
        modules_structure = [
            ("Introducción", ["¿Qué es esto?", "Historia y Contexto", "Configuración Inicial"]),
            ("Conceptos Clave", ["Fundamentos Teóricos", "Mejores Prácticas", "Errores Comunes"]),
            ("Aplicación Práctica", ["Caso de Uso Real", "Ejercicio Paso a Paso", "Proyecto Final"]),
            ("Conclusión", ["Próximos Pasos", "Recursos Adicionales"])
        ]

        for i, (mod_title, lessons) in enumerate(modules_structure, 1):
            module = Module.objects.create(course=course, title=f"{mod_title}: {topic}", order=i)
            
            for j, lesson_title in enumerate(lessons, 1):
                lesson_type = 'video' if j % 2 != 0 else 'article' # Alternate types
                Lesson.objects.create(
                    module=module,
                    title=lesson_title,
                    order=j,
                    lesson_type=lesson_type,
                    content=f"<p>Contenido generado automáticamente para la lección: <strong>{lesson_title}</strong>.</p><p>Aquí la IA explicaría detalladamente {topic}.</p>",
                    duration=random.randint(5, 20)
                )

        # 3. Create a Quiz
        final_module = Module.objects.create(course=course, title="Evaluación Final", order=5)
        quiz = Quiz.objects.create(
            module=final_module,
            title=f"Examen de {topic}",
            description="Demuestra lo que has aprendido.",
            pass_mark=70,
            duration=30
        )

        # Add mock questions
        q1 = Question.objects.create(
            quiz=quiz, 
            text=f"¿Cuál es el principal beneficio de {topic}?", 
            question_type='single_choice',
            points=10
        )
        Answer.objects.create(question=q1, text="Mayor eficiencia", is_correct=True)
        Answer.objects.create(question=q1, text="Más complejidad", is_correct=False)
        
        q2 = Question.objects.create(
            quiz=quiz,
            text=f"Es {topic} una tecnología obsoleta?",
            question_type='true_false',
            points=10
        )
        Answer.objects.create(question=q2, text="Falso", is_correct=True)
        Answer.objects.create(question=q2, text="Verdadero", is_correct=False)

        return course
