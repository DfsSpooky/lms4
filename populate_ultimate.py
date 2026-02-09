import os
import django
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta

# 1. Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_final.settings')
django.setup()

from django.contrib.auth.models import User
from academy.models import (
    Profile, Category, Course, Module, Lesson, 
    Quiz, Question, Answer, HeroSlide, CertificationCard, AnnouncementCard,
    Institution, Event, EventSession  # <--- IMPORTANTE: Agregamos Event y EventSession
)

def populate():
    print("🚀 INICIANDO POBLACIÓN 'ULTIMATE' (ACTUALIZADO CON ORGANIZADOR)...")

    # ---------------------------------------------------------
    # 1. USUARIOS Y PERFILES
    # ---------------------------------------------------------
    print("--> [1/7] Gestionando usuarios...")
    
    # --- ADMIN / INSTRUCTOR ---
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@lms.com', 'admin123')
        admin.first_name = "Admin"
        admin.last_name = "Principal"
        admin.save()
    else:
        admin = User.objects.get(username='admin')

    # Actualizar perfil Admin
    if hasattr(admin, 'profile'):
        profile = admin.profile
    else:
        profile = Profile.objects.create(user=admin)
    profile.role = 'teacher'
    profile.bio = 'Director Académico y experto en tecnología educativa.'
    profile.save()

    # --- ORGANIZADOR DE EVENTOS (NUEVO) ---
    if not User.objects.filter(username='organizador').exists():
        org_user = User.objects.create_user('organizador', 'org@lms.com', 'organizador123')
        org_user.first_name = "Eventos"
        org_user.last_name = "Corporativos"
        org_user.save()
        print("    + Usuario 'organizador' creado (Pass: organizador123)")
    else:
        org_user = User.objects.get(username='organizador')

    # Asegurar rol de organizador
    if hasattr(org_user, 'profile'):
        org_profile = org_user.profile
    else:
        org_profile = Profile.objects.create(user=org_user)
    org_profile.role = 'organizer'
    org_profile.bio = 'Especialista en gestión de conferencias tecnológicas.'
    org_profile.save()

    # ---------------------------------------------------------
    # 2. INSTITUCIONES
    # ---------------------------------------------------------
    print("--> [2/7] Creando Instituciones...")
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
    print("--> [3/7] Creando Categorías...")
    categories = {
        'Oficina': {'name': 'Productividad y Oficina', 'icon': 'fas fa-briefcase'},
        'Diseño': {'name': 'Diseño y Creatividad', 'icon': 'fas fa-palette'},
        'IA': {'name': 'Inteligencia Artificial', 'icon': 'fas fa-robot'},
        'Eventos': {'name': 'Gestión y Liderazgo', 'icon': 'fas fa-users'}, # Nueva categoría útil para eventos
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
    print("--> [4/7] Creando Curso Office 365...")
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
                <p>Domina las herramientas más demandadas en el entorno corporativo.</p>
                <ul>
                    <li><strong>Excel:</strong> Tablas dinámicas y Dashboards.</li>
                    <li><strong>Word:</strong> Documentos maestros.</li>
                </ul>
            """,
            'short_description': 'Domina Excel, Word y PowerPoint a nivel experto.',
            'learning_objectives': "- Crear Dashboards en Excel\n- Automatizar correos",
            'requirements': "- PC con Windows\n- Office instalado"
        }
    )

    if created:
        m1 = Module.objects.create(course=c_office, title="Excel: De Datos a Información", order=1)
        Lesson.objects.create(module=m1, title="Lógica de Funciones", duration=15, order=1, content="Aprende SI, Y, O.", lesson_type='video')
        
        q1 = Quiz.objects.create(module=m1, title="Evaluación de Excel", pass_mark=80)
        que1 = Question.objects.create(quiz=q1, text="¿Herramienta para resumir datos?", points=5)
        Answer.objects.create(question=que1, text="Tablas Dinámicas", is_correct=True)
        Answer.objects.create(question=que1, text="Filtros", is_correct=False)

    # ---------------------------------------------------------
    # 5. CURSO: IA EN DISEÑO
    # ---------------------------------------------------------
    print("--> [5/7] Creando Curso IA Generativa...")
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
            'description': "<p>Aprende Midjourney y DALL-E 3.</p>",
            'short_description': 'Integra IA en tu flujo creativo.',
            'learning_objectives': "- Prompt Engineering\n- Inpainting",
            'requirements': "- Cuenta de Discord"
        }
    )

    if created:
        m_ai_1 = Module.objects.create(course=c_ai, title="Fundamentos", order=1)
        Lesson.objects.create(module=m_ai_1, title="Prompts", duration=20, order=1, content="Texto a imagen.", lesson_type='article')

    # ---------------------------------------------------------
    # 6. EVENTOS Y SESIONES (NUEVO)
    # ---------------------------------------------------------
    print("--> [6/7] Creando Evento del Organizador...")
    
    # Fechas futuras para que el evento esté activo
    event_start = timezone.now() + timedelta(days=20)
    event_end = event_start + timedelta(days=2)

    tech_event, created = Event.objects.get_or_create(
        slug='startups-summit-2025',
        defaults={
            'organizer': org_user,  # Asignado al nuevo usuario organizador
            'title': 'Startups Summit 2025: Innovación Latam',
            'description': """
                <p>El encuentro definitivo para fundadores, inversores y entusiastas de la tecnología.</p>
                <p>Dos días de conferencias, rondas de inversión y networking de alto nivel en el corazón de la ciudad.</p>
            """,
            'start_date': event_start,
            'end_date': event_end,
            'location': 'Centro de Convenciones, Lima',
            'capacity': 300,
            'price': 199.00,
            'is_active': True
        }
    )

    if created:
        print(f"    + Evento creado: {tech_event.title}")
        # Crear Agenda
        EventSession.objects.create(
            event=tech_event,
            title="Acreditación y Networking Inicial",
            start_time=event_start.replace(hour=8, minute=30),
            end_time=event_start.replace(hour=9, minute=30),
            session_type='networking',
            room='Lobby Principal'
        )
        EventSession.objects.create(
            event=tech_event,
            title="Keynote: El futuro del Venture Capital",
            start_time=event_start.replace(hour=9, minute=30),
            end_time=event_start.replace(hour=11, minute=0),
            session_type='lecture',
            room='Auditorio A',
            speaker=admin # El admin también puede ser speaker
        )
        EventSession.objects.create(
            event=tech_event,
            title="Workshop: Pitch Deck Perfecto",
            start_time=event_start.replace(hour=11, minute=30),
            end_time=event_start.replace(hour=13, minute=0),
            session_type='workshop',
            room='Sala B'
        )
    else:
        print(f"    . El evento '{tech_event.title}' ya existía.")

    # ---------------------------------------------------------
    # 7. HERO SLIDES & CMS
    # ---------------------------------------------------------
    print("--> [7/7] Generando Hero Slides y Anuncios...")
    
    HeroSlide.objects.all().delete()

    # SLIDE 1: IA
    HeroSlide.objects.create(
        title='Diseña con <span class="text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-400 via-purple-400 to-indigo-400">Inteligencia Artificial</span>',
        description='Descubre cómo Midjourney y Firefly pueden multiplicar tu creatividad.',
        style='new', 
        tag_text='Tendencia 2025',
        btn1_text='Ver Curso',
        btn1_url=f'/course/{c_ai.slug}/',
        order=1,
        is_active=True
    )

    # SLIDE 2: EVENTO (Promocionamos el evento creado)
    HeroSlide.objects.create(
        title='Asiste al <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">Startups Summit 2025</span>',
        description='Conecta con los líderes del ecosistema emprendedor. Entradas ya a la venta.',
        style='business',
        tag_text='Evento Presencial',
        btn1_text='Comprar Entrada',
        btn1_url=f'/events/{tech_event.slug}/', # Enlace al detalle del evento
        order=2,
        is_active=True
    )

    # Anuncios y Certificaciones (Limpiar y recrear)
    AnnouncementCard.objects.all().delete()
    AnnouncementCard.objects.create(title="Oferta Flash", description="50% DCTO en cursos.", btn_text="Ver", btn_url="/courses/", style="gradient", order=1)
    
    CertificationCard.objects.all().delete()
    CertificationCard.objects.create(title="Experto en Excel", provider="Microsoft", style="green", rating=4.9, order=1)
    CertificationCard.objects.create(title="AI Artist", provider="Adobe", style="indigo", rating=5.0, order=2)

    print("\n✅ ¡POBLACIÓN FINALIZADA CON ÉXITO!")
    print("--> Usuario Organizador: organizador / organizador123")
    print("--> Evento asignado: Startups Summit 2025")

if __name__ == '__main__':
    populate()