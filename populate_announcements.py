import os
import django

# 1. Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_final.settings')
django.setup()

from academy.models import AnnouncementCard

def populate_announcements():
    print("=== CREANDO ANUNCIOS RÁPIDOS (BANNERS) ===")

    # Limpiar anuncios existentes para no duplicar si lo corres varias veces
    AnnouncementCard.objects.all().delete()
    print("-> Anuncios anteriores eliminados.")

    # --- ANUNCIO 1: ESTILO PLUS (AZUL BRILLANTE) ---
    AnnouncementCard.objects.create(
        title="Desbloquea el acceso a más de 10,000 cursos con una suscripción",
        description="Obtén certificados ilimitados, especializaciones y más con LMS Plus. Cancela cuando quieras.",
        btn_text="Comenzar la prueba gratuita de 7 días",
        btn_url="/plus/",
        style="primary",  # Azul brillante
        order=1,
        is_active=True
        # Nota: Puedes subir una imagen manualmente desde el admin después para que quede perfecto
    )
    print("-> Creado: Anuncio LMS Plus (Azul)")

    # --- ANUNCIO 2: ESTILO BUSINESS (OSCURO) ---
    AnnouncementCard.objects.create(
        title="Impulsa tu negocio y potencia a tus equipos",
        description="Capacitación de clase mundial para empresas de todos los tamaños. Desarrolla el talento de tu organización.",
        btn_text="Prueba LMS para negocios",
        btn_url="/business/",
        style="dark",  # Azul oscuro / Negro
        order=2,
        is_active=True
    )
    print("-> Creado: Anuncio Business (Oscuro)")

    # --- ANUNCIO 3: EXTRA (GRADIENTE) ---
    AnnouncementCard.objects.create(
        title="Aprende Inteligencia Artificial hoy",
        description="Domina ChatGPT, Midjourney y Python para IA. El futuro es ahora.",
        btn_text="Ver ruta de aprendizaje",
        btn_url="/courses/?q=ia",
        style="gradient",  # Gradiente morado/índigo
        order=3,
        is_active=True
    )
    print("-> Creado: Anuncio IA (Gradiente)")

    print("\n=== ¡LISTO! 3 ANUNCIOS CREADOS ===")
    print("Nota: Para ver las imágenes decorativas, entra al admin y súbelas en la sección 'Tarjetas de Anuncios'.")

if __name__ == '__main__':
    populate_announcements()