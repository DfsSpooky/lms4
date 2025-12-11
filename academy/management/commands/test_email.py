from django.core.management.base import BaseCommand
from academy.services.email_service import EmailService
from django.conf import settings

class Command(BaseCommand):
    help = 'Envía un correo de prueba para verificar la configuración SMTP.'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Dirección de correo electrónico del destinatario')

    def handle(self, *args, **kwargs):
        email = kwargs['email']
        self.stdout.write(f"Intentando enviar correo a: {email}")
        self.stdout.write(f"Backend configurado: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"Host: {settings.EMAIL_HOST or 'No configurado (usando consola)'}")

        subject = "Prueba de Configuración de Correo - LMS"
        message = "Si estás leyendo esto, la configuración de envío de correos funciona correctamente."

        success = EmailService.send_email(subject, message, [email])

        if success:
            self.stdout.write(self.style.SUCCESS(f"Correo enviado exitosamente a {email}"))
        else:
            self.stdout.write(self.style.ERROR("Error al enviar el correo. Revisa los logs."))
