from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url
from django.urls import reverse
from .models import Profile

class MyAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        # 1. Resolver la URL base (normalmente 'academy:dashboard' o 'home')
        url = super().get_login_redirect_url(request)

        # 2. Verificar si el usuario tiene los datos obligatorios
        user = request.user
        if user.is_authenticated:
            try:
                profile = user.profile
                # Campos obligatorios definidos: DNI y Celular (según forms.py / request)
                if not profile.dni or not profile.phone_number:
                    return resolve_url('academy:profile_edit')
            except Profile.DoesNotExist:
                # Si no tiene perfil (raro, pero posible), crearlo o mandarlo a editar
                return resolve_url('academy:profile_edit')

        return url

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Opcional: Validaciones extra antes de loguear
        pass

    def save_user(self, request, sociallogin, form=None):
        # Se llama cuando se crea un usuario nuevo via social
        user = super().save_user(request, sociallogin, form)
        # Aseguramos que tenga perfil
        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user)
        return user
