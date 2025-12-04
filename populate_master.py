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
    Event, EventSession
)

def populate():
    print("=== INICIANDO POBLACIÓN MAESTRA CON EVENTOS ===")

    # ---------------------------------------------------------
    # 1. USUARIOS (ADMIN / INSTRUCTOR)
    # ---------------------------------------------------------
    print("--> [1/6] Gestionando usuarios...")
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@lms.com', 'admin123')
        admin.first_name = "Admin"
        admin.last_name = "User"
        admin.save()
    else:
        admin = User.objects.get(username='admin')

    if not hasattr(admin, 'profile'):
        Profile.objects.create(user=admin, role='teacher', bio='Director Maestro.')
    else:
        admin.profile.role = 'teacher'
        admin.profile.save()

    # ---------------------------------------------------------
    # 2. CATEGORÍAS
    # ---------------------------------------------------------
    print("--> [2/6] Creando categorías...")
    categories_data = [
        {'name': 'Desarrollo Web', 'icon': 'fas fa-code'},
        {'name': 'Data Science', 'icon': 'fas fa-chart-line'},
        {'name': 'Diseño UX/UI', 'icon': 'fas fa-pen-nib'},
        {'name': 'Negocios', 'icon': 'fas fa-briefcase'},
        {'name': 'Marketing', 'icon': 'fas fa-bullhorn'},
        {'name': 'Productividad y Oficina', 'icon': 'fas fa-file-word'},
    ]
    
    categories = {}
    for cat in categories_data:
        slug = slugify(cat['name'])
        c, created = Category.objects.get_or_create(
            slug=slug,
            defaults={'name': cat['name'], 'icon': cat['icon']}
        )
        categories[slug] = c

    # ---------------------------------------------------------
    # 3. CURSOS (PUBLICADOS)
    # ---------------------------------------------------------
    print("--> [3/6] Creando cursos...")
    
    # Curso Office
    office_cat = categories.get('productividad-y-oficina')
    if office_cat:
        c_office, created = Course.objects.get_or_create(
            slug='microsoft-office-365-nivel-basico',
            defaults={
                'title': "Microsoft Office 365: Nivel Básico",
                'category': office_cat,
                'instructor': admin,
                'description': "Domina Word, Excel y PowerPoint.",
                'price': 120.00,
                'level': 'beginner',
                'status': 'published' # <--- CLAVE PARA QUE APAREZCA
            }
        )
        if created:
            m = Module.objects.create(course=c_office, title="Excel Básico", order=1)
            Lesson.objects.create(module=m, title="Fórmulas", duration=10, order=1)

    # Curso Python
    web_cat = categories.get('desarrollo-web')
    if web_cat:
        c_python, created = Course.objects.get_or_create(
            slug='python-de-cero-a-experto',
            defaults={
                'title': 'Python de Cero a Experto',
                'category': web_cat,
                'instructor': admin,
                'description': 'Aprende a programar desde cero.',
                'price': 49.99,
                'level': 'beginner',
                'status': 'published'
            }
        )

    # ---------------------------------------------------------
    # 4. EVENTOS (NUEVO: AGENDAS DETALLADAS)
    # ---------------------------------------------------------
    print("--> [4/6] Creando Evento Futuro con Agenda Completa...")
    
    # Definir fechas (Próximo mes)
    today = timezone.now()
    event_start = today + timedelta(days=30) # Empieza en 30 días
    event_end = event_start + timedelta(days=1) # Dura 2 días (Día 30 y Día 31)
    
    # 4.1 Crear el Evento Padre
    tech_summit, created = Event.objects.get_or_create(
        slug='tech-summit-2025',
        defaults={
            'title': 'Tech Summit 2025: Inteligencia Artificial',
            'description': """
                El evento más importante de tecnología del año. 
                Únete a nosotros para dos días intensivos de aprendizaje, networking y talleres prácticos sobre el futuro de la IA.
                
                Incluye:
                - Acceso a todas las conferencias.
                - Material de los talleres.
                - Certificado de participación.
                - Coffee breaks y almuerzo.
            """,
            'start_date': event_start,
            'end_date': event_end,
            'location': 'Centro de Convenciones Lima',
            'capacity': 500,
            'price': 250.00,
            'is_active': True
        }
    )
    
    if not created:
        # Si ya existe, actualizamos fechas para que siempre sea futuro al correr el script
        tech_summit.start_date = event_start
        tech_summit.end_date = event_end
        tech_summit.save()
        # Limpiamos sesiones viejas para recrearlas limpias
        tech_summit.sessions.all().delete()

    print(f"    - Evento '{tech_summit.title}' creado/actualizado.")

    # 4.2 Crear Agenda (Sesiones)
    
    # --- DÍA 1: MAÑANA ---
    EventSession.objects.create(
        event=tech_summit,
        title="Registro y Bienvenida",
        description="Entrega de credenciales y kits de bienvenida.",
        start_time=event_start.replace(hour=8, minute=30),
        end_time=event_start.replace(hour=9, minute=30),
        session_type='networking',
        room="Lobby Principal"
    )
    
    EventSession.objects.create(
        event=tech_summit,
        title="Keynote: El Futuro de la IA Generativa",
        description="Charla magistral sobre cómo los LLMs están transformando la industria.",
        start_time=event_start.replace(hour=9, minute=30),
        end_time=event_start.replace(hour=11, minute=0),
        session_type='lecture',
        room="Auditorio A",
        speaker=admin # Usamos al admin como speaker por defecto
    )

    EventSession.objects.create(
        event=tech_summit,
        title="Coffee Break",
        description="Espacio para networking y refrigerio.",
        start_time=event_start.replace(hour=11, minute=0),
        end_time=event_start.replace(hour=11, minute=30),
        session_type='break',
        room="Terraza"
    )

    EventSession.objects.create(
        event=tech_summit,
        title="Taller: Creando tu primer Chatbot",
        description="Taller práctico. Traer laptop.",
        start_time=event_start.replace(hour=11, minute=30),
        end_time=event_start.replace(hour=13, minute=0),
        session_type='workshop',
        room="Laboratorio 1",
        speaker=admin
    )

    # --- DÍA 1: TARDE ---
    EventSession.objects.create(
        event=tech_summit,
        title="Almuerzo Ejecutivo",
        description="Almuerzo incluido para todos los asistentes.",
        start_time=event_start.replace(hour=13, minute=0),
        end_time=event_start.replace(hour=14, minute=30),
        session_type='break',
        room="Comedor Central"
    )

    EventSession.objects.create(
        event=tech_summit,
        title="Panel: Ética en la IA",
        description="Debate con expertos sobre los límites de la tecnología.",
        start_time=event_start.replace(hour=15, minute=0),
        end_time=event_start.replace(hour=16, minute=30),
        session_type='lecture',
        room="Auditorio B"
    )

    # --- DÍA 2: MAÑANA (Solo un ejemplo rápido) ---
    day_2 = event_start + timedelta(days=1)
    
    EventSession.objects.create(
        event=tech_summit,
        title="Workshop Avanzado: Fine-Tuning",
        description="Aprende a entrenar tus propios modelos.",
        start_time=day_2.replace(hour=10, minute=0),
        end_time=day_2.replace(hour=13, minute=0),
        session_type='workshop',
        room="Laboratorio 2",
        speaker=admin
    )

    print("    - Agenda detallada (Mañana/Tarde/Día 2) generada.")

    # ---------------------------------------------------------
    # 5. CONTENIDO DEL HOME (CMS)
    # ---------------------------------------------------------
    print("--> [5/6] Configurando CMS (Slides y Banners)...")
    
    AnnouncementCard.objects.all().delete()
    AnnouncementCard.objects.create(
        title="LMS Plus: Acceso Ilimitado",
        description="Suscripción anual con descuento.",
        btn_text="Ver Oferta", btn_url="/plus/",
        style="primary", order=1, is_active=True
    )
    
    HeroSlide.objects.get_or_create(
        title='Aprende el Futuro',
        defaults={'style': 'new', 'is_active': True, 'order': 1}
    )

    print("\n=== ¡POBLACIÓN MAESTRA COMPLETADA! ===")
    print(f"Evento creado: {tech_summit.title}")
    print(f"Fechas: {event_start.strftime('%d/%m')} - {event_end.strftime('%d/%m')}")
    print("Los cursos ahora están publicados y visibles.")

if __name__ == '__main__':
    populate()