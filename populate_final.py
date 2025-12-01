import os
import django
import random
from django.utils import timezone
from django.utils.text import slugify  # <--- IMPORTANTE: Importar slugify

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_final.settings')
django.setup()

from django.contrib.auth.models import User
from academy.models import (
    Profile, Category, Course, Module, Lesson, 
    Quiz, Question, Answer, HeroSlide, CertificationCard
)

def populate():
    print("=== POBLANDO BASE DE DATOS LMS ACADEMY (FIXED) ===")

    # 1. CREAR SUPERUSUARIO Y PROFESOR
    print("--> Creando usuarios...")
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@lms.com', 'admin123')
        admin.first_name = "Admin"
        admin.last_name = "User"
        admin.save()
        
        if not hasattr(admin, 'profile'):
            Profile.objects.create(user=admin, role='teacher', bio='Director y Fundador de LMS Academy.')
        else:
            admin.profile.role = 'teacher'
            admin.profile.bio = 'Director y Fundador de LMS Academy.'
            admin.profile.save()
    
    u_admin = User.objects.get(username='admin')

    # 2. CREAR CATEGORÍAS
    print("--> Creando categorías...")
    categories_data = [
        {'name': 'Desarrollo Web', 'icon': 'fas fa-code'},
        {'name': 'Data Science', 'icon': 'fas fa-chart-line'},
        {'name': 'Diseño UX/UI', 'icon': 'fas fa-pen-nib'},
        {'name': 'Negocios', 'icon': 'fas fa-briefcase'},
        {'name': 'Marketing', 'icon': 'fas fa-bullhorn'},
    ]
    
    categories = {}
    for cat in categories_data:
        # Usamos slugify aquí también por seguridad
        slug_cat = slugify(cat['name'])
        c, created = Category.objects.get_or_create(
            name=cat['name'],
            defaults={'slug': slug_cat, 'icon': cat['icon']}
        )
        if not created:
            c.icon = cat['icon']
            c.save()
        categories[cat['name']] = c

    # 3. CREAR CURSOS
    print("--> Creando cursos...")
    courses_list = [
        {
            'title': 'Python de Cero a Experto',
            'category': 'Desarrollo Web',
            'level': 'beginner',
            'price': 49.99,
            'desc': 'Domina el lenguaje más popular del mundo.',
            'short': 'Aprende Python desde las bases.'
        },
        {
            'title': 'Master en React y Tailwind',
            'category': 'Desarrollo Web',
            'level': 'intermediate',
            'price': 89.99,
            'desc': 'Crea interfaces modernas y responsivas.',
            'short': 'Construye aplicaciones web modernas.'
        },
        {
            'title': 'Análisis de Datos con Pandas', # <--- EL CULPABLE
            'category': 'Data Science',
            'level': 'intermediate',
            'price': 65.00,
            'desc': 'Transforma datos en información valiosa.',
            'short': 'Domina la librería más potente para ciencia de datos.'
        },
        {
            'title': 'Diseño de Interfaces Móviles',
            'category': 'Diseño UX/UI',
            'level': 'beginner',
            'price': 35.00,
            'desc': 'Aprende Figma a fondo.',
            'short': 'Diseña apps que los usuarios amen usar.'
        },
        {
            'title': 'Liderazgo para Gerentes',
            'category': 'Negocios',
            'level': 'advanced',
            'price': 120.00,
            'desc': 'Habilidades blandas esenciales.',
            'short': 'Lleva tu carrera gerencial al siguiente nivel.'
        },
        {
            'title': 'SEO Técnico Avanzado',
            'category': 'Marketing',
            'level': 'advanced',
            'price': 55.00,
            'desc': 'Posiciona tu sitio web en los primeros lugares.',
            'short': 'Domina los motores de búsqueda.'
        }
    ]

    for course_data in courses_list:
        cat = categories.get(course_data['category'])
        
        # CORRECCIÓN CLAVE: Usamos slugify() para limpiar tildes y caracteres raros
        clean_slug = slugify(course_data['title']) 
        
        course, created = Course.objects.get_or_create(
            title=course_data['title'],
            defaults={
                'slug': clean_slug, # <--- Aquí estaba el error antes
                'category': cat,
                'instructor': u_admin,
                'description': course_data['desc'],
                'short_description': course_data['short'],
                'price': course_data['price'],
                'level': course_data['level']
            }
        )
        
        if created:
            m = Module.objects.create(course=course, title="Introducción", order=1)
            Lesson.objects.create(module=m, title="Bienvenida", content="Intro...", duration=10, order=1)
            q = Quiz.objects.create(module=m, title="Quiz Demo", pass_mark=60)
            que = Question.objects.create(quiz=q, text="¿Pregunta de prueba?")
            Answer.objects.create(question=que, text="Sí", is_correct=True)
            Answer.objects.create(question=que, text="No", is_correct=False)

    # 4. CREAR SLIDES DEL HOME
    print("--> Creando slides del home...")
    slides_data = [
        {
            'title': '<span class="block">Desarrolla tus</span><span class="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 via-orange-400 to-yellow-500">Habilidades</span>',
            'description': 'Obtén acceso ilimitado a más de 10,000 programas.',
            'style': 'promo', 'tag_text': 'Oferta Limitada', 'btn1_text': 'Ahorra en LMS Plus', 'order': 1
        },
        {
            'title': 'Impulsa tu negocio y potencia a tus equipos',
            'description': 'Capacitación personalizada para empresas.',
            'style': 'business', 'tag_text': '', 'btn1_text': 'LMS para Negocios', 'order': 2
        },
        {
            'title': 'Inteligencia Artificial <br><span class="text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-500 to-purple-600">Generativa</span>',
            'description': 'Domina ChatGPT y Midjourney.',
            'style': 'new', 'tag_text': 'NUEVO LANZAMIENTO', 'btn1_text': 'Ver Programa', 'btn2_text': 'Trailer', 'order': 3
        }
    ]

    for slide in slides_data:
        HeroSlide.objects.get_or_create(
            title=slide['title'],
            defaults={
                'description': slide['description'], 'style': slide['style'],
                'tag_text': slide['tag_text'], 'btn1_text': slide['btn1_text'],
                'btn2_text': slide.get('btn2_text', ''), 'order': slide['order'], 'is_active': True
            }
        )

    # 5. CREAR CERTIFICACIONES
    print("--> Creando certificaciones...")
    certs_data = [
        {'title': 'Analista Power BI', 'provider': 'Microsoft', 'icon': 'fab fa-microsoft', 'style': 'blue', 'rating': 4.8, 'reviews': 1200, 'order': 1},
        {'title': 'Ciberseguridad', 'provider': 'IBM', 'icon': 'fas fa-shield-alt', 'style': 'indigo', 'rating': 4.9, 'reviews': 850, 'order': 2},
        {'title': 'Python Automate', 'provider': 'Google', 'icon': 'fab fa-python', 'style': 'green', 'rating': 4.7, 'reviews': 5000, 'order': 3}
    ]

    for cert in certs_data:
        CertificationCard.objects.get_or_create(
            title=cert['title'],
            defaults={
                'provider': cert['provider'], 'icon_class': cert['icon'],
                'style': cert['style'], 'rating': cert['rating'],
                'reviews_count': cert['reviews'], 'order': cert['order'], 'is_active': True
            }
        )

    print("=== ¡CORRECCIÓN COMPLETADA! ===")

if __name__ == '__main__':
    populate()