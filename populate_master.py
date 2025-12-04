import os
import django
from django.utils.text import slugify

# 1. Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_final.settings')
django.setup()

from django.contrib.auth.models import User
from academy.models import (
    Profile, Category, Course, Module, Lesson, 
    Quiz, Question, Answer, HeroSlide, AnnouncementCard, CertificationCard
)

def create_quiz(module, title, questions_data):
    """ Crea un examen con preguntas y respuestas para un módulo """
    quiz = Quiz.objects.create(
        module=module,
        title=title,
        description="Evaluación de conocimientos fundamentales del módulo.",
        pass_mark=70,
        randomize_questions=True,
        questions_to_show=len(questions_data)
    )
    
    for i, q_data in enumerate(questions_data, 1):
        q = Question.objects.create(
            quiz=quiz,
            text=q_data['text'],
            question_type='single_choice',
            points=20.0 / len(questions_data), # Calcula puntos para sumar 20
            order=i
        )
        for ans_text, is_correct in q_data['answers']:
            Answer.objects.create(question=q, text=ans_text, is_correct=is_correct)
            
    print(f"    - [Examen] '{title}' creado con {len(questions_data)} preguntas.")

def populate_master():
    print("=== GENERANDO SOLO LOS 2 CURSOS SOLICITADOS (OFFICE & IA CON GEMINI) ===")

    # ---------------------------------------------------------
    # 1. INSTRUCTOR
    # ---------------------------------------------------------
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@lms.com', 'admin123')
        Profile.objects.create(user=admin, role='teacher', bio='Instructor Principal LMS')
    else:
        admin = User.objects.get(username='admin')
        if not hasattr(admin, 'profile'):
            Profile.objects.create(user=admin, role='teacher')
    
    print(f"-> Instructor asignado: {admin.username}")

    # ---------------------------------------------------------
    # 2. LIMPIEZA DE CMS (Para que solo se vea lo nuevo)
    # ---------------------------------------------------------
    HeroSlide.objects.all().delete()
    AnnouncementCard.objects.all().delete()
    CertificationCard.objects.all().delete()
    print("-> CMS Limpiado (Slides y Anuncios anteriores eliminados).")

    # ---------------------------------------------------------
    # 3. CATEGORÍAS
    # ---------------------------------------------------------
    cat_office, _ = Category.objects.get_or_create(name="Ofimática y Productividad", defaults={'slug': 'ofimatica', 'icon': 'fas fa-briefcase'})
    cat_design, _ = Category.objects.get_or_create(name="Diseño e Innovación", defaults={'slug': 'diseno', 'icon': 'fas fa-pen-nib'})

    # ==============================================================================
    # CURSO 1: MICROSOFT OFFICE 365 (COMPLETO)
    # ==============================================================================
    course_office, created = Course.objects.get_or_create(
        title="Microsoft Office 365: Nivel Básico",
        defaults={
            'slug': 'office-365-basico-completo',
            'category': cat_office,
            'instructor': admin,
            'description': """
                <p>Domina las herramientas esenciales del mundo laboral con Office 365.</p>
                <p>Este curso integral cubre las 4 aplicaciones fundamentales:</p>
                <ul>
                    <li><strong>Word:</strong> Creación de documentos profesionales.</li>
                    <li><strong>Excel:</strong> Hojas de cálculo y fórmulas desde cero.</li>
                    <li><strong>PowerPoint:</strong> Presentaciones de impacto.</li>
                    <li><strong>Access:</strong> Gestión de bases de datos.</li>
                </ul>
            """,
            'short_description': 'El curso definitivo de Office. Domina Word, Excel, PowerPoint y Access paso a paso.',
            'price': 120.00,
            'level': 'beginner',
            'status': 'published',
            'learning_objectives': "- Redactar documentos en Word\n- Crear fórmulas en Excel\n- Diseñar slides en PowerPoint\n- Gestionar datos en Access",
            'requirements': "- PC con Windows\n- Microsoft Office instalado"
        }
    )
    print(f"\n-> Curso 1 Creado: {course_office.title}")

    if created:
        # --- MÓDULO 1: WORD ---
        m1 = Module.objects.create(course=course_office, title="Módulo 1: Microsoft Word", order=1)
        Lesson.objects.create(module=m1, title="La Interfaz de Word y Configuración", duration=15, order=1, content="Cinta de opciones y configuración de página.")
        Lesson.objects.create(module=m1, title="Formato de Texto y Estilos", duration=20, order=2, content="Fuentes, párrafos y uso de estilos rápidos.")
        Lesson.objects.create(module=m1, title="Tablas e Imágenes", duration=25, order=3, content="Insertar y manipular objetos visuales.")
        
        create_quiz(m1, "Quiz de Word", [
            {'text': "¿Atajo para guardar un documento?", 'answers': [('Ctrl + G', True), ('Ctrl + P', False)]},
            {'text': "¿Herramienta para alinear texto a ambos márgenes?", 'answers': [('Justificar', True), ('Centrar', False)]}
        ])

        # --- MÓDULO 2: EXCEL ---
        m2 = Module.objects.create(course=course_office, title="Módulo 2: Microsoft Excel", order=2)
        Lesson.objects.create(module=m2, title="Filas, Columnas y Celdas", duration=15, order=1, content="Navegación básica en hojas de cálculo.")
        Lesson.objects.create(module=m2, title="Fórmulas Básicas (Suma, Promedio)", duration=30, order=2, content="Operaciones matemáticas esenciales.")
        Lesson.objects.create(module=m2, title="Gráficos Básicos", duration=20, order=3, content="Visualización de datos simple.")

        create_quiz(m2, "Quiz de Excel", [
            {'text': "¿Con qué signo inicia una fórmula?", 'answers': [('=', True), ('#', False)]},
            {'text': "La intersección de fila y columna es:", 'answers': [('Celda', True), ('Rango', False)]}
        ])

        # --- MÓDULO 3: POWERPOINT ---
        m3 = Module.objects.create(course=course_office, title="Módulo 3: Microsoft PowerPoint", order=3)
        Lesson.objects.create(module=m3, title="Creación de Diapositivas", duration=20, order=1, content="Estructura y diseño básico.")
        Lesson.objects.create(module=m3, title="Animaciones y Transiciones", duration=25, order=2, content="Dar vida a la presentación.")

        create_quiz(m3, "Quiz de PowerPoint", [
            {'text': "¿Tecla para iniciar presentación?", 'answers': [('F5', True), ('Esc', False)]},
            {'text': "¿Qué es una transición?", 'answers': [('Efecto entre diapositivas', True), ('Movimiento de un objeto', False)]}
        ])

        # --- MÓDULO 4: ACCESS ---
        m4 = Module.objects.create(course=course_office, title="Módulo 4: Microsoft Access", order=4)
        Lesson.objects.create(module=m4, title="Conceptos de Base de Datos", duration=20, order=1, content="Tablas, campos y registros.")
        Lesson.objects.create(module=m4, title="Creación de Tablas y Formularios", duration=35, order=2, content="Interfaz de usuario para datos.")

        create_quiz(m4, "Quiz de Access", [
            {'text': "¿Dónde se guardan los datos en Access?", 'answers': [('Tablas', True), ('Formularios', False)]},
            {'text': "¿Qué es un campo?", 'answers': [('Una columna de información', True), ('Una fila de datos', False)]}
        ])

    # ==============================================================================
    # CURSO 2: IA EN DISEÑO GRÁFICO (CON GOOGLE GEMINI)
    # ==============================================================================
    course_ai, created = Course.objects.get_or_create(
        title="Inteligencia Artificial en Diseño Gráfico",
        defaults={
            'slug': 'ia-diseno-gemini',
            'category': cat_design,
            'instructor': admin,
            'description': """
                <p>Descubre cómo revolucionar tu proceso creativo utilizando la potencia de <strong>Google Gemini</strong> y otras herramientas de IA.</p>
                <p>En este curso aprenderás a:</p>
                <ul>
                    <li>Usar <strong>Gemini</strong> para generar ideas, conceptos y textos creativos (Copywriting).</li>
                    <li>Crear prompts efectivos para generación de imágenes (Imagen 3 / Midjourney).</li>
                    <li>Integrar IA en Adobe Photoshop y flujos de trabajo de diseño.</li>
                </ul>
            """,
            'short_description': 'Potencia tu creatividad con Google Gemini. Aprende a generar conceptos, textos e imágenes con IA.',
            'price': 90.00,
            'level': 'beginner',
            'status': 'published',
            'learning_objectives': "- Dominar Google Gemini para brainstorming\n- Ingeniería de Prompts\n- Generación de Imágenes con IA\n- Ética en el diseño con IA",
            'requirements': "- Cuenta de Google (para Gemini)\n- Nociones básicas de diseño"
        }
    )
    print(f"\n-> Curso 2 Creado: {course_ai.title}")

    if created:
        # --- MÓDULO 1: FUNDAMENTOS Y GEMINI ---
        m1 = Module.objects.create(course=course_ai, title="Introducción a la IA Generativa con Gemini", order=1)
        Lesson.objects.create(module=m1, title="¿Qué es Google Gemini?", duration=15, order=1, content="Introducción al modelo multimodal de Google.")
        Lesson.objects.create(module=m1, title="Brainstorming Creativo", duration=20, order=2, content="Usando Gemini para generar lluvias de ideas y conceptos visuales.")
        Lesson.objects.create(module=m1, title="Copywriting para Diseñadores", duration=20, order=3, content="Creación de textos publicitarios y slogans con Gemini.")

        create_quiz(m1, "Quiz: Fundamentos de Gemini", [
            {'text': "¿Qué tipo de modelo es Gemini?", 'answers': [('Multimodal (Texto, Imagen, Video)', True), ('Solo texto', False)]},
            {'text': "¿Para qué sirve el prompting?", 'answers': [('Dar instrucciones a la IA', True), ('Editar fotos', False)]}
        ])

        # --- MÓDULO 2: GENERACIÓN DE IMÁGENES ---
        m2 = Module.objects.create(course=course_ai, title="Generación de Imágenes (Imagen 3 y Otros)", order=2)
        Lesson.objects.create(module=m2, title="Ingeniería de Prompts Visuales", duration=25, order=1, content="Cómo describir estilos, iluminación y composición a la IA.")
        Lesson.objects.create(module=m2, title="Herramientas de Google: ImageFX", duration=20, order=2, content="Usando la tecnología de Google Imagen para crear assets.")
        
        create_quiz(m2, "Quiz: Generación Visual", [
            {'text': "¿Qué elemento es clave en un prompt visual?", 'answers': [('El estilo artístico', True), ('La velocidad de internet', False)]},
            {'text': "¿Qué es ImageFX?", 'answers': [('Herramienta de generación de imágenes de Google', True), ('Un editor de video', False)]}
        ])

        # --- MÓDULO 3: EDICIÓN Y FLUJO DE TRABAJO ---
        m3 = Module.objects.create(course=course_ai, title="Flujo de Trabajo Híbrido", order=3)
        Lesson.objects.create(module=m3, title="De la IA al PSD", duration=30, order=1, content="Incorporando assets generados en Photoshop.")
        Lesson.objects.create(module=m3, title="Vectorización y Acabado", duration=25, order=2, content="Transformando ideas de IA en vectores editables.")

    # ---------------------------------------------------------
    # 4. CONFIGURACIÓN DEL HOME (SLIDES Y BANNERS)
    # ---------------------------------------------------------
    print("\n-> Configurando Home Page...")
    
    # Slides
    HeroSlide.objects.create(
        title='Domina <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">Office 365</span>',
        description='El estándar de la industria. Aprende Excel, Word, PPT y Access.',
        style='business',
        btn1_text='Ver Curso',
        btn1_url=f'/course/{course_office.slug}/',
        is_active=True,
        order=1
    )
    HeroSlide.objects.create(
        title='Diseña con <span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">Google Gemini</span>',
        description='Potencia tu creatividad usando la Inteligencia Artificial más avanzada de Google.',
        style='new',
        btn1_text='Ver Curso',
        btn1_url=f'/course/{course_ai.slug}/',
        is_active=True,
        order=2
    )

    # Anuncios (Cards)
    AnnouncementCard.objects.create(
        title="Nuevo: Office 365 Completo",
        description="Desde lo básico hasta Access. Todo en un solo curso.",
        btn_text="Inscribirme",
        btn_url=f"/course/{course_office.slug}/",
        style="primary",
        order=1
    )
    AnnouncementCard.objects.create(
        title="IA con Gemini para Creativos",
        description="Aprende a usar la IA de Google en tu flujo de diseño.",
        btn_text="Explorar",
        btn_url=f"/course/{course_ai.slug}/",
        style="dark",
        order=2
    )
    
    # Certificaciones (Ejemplos visuales en el home)
    CertificationCard.objects.create(title="Office Specialist", provider="Microsoft", style="blue", order=1)
    CertificationCard.objects.create(title="AI Creative", provider="Google Cloud", style="green", order=2)

    print("\n=== ¡POBLACIÓN FINALIZADA CON ÉXITO! ===")
    print("Recuerda entrar al Panel de Instructor para subir tus videos a las lecciones.")

if __name__ == '__main__':
    populate_master()