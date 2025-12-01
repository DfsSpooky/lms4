from .models import Notification, TopBanner, SiteConfiguration

def notifications_processor(request):
    """
    Context processor para disponibilizar notificaciones y banners 
    globales en todas las plantillas.
    """
    context = {}

    # 0. Configuración del Sitio (Global)
    # Cache optimization: SiteConfiguration.get_solo() uses get_or_create but we could cache it
    # For now, a DB hit per request is acceptable for this scale.
    try:
        context['site_config'] = SiteConfiguration.get_solo()
    except Exception:
        context['site_config'] = None

    # 1. Lógica de Notificaciones (Solo para usuarios logueados)
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        latest_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        
        context['unread_notifications_count'] = unread_count
        context['latest_notifications'] = latest_notifications

    # 2. Lógica de la Barra de Anuncios (Para todos los usuarios, incluso anónimos)
    # Obtenemos el último banner que esté marcado como activo
    active_banner = TopBanner.objects.filter(is_active=True).last()
    context['top_banner'] = active_banner

    return context