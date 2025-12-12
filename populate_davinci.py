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
    print("🎬 Iniciando script de población para Curso DaVinci Resolve...")

    # --- 1. PREPARACIÓN DE DATOS ---
    
    # Instructor
    instructor = User.objects.filter(is_superuser=True).first()
    if not instructor:
        instructor = User.objects.create_superuser('admin_video', 'video@example.com', 'admin123')

    # Crear Categoría 'Edición de Video'
    category, created = Category.objects.get_or_create(
        slug='edicion-video',
        defaults={'name': 'Edición de Video y VFX', 'icon': 'fas fa-film'}
    )
    
    # Crear Institución
    institution, _ = Institution.objects.get_or_create(
        name="Blackmagic Design Training Partner",
        defaults={'website': 'https://www.blackmagicdesign.com'}
    )

    # --- 2. CREAR EL CURSO ---
    
    course_title = "DaVinci Resolve 18: De Cero a Editor Profesional"
    
    # Limpiar si existe
    Course.objects.filter(title=course_title).delete()

    course = Course.objects.create(
        title=course_title,
        slug='davinci-resolve-basico',
        category=category,
        instructor=instructor,
        institution=institution,
        description="""
        <p>Descubre por qué Hollywood utiliza DaVinci Resolve para sus grandes producciones. Este curso te enseñará el flujo de trabajo completo de postproducción en un solo software.</p>
        <p><strong>Aprenderás:</strong></p>
        <ul>
            <li>Gestión de medios y organización.</li>
            <li>Edición rápida en el módulo de Montaje (Cut Page).</li>
            <li>Corrección de color profesional (Color Grading).</li>
            <li>Mezcla básica de audio con Fairlight.</li>
        </ul>
        """,
        short_description="Aprende a editar, corregir color y renderizar videos profesionales.",
        learning_objectives="Dominar la interfaz de DaVinci Resolve.\nEntender el flujo de trabajo de Nodos.\nRealizar corrección de color primaria.\nExportar para YouTube y Cine.",
        requirements="PC/Mac con DaVinci Resolve (versión gratuita o Studio).\n8GB de RAM mínimo (16GB recomendado).",
        price=29.99,
        old_price=59.99,
        level='beginner',
        status='published',
        course_type='course',
        preview_video_url='https://www.youtube.com/watch?v=n6E8Q8Q5F5M' # Video intro oficial de Blackmagic
    )

    # --- 3. CONTENIDO DEL CURSO ---

    # ==========================================
    # MÓDULO 1: LA INTERFAZ Y MEDIOS
    # ==========================================
    m1 = Module.objects.create(course=course, title="Módulo 1: Primeros Pasos", order=1)
    
    Lesson.objects.create(
        module=m1, title="Descarga e Instalación", order=1,
        lesson_type='article', duration=10,
        content="<p>Guía paso a paso para instalar la versión gratuita desde la web oficial de Blackmagic Design.</p>"
    )
    Lesson.objects.create(
        module=m1, title="Tour por la Interfaz", order=2,
        lesson_type='video', duration=15,
        video_url="https://www.youtube.com/watch?v=63jGdX7f9Bw", 
        content="Entendiendo las pestañas: Media, Cut, Edit, Fusion, Color, Fairlight y Deliver."
    )
    Lesson.objects.create(
        module=m1, title="Importación de Medios (Media Pool)", order=3,
        lesson_type='video', duration=12,
        video_url="https://www.youtube.com/watch?v=Z1FZ1F1F1F1", # URL simulada
        content="Cómo organizar tus clips, crear Bins y usar Smart Bins."
    )

    # ==========================================
    # MÓDULO 2: EDICIÓN Y MONTAJE
    # ==========================================
    m2 = Module.objects.create(course=course, title="Módulo 2: El Arte del Corte", order=2)

    Lesson.objects.create(
        module=m2, title="Cut Page vs Edit Page", order=1,
        lesson_type='video', duration=20,
        video_url="https://www.youtube.com/watch?v=xyz123abc",
        content="Diferencias clave: ¿Cuándo usar la página de Corte rápido y cuándo la Edición tradicional?"
    )
    Lesson.objects.create(
        module=m2, title="Herramientas de Edición", order=2,
        lesson_type='video', duration=25,
        video_url="https://www.youtube.com/watch?v=cutclip123",
        content="Uso de la cuchilla (Blade), Trim, Ripple Edit y atajos de teclado esenciales."
    )

    # >> Quiz de Edición
    q1 = Quiz.objects.create(
        module=m2, title="Quiz de Edición Básica", 
        description="Pon a prueba tus conocimientos sobre herramientas de corte.",
        pass_mark=70, duration=10
    )
    ques1 = Question.objects.create(quiz=q1, text="¿Qué tecla se usa comúnmente para la herramienta 'Cuchilla' (Blade) en modo estándar?", question_type='single_choice', points=5)
    Answer.objects.create(question=ques1, text="B", is_correct=True)
    Answer.objects.create(question=ques1, text="C", is_correct=False)
    Answer.objects.create(question=ques1, text="X", is_correct=False)

    # ==========================================
    # MÓDULO 3: CORRECCIÓN DE COLOR (EL FUERTE)
    # ==========================================
    m3 = Module.objects.create(course=course, title="Módulo 3: Color Grading Profesional", order=3)

    Lesson.objects.create(
        module=m3, title="Entendiendo los Nodos", order=1,
        lesson_type='article', duration=15,
        content="""
        <h3>Nodos vs Capas</h3>
        <p>DaVinci usa un sistema de nodos. A diferencia de las capas, los nodos permiten un flujo de señal más flexible.</p>
        <p><strong>Nodo Serial:</strong> El más común, procesa la imagen en serie.</p>
        """
    )
    Lesson.objects.create(
        module=m3, title="Ruedas de Color (Lift, Gamma, Gain)", order=2,
        lesson_type='video', duration=30,
        video_url="https://www.youtube.com/watch?v=colorwheel1",
        content="Aprende a balancear tus tomas ajustando sombras, medios tonos y luces."
    )
    
    # >> Quiz de Color
    q2 = Quiz.objects.create(
        module=m3, title="Conceptos de Color",
        pass_mark=60, duration=15
    )
    ques2 = Question.objects.create(quiz=q2, text="¿Qué rueda de color afecta principalmente a las partes oscuras de la imagen?", question_type='single_choice', points=10)
    Answer.objects.create(question=ques2, text="Lift (Sombras)", is_correct=True)
    Answer.objects.create(question=ques2, text="Gamma (Medios)", is_correct=False)
    Answer.objects.create(question=ques2, text="Gain (Luces)", is_correct=False)

    # ==========================================
    # MÓDULO 4: EXPORTACIÓN
    # ==========================================
    m4 = Module.objects.create(course=course, title="Módulo 4: Entrega Final", order=4)

    Lesson.objects.create(
        module=m4, title="Página de Entrega (Deliver)", order=1,
        lesson_type='video', duration=10,
        video_url="https://www.youtube.com/watch?v=render123",
        content="Configuración de códecs (H.264, H.265) y contenedores (MP4, MOV)."
    )

    # ==========================================
    # EXAMEN FINAL
    # ==========================================
    q_final = Quiz.objects.create(
        module=m4, title="CERTIFICACIÓN DAVINCI RESOLVE", 
        description="Examen final teórico para obtener tu certificado.",
        pass_mark=80, duration=45, is_final_exam=True, randomize_questions=True
    )

    qf1 = Question.objects.create(quiz=q_final, text="¿Es posible editar audio profesionalmente dentro de DaVinci Resolve?", question_type='true_false', points=4)
    Answer.objects.create(question=qf1, text="Verdadero (usando Fairlight)", is_correct=True)
    Answer.objects.create(question=qf1, text="Falso", is_correct=False)

    qf2 = Question.objects.create(quiz=q_final, text="¿Qué formato es ideal para subir videos a YouTube?", question_type='single_choice', points=4)
    Answer.objects.create(question=qf2, text="H.264 / MP4", is_correct=True)
    Answer.objects.create(question=qf2, text="ProRes 4444 XQ", is_correct=False) # Muy pesado
    Answer.objects.create(question=qf2, text="DPX Sequence", is_correct=False)

    print("✅ Curso 'DaVinci Resolve' creado exitosamente.")

if __name__ == '__main__':
    populate()