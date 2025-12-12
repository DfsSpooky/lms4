import os
import django
import random
from django.utils import timezone

# 1. Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_final.settings')
django.setup()

from django.contrib.auth.models import User
from academy.models import (
    Category, Course, Module, Lesson, 
    Quiz, Question, Answer, Institution
)

def populate():
    print("🚀 Iniciando script de población para Curso Office Básico...")

    # --- 1. PREPARACIÓN DE DATOS ---
    
    # Obtener o crear Admin/Instructor
    # Intentamos buscar al usuario 'admin', si no, creamos uno temporal
    instructor = User.objects.filter(is_superuser=True).first()
    if not instructor:
        print("⚠️ No se encontró superusuario. Creando 'admin_office'...")
        instructor = User.objects.create_superuser('admin_office', 'admin@example.com', 'admin123')

    # Crear Categoría 'Ofimática'
    category, created = Category.objects.get_or_create(
        slug='ofimatica',
        defaults={'name': 'Ofimática y Productividad', 'icon': 'fas fa-briefcase'}
    )
    
    # Crear Institución (opcional, para que se vea pro)
    institution, _ = Institution.objects.get_or_create(
        name="Microsoft Skills Academy",
        defaults={'website': 'https://www.microsoft.com'}
    )

    # --- 2. CREAR EL CURSO ---
    
    course_title = "Curso Completo de Microsoft Office 2024"
    print(f"📚 Creando curso: {course_title}")
    
    # Borrar si ya existe para no duplicar en pruebas
    Course.objects.filter(title=course_title).delete()

    course = Course.objects.create(
        title=course_title,
        slug='curso-completo-office-basico',
        category=category,
        instructor=instructor,
        institution=institution,
        description="""
        <p>Aprende a dominar las herramientas más importantes del mundo laboral. Este curso te llevará desde cero hasta un nivel competente en:</p>
        <ul>
            <li><strong>Microsoft Word:</strong> Creación y edición profesional de documentos.</li>
            <li><strong>Microsoft Excel:</strong> Fórmulas, tablas y análisis de datos.</li>
            <li><strong>Microsoft PowerPoint:</strong> Presentaciones de alto impacto.</li>
            <li><strong>Microsoft Access:</strong> Gestión básica de bases de datos.</li>
        </ul>
        <p>Ideal para estudiantes, administrativos y cualquier persona que quiera mejorar su productividad.</p>
        """,
        short_description="Domina Word, Excel, PowerPoint y Access desde cero.",
        learning_objectives="Crear documentos profesionales en Word.\nUtilizar fórmulas y gráficos en Excel.\nDiseñar presentaciones efectivas.\nGestionar bases de datos simples.",
        requirements="PC con Microsoft Office instalado (versión 2016, 2019 o 365).\nConocimientos básicos de manejo de Windows.",
        price=49.99,
        old_price=99.99,
        level='beginner',
        status='published',  # Importante para que salga en la app
        course_type='course',
        preview_video_url='https://www.youtube.com/watch?v=I444Fk5i0O8' # Video genérico de Office
    )

    # --- 3. CREAR CONTENIDO (Módulos, Lecciones y Exámenes) ---

    # ==========================================
    # MÓDULO 1: MICROSOFT WORD
    # ==========================================
    m1 = Module.objects.create(course=course, title="Módulo 1: Dominando Microsoft Word", order=1)
    
    Lesson.objects.create(
        module=m1, title="Interfaz y Primeros Pasos", order=1,
        lesson_type='video', duration=10,
        video_url="https://www.youtube.com/watch?v=S95J5BmAXpM", # Tutorial Word
        content="Exploración de la cinta de opciones, barra de estado y configuración de página."
    )
    Lesson.objects.create(
        module=m1, title="Formato de Texto y Párrafos", order=2,
        lesson_type='article', duration=15,
        content="""
        <h3>Conceptos Clave</h3>
        <p>Aprenderemos a usar negritas, cursivas, alineación y sangrías.</p>
        <p><strong>Tip:</strong> Usa estilos predefinidos para generar índices automáticos.</p>
        """
    )
    Lesson.objects.create(
        module=m1, title="Tablas e Imágenes", order=3,
        lesson_type='video', duration=12,
        video_url="https://www.youtube.com/watch?v=2K4Vb6uLg4k",
        content="Cómo insertar tablas, ajustar columnas y colocar imágenes flotantes."
    )

    # >> Quiz Word
    q1 = Quiz.objects.create(
        module=m1, title="Evaluación de Word Básico", 
        description="Demuestra lo aprendido sobre documentos.",
        pass_mark=70, duration=10, randomize_questions=True
    )
    # Preguntas
    ques1 = Question.objects.create(quiz=q1, text="¿Cuál es el atajo de teclado para Guardar un documento?", question_type='single_choice', points=5)
    Answer.objects.create(question=ques1, text="Ctrl + G (o Ctrl + S)", is_correct=True)
    Answer.objects.create(question=ques1, text="Ctrl + P", is_correct=False)
    Answer.objects.create(question=ques1, text="Alt + F4", is_correct=False)

    ques2 = Question.objects.create(quiz=q1, text="Las tablas en Word permiten realizar cálculos básicos.", question_type='true_false', points=5)
    Answer.objects.create(question=ques2, text="Verdadero", is_correct=True)
    Answer.objects.create(question=ques2, text="Falso", is_correct=False)


    # ==========================================
    # MÓDULO 2: MICROSOFT EXCEL
    # ==========================================
    m2 = Module.objects.create(course=course, title="Módulo 2: Fundamentos de Excel", order=2)

    Lesson.objects.create(
        module=m2, title="Filas, Columnas y Celdas", order=1,
        lesson_type='video', duration=15,
        video_url="https://www.youtube.com/watch?v=Zk4a31r5y6s",
        content="Entendiendo la estructura de una hoja de cálculo."
    )
    Lesson.objects.create(
        module=m2, title="Fórmulas Básicas (Suma, Promedio)", order=2,
        lesson_type='video', duration=20,
        video_url="https://www.youtube.com/watch?v=eYp5A2yO2e4",
        content="Aprende a usar =SUMA(), =PROMEDIO() y operaciones matemáticas básicas."
    )
    Lesson.objects.create(
        module=m2, title="Creación de Gráficos", order=3,
        lesson_type='article', duration=10,
        content="<p>Los gráficos permiten visualizar datos numéricos. Excel recomienda gráficos basados en tu selección.</p>"
    )

    # >> Quiz Excel
    q2 = Quiz.objects.create(
        module=m2, title="Examen Rápido de Excel",
        pass_mark=60, duration=15
    )
    ques3 = Question.objects.create(quiz=q2, text="Todas las fórmulas en Excel deben comenzar con el símbolo:", question_type='single_choice', points=10)
    Answer.objects.create(question=ques3, text="=", is_correct=True)
    Answer.objects.create(question=ques3, text="#", is_correct=False)
    Answer.objects.create(question=ques3, text="+", is_correct=False) # A veces funciona pero = es el estándar

    ques4 = Question.objects.create(quiz=q2, text="Selecciona los tipos de gráficos disponibles en Excel:", question_type='multiple_choice', points=10)
    Answer.objects.create(question=ques4, text="Barras", is_correct=True)
    Answer.objects.create(question=ques4, text="Pastel (Circular)", is_correct=True)
    Answer.objects.create(question=ques4, text="Holograma 3D", is_correct=False)


    # ==========================================
    # MÓDULO 3: MICROSOFT POWERPOINT
    # ==========================================
    m3 = Module.objects.create(course=course, title="Módulo 3: Presentaciones con PowerPoint", order=3)

    Lesson.objects.create(
        module=m3, title="Diseño de Diapositivas", order=1,
        lesson_type='video', duration=10,
        video_url="https://www.youtube.com/watch?v=XF1gXzHhQj0",
        content="Uso de temas, patrones y diseño."
    )
    Lesson.objects.create(
        module=m3, title="Animaciones y Transiciones", order=2,
        lesson_type='video', duration=12,
        video_url="https://www.youtube.com/watch?v=Cq8M6wX0y_I",
        content="Dando vida a tus presentaciones con movimiento."
    )

    # ==========================================
    # MÓDULO 4: MICROSOFT ACCESS
    # ==========================================
    m4 = Module.objects.create(course=course, title="Módulo 4: Intro a Bases de Datos (Access)", order=4)

    Lesson.objects.create(
        module=m4, title="¿Qué es una Base de Datos?", order=1,
        lesson_type='article', duration=20,
        content="<p>Conceptos de Tabla, Registro, Campo y Clave Primaria.</p>"
    )
    Lesson.objects.create(
        module=m4, title="Creando nuestra primera Tabla", order=2,
        lesson_type='video', duration=25,
        video_url="https://www.youtube.com/watch?v=C6rK0Sj0gqY",
        content="Diseño de tablas y tipos de datos en Access."
    )

    # ==========================================
    # EXAMEN FINAL
    # ==========================================
    # Agregamos el examen final al último módulo
    q_final = Quiz.objects.create(
        module=m4, title="EXAMEN FINAL CERTIFICADO", 
        description="Evaluación global de Office. Necesitas 80% para aprobar.",
        pass_mark=80, duration=30, is_final_exam=True, randomize_questions=True
    )

    # Preguntas variadas
    qf1 = Question.objects.create(quiz=q_final, text="¿Qué programa usarías para escribir una carta?", question_type='single_choice', points=4)
    Answer.objects.create(question=qf1, text="Word", is_correct=True)
    Answer.objects.create(question=qf1, text="Excel", is_correct=False)
    
    qf2 = Question.objects.create(quiz=q_final, text="¿Qué extensión de archivo usa Excel moderno?", question_type='single_choice', points=4)
    Answer.objects.create(question=qf2, text=".xlsx", is_correct=True)
    Answer.objects.create(question=qf2, text=".doc", is_correct=False)

    qf3 = Question.objects.create(quiz=q_final, text="Access es un gestor de presentaciones.", question_type='true_false', points=4)
    Answer.objects.create(question=qf3, text="Falso", is_correct=True)
    Answer.objects.create(question=qf3, text="Verdadero", is_correct=False)

    print("✅ Curso 'Office Completo' creado exitosamente con Módulos, Lecciones y Exámenes.")

if __name__ == '__main__':
    populate()