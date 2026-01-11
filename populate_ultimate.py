import os
import django
from django.utils import timezone
from django.utils.text import slugify

# 1. Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_final.settings')
django.setup()

from django.contrib.auth.models import User
from academy.models import (
    Profile, Category, Course, Module, Lesson, 
    Quiz, Question, Answer, HeroSlide, CertificationCard, AnnouncementCard,
    Institution
)

def populate():
    print("🚀 INICIANDO POBLACIÓN 'ULTIMATE' (CORREGIDO)...")

    # ---------------------------------------------------------
    # 1. USUARIOS Y PERFILES (FIX INTEGRITY ERROR)
    # ---------------------------------------------------------
    print("--> [1/6] Gestionando usuario Admin...")
    
    # Crear o recuperar usuario admin
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@lms.com', 'admin123')
        admin.first_name = "Admin"
        admin.last_name = "Principal"
        admin.save()
    else:
        admin = User.objects.get(username='admin')

    # CORRECCIÓN: Verificar si ya tiene perfil antes de crear uno
    # La señal post_save suele crear uno automáticamente.
    if hasattr(admin, 'profile'):
        profile = admin.profile
    else:
        profile = Profile.objects.create(user=admin)
    
    # Actualizamos los datos del perfil existente
    profile.role = 'teacher'
    profile.bio = 'Director Académico y experto en tecnología educativa.'
    profile.save()

    # ---------------------------------------------------------
    # 2. INSTITUCIONES (CON DUMMY LOGOS PARA EVITAR ERROR)
    # ---------------------------------------------------------
    print("--> [2/6] Creando Instituciones...")
    # Usamos defaults con una ruta de imagen ficticia para pasar la validación de 'required'
    inst_microsoft, _ = Institution.objects.get_or_create(
        name="Microsoft Certified",
        defaults={'logo': 'institutions/default_microsoft.png'}
    )
    inst_adobe, _ = Institution.objects.get_or_create(
        name="Adobe Authorized Center",
        defaults={'logo': 'institutions/default_adobe.png'}
    )

    # ---------------------------------------------------------
    # 3. CATEGORÍAS
    # ---------------------------------------------------------
    print("--> [3/6] Creando Categorías...")
    categories = {
        'Oficina': {'name': 'Productividad y Oficina', 'icon': 'fas fa-briefcase'},
        'Diseño': {'name': 'Diseño y Creatividad', 'icon': 'fas fa-palette'},
        'IA': {'name': 'Inteligencia Artificial', 'icon': 'fas fa-robot'},
    }
    
    cats_objs = {}
    for key, data in categories.items():
        c, _ = Category.objects.get_or_create(
            slug=slugify(data['name']),
            defaults={'name': data['name'], 'icon': data['icon']}
        )
        cats_objs[key] = c

    # ---------------------------------------------------------
    # 4. CURSO: MICROSOFT OFFICE 365
    # ---------------------------------------------------------
    print("--> [4/6] Creando Curso Office 365...")
    c_office, created = Course.objects.get_or_create(
        slug='master-office-365-empresarial',
        defaults={
            'title': 'Master en Microsoft Office 365 Empresarial',
            'category': cats_objs['Oficina'],
            'instructor': admin,
            'institution': inst_microsoft,
            'level': 'intermediate',
            'status': 'published',
            'price': 149.99,
            'old_price': 299.99,
            'description': """
                <p>Domina las herramientas más demandadas en el entorno corporativo. Este curso te llevará desde los fundamentos hasta funciones avanzadas.</p>
                <ul>
                    <li><strong>Excel:</strong> Tablas dinámicas, Power Query y Dashboards.</li>
                    <li><strong>Word:</strong> Documentos maestros y automatización de correspondencia.</li>
                    <li><strong>PowerPoint:</strong> Storytelling y animaciones profesionales.</li>
                </ul>
            """,
            'short_description': 'Domina Excel, Word y PowerPoint a nivel experto. Aumenta tu productividad y destaca en tu trabajo.',
            'learning_objectives': "- Crear Dashboards en Excel\n- Automatizar correos con Word\n- Presentaciones de alto impacto",
            'requirements': "- PC con Windows o Mac\n- Microsoft Office 2019 o 365 instalado"
        }
    )

    if created:
        # Modulo Excel
        m1 = Module.objects.create(course=c_office, title="Excel: De Datos a Información", order=1)
        Lesson.objects.create(module=m1, title="Lógica de Funciones Anidadas", duration=15, order=1, content="Aprende a combinar SI, Y, O y BUSCARV para análisis complejos.", lesson_type='video')
        Lesson.objects.create(module=m1, title="Tablas Dinámicas Avanzadas", duration=25, order=2, content="Segmentación de datos y escalas de tiempo para reportes gerenciales.", lesson_type='video')
        
        # Quiz Excel
        q1 = Quiz.objects.create(module=m1, title="Evaluación de Excel", pass_mark=80)
        que1 = Question.objects.create(quiz=q1, text="¿Qué herramienta permite resumir grandes volúmenes de datos dinámicamente?", points=5)
        Answer.objects.create(question=que1, text="Tablas Dinámicas", is_correct=True)
        Answer.objects.create(question=que1, text="Formato Condicional", is_correct=False)
        Answer.objects.create(question=que1, text="Validación de Datos", is_correct=False)

        # Modulo Word
        m2 = Module.objects.create(course=c_office, title="Word: Documentos Profesionales", order=2)
        Lesson.objects.create(module=m2, title="Estilos y Tablas de Contenido", duration=12, order=1, content="Automatiza el índice de tus documentos usando estilos.", lesson_type='video')

    # ---------------------------------------------------------
    # 5. CURSO: IA EN DISEÑO
    # ---------------------------------------------------------
    print("--> [5/6] Creando Curso IA Generativa...")
    c_ai, created = Course.objects.get_or_create(
        slug='ia-generativa-para-disenadores',
        defaults={
            'title': 'Revolución Creativa: IA para Diseñadores',
            'category': cats_objs['Diseño'],
            'instructor': admin,
            'institution': inst_adobe,
            'level': 'advanced',
            'status': 'published',
            'price': 89.00,
            'old_price': 150.00,
            'course_type': 'course',
            'description': """
                <p>La Inteligencia Artificial no te reemplazará, te potenciará. Aprende a integrar <strong>Midjourney</strong>, <strong>DALL-E 3</strong> y <strong>Adobe Firefly</strong> en tu flujo de trabajo diario.</p>
                <p>Descubre cómo generar conceptos visuales en segundos, expandir imágenes con "Outpainting" y crear assets únicos para tus proyectos web y de branding.</p>
            """,
            'short_description': 'Aprende a integrar Midjourney, Stable Diffusion y Firefly en tu flujo de trabajo creativo profesional.',
            'learning_objectives': "- Prompt Engineering Avanzado\n- Inpainting y Outpainting\n- Ética y Derechos de Autor en IA",
            'requirements': "- Cuenta de Discord (Midjourney)\n- Conocimientos básicos de Photoshop"
        }
    )

    if created:
        m_ai_1 = Module.objects.create(course=c_ai, title="Fundamentos del Prompting", order=1)
        Lesson.objects.create(module=m_ai_1, title="Anatomía de un Prompt Perfecto", duration=20, order=1, content="Sujeto + Estilo + Iluminación + Parámetros.", lesson_type='article')
        Lesson.objects.create(module=m_ai_1, title="Midjourney v6: Parámetros Avanzados", duration=30, order=2, content="Domina --stylize, --weird y --chaos.", lesson_type='video')
        
        m_ai_2 = Module.objects.create(course=c_ai, title="Integración con Photoshop", order=2)
        Lesson.objects.create(module=m_ai_2, title="Generative Fill en Profundidad", duration=15, order=1, content="Cómo usar la IA de Adobe para retocar fotos.", lesson_type='video')

    # ---------------------------------------------------------
    # 6. HERO SLIDES & CMS (VISUALES DE ALTO IMPACTO)
    # ---------------------------------------------------------
    print("--> [6/6] Generando Hero Slides y Anuncios...")
    
    # Limpiamos para evitar duplicados en el slider
    HeroSlide.objects.all().delete()

    # SLIDE 1: IA (Estilo 'new' - Morado/Cyber)
    HeroSlide.objects.create(
        title='<span class="block text-white text-lg font-medium tracking-widest uppercase mb-2">Domina el Futuro</span>Diseña con <span class="text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-400 via-purple-400 to-indigo-400">Inteligencia Artificial</span>',
        description='Descubre cómo Midjourney y Firefly pueden multiplicar tu creatividad por 10. Curso definitivo ya disponible.',
        style='new', 
        tag_text='Tendencia 2025',
        btn1_text='Ver Curso de IA',
        btn1_url=f'/course/{c_ai.slug}/',
        btn2_text='Ver Trailer',
        btn2_url='#',
        order=1,
        is_active=True
    )

    # SLIDE 2: OFFICE (Estilo 'promo' - Dorado/Profesional)
    HeroSlide.objects.create(
        title='Acelera tu <span class="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-amber-500">Carrera Profesional</span>',
        description='El dominio de Office 365 es la habilidad #1 requerida por las empresas. Certifícate hoy mismo.',
        style='promo',
        tag_text='Certificación Oficial',
        btn1_text='Empezar Ahora',
        btn1_url=f'/course/{c_office.slug}/',
        order=2,
        is_active=True
    )

    # SLIDE 3: INSTITUCIONAL (Estilo 'business' - Azul)
    HeroSlide.objects.create(
        title='Capacitación para <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">Empresas Modernas</span>',
        description='Lleva a tu equipo al siguiente nivel con nuestra plataforma LMS corporativa. Reportes, seguimiento y más.',
        style='business',
        tag_text='LMS Enterprise',
        btn1_text='Contactar Ventas',
        btn1_url='/empresas/',
        order=3,
        is_active=True
    )

    # Anuncios y Certificaciones
    AnnouncementCard.objects.all().delete()
    AnnouncementCard.objects.create(
        title="Oferta Flash: 50% DCTO",
        description="Solo por 24 horas en todos los cursos de tecnología.",
        btn_text="Aprovechar",
        btn_url="/courses/?price=paid",
        style="gradient",
        order=1
    )
    AnnouncementCard.objects.create(
        title="¿Eres Instructor?",
        description="Monetiza tu conocimiento. Únete a nuestra red de mentores.",
        btn_text="Aplicar",
        btn_url="/signup/",
        style="dark",
        order=2
    )

    CertificationCard.objects.all().delete()
    CertificationCard.objects.create(title="Experto en Excel", provider="Microsoft", icon_class="fas fa-file-excel", style="green", rating=4.9, order=1)
    CertificationCard.objects.create(title="AI Artist", provider="Adobe", icon_class="fas fa-robot", style="indigo", rating=5.0, order=2)
    CertificationCard.objects.create(title="Project Management", provider="PMI", icon_class="fas fa-tasks", style="blue", rating=4.8, order=3)

    print("\n✅ ¡POBLACIÓN FINALIZADA CON ÉXITO!")
    print("El error de 'UNIQUE constraint' ha sido resuelto. ¡Disfruta tu nuevo contenido!")

if __name__ == '__main__':
    populate()