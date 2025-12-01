import os
import django
from django.utils.text import slugify

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_final.settings')
django.setup()

from django.contrib.auth.models import User
from academy.models import (
    Course, Category, Module, Lesson, 
    Quiz, Question, Answer
)

def populate_office_course():
    print("=== CREANDO CURSO COMPLETO DE MICROSOFT OFFICE ===")

    # 1. Obtener Instructor (Admin)
    try:
        instructor = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("Error: El usuario 'admin' no existe. Ejecuta populate_final.py primero.")
        return

    # 2. Crear Categoría "Productividad"
    cat_name = "Productividad y Oficina"
    category, created = Category.objects.get_or_create(
        name=cat_name,
        defaults={'slug': slugify(cat_name), 'icon': 'fas fa-briefcase'}
    )
    if created: print(f"-> Categoría '{cat_name}' creada.")

    # 3. Crear el Curso
    course_title = "Microsoft Office 365: Nivel Básico"
    course, created = Course.objects.get_or_create(
        title=course_title,
        defaults={
            'slug': slugify(course_title),
            'category': category,
            'instructor': instructor,
            'description': """
                Domina las herramientas esenciales de oficina más utilizadas en el mundo laboral. 
                
                En este curso práctico aprenderás a:
                - Redactar documentos profesionales en Word.
                - Gestionar hojas de cálculo y fórmulas básicas en Excel.
                - Crear presentaciones de alto impacto en PowerPoint.
                
                Ideal para estudiantes, administrativos y cualquier persona que quiera mejorar su productividad digital.
            """,
            'short_description': 'Domina Word, Excel y PowerPoint desde cero. El curso esencial para el trabajo administrativo.',
            'price': 120.00,
            'level': 'beginner',
            # Nota: Recuerda subir una imagen 'office.jpg' al admin si quieres ver thumbnail
        }
    )
    
    if not created:
        print(f"El curso '{course_title}' ya existía. Se omitió la creación.")
        return

    print(f"-> Curso '{course_title}' creado.")

    # --- ESTRUCTURA DEL CONTENIDO ---

    # MÓDULO 1: MICROSOFT WORD
    m1 = Module.objects.create(course=course, title="Módulo 1: Dominando Microsoft Word", order=1)
    
    Lesson.objects.create(
        module=m1, title="Interfaz y Configuración Inicial", 
        content="Exploraremos la cinta de opciones, la barra de acceso rápido y cómo configurar tu espacio de trabajo para máxima eficiencia.", 
        duration=15, order=1, video_url="" # Aquí pondrás tu video
    )
    Lesson.objects.create(
        module=m1, title="Formato de Texto y Párrafos", 
        content="Aprende a usar estilos, fuentes, interlineado y sangrías para dar un aspecto profesional a tus documentos.", 
        duration=20, order=2, video_url=""
    )
    Lesson.objects.create(
        module=m1, title="Inserción de Tablas e Imágenes", 
        content="Mejora tus documentos visualmente insertando y manipulando objetos gráficos y tablas de datos.", 
        duration=25, order=3, video_url=""
    )

    # Examen Word
    q1 = Quiz.objects.create(module=m1, title="Quiz: Fundamentos de Word", pass_mark=70)
    que1 = Question.objects.create(quiz=q1, text="¿Qué tecla se usa para guardar rápidamente un documento?")
    Answer.objects.create(question=que1, text="Ctrl + G (o Ctrl + S)", is_correct=True)
    Answer.objects.create(question=que1, text="Ctrl + P", is_correct=False)
    Answer.objects.create(question=que1, text="Alt + F4", is_correct=False)
    
    que2 = Question.objects.create(quiz=q1, text="¿Para qué sirve la opción 'Justificar'?")
    Answer.objects.create(question=que2, text="Para alinear el texto a ambos márgenes", is_correct=True)
    Answer.objects.create(question=que2, text="Para poner el texto en negrita", is_correct=False)

    print("-> Módulo Word creado con 3 lecciones y 1 examen.")

    # MÓDULO 2: MICROSOFT EXCEL
    m2 = Module.objects.create(course=course, title="Módulo 2: Excel para Principiantes", order=2)

    Lesson.objects.create(
        module=m2, title="Celdas, Filas y Columnas", 
        content="Entendiendo la lógica de la hoja de cálculo. Tipos de datos y navegación.", 
        duration=10, order=1, video_url=""
    )
    Lesson.objects.create(
        module=m2, title="Fórmulas Básicas (SUMA, PROMEDIO)", 
        content="Deja de usar la calculadora. Aprende a automatizar cálculos simples con funciones nativas.", 
        duration=30, order=2, video_url=""
    )
    Lesson.objects.create(
        module=m2, title="Formato Condicional", 
        content="Aprende a resaltar datos importantes automáticamente basándote en reglas lógicas.", 
        duration=20, order=3, video_url=""
    )

    # Examen Excel
    q2 = Quiz.objects.create(module=m2, title="Quiz: Lógica de Excel", pass_mark=60)
    que3 = Question.objects.create(quiz=q2, text="¿Con qué símbolo debe empezar toda fórmula en Excel?")
    Answer.objects.create(question=que3, text="= (Igual)", is_correct=True)
    Answer.objects.create(question=que3, text="# (Numeral)", is_correct=False)
    Answer.objects.create(question=que3, text="$ (Dólar)", is_correct=False)

    print("-> Módulo Excel creado con 3 lecciones y 1 examen.")

    # MÓDULO 3: MICROSOFT POWERPOINT
    m3 = Module.objects.create(course=course, title="Módulo 3: Presentaciones de Impacto", order=3)

    Lesson.objects.create(
        module=m3, title="Diseño de Diapositivas", 
        content="Reglas de oro para el diseño: menos es más. Uso de plantillas vs diseño propio.", 
        duration=15, order=1, video_url=""
    )
    Lesson.objects.create(
        module=m3, title="Animaciones y Transiciones", 
        content="Cómo dar vida a tu presentación sin marear a la audiencia. Buenas prácticas de animación.", 
        duration=20, order=2, video_url=""
    )

    print("-> Módulo PowerPoint creado con 2 lecciones.")

    print("\n=== ¡LISTO! CURSO CREADO ===")
    print(f"Total: 3 Módulos, 8 Lecciones, 2 Exámenes.")
    print("Ahora entra al panel de profesor y agrega los links de video en 'Editar Contenido'.")

if __name__ == '__main__':
    populate_office_course()