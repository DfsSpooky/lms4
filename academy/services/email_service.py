import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_email(subject, message, recipient_list, from_email=None, html_message=None):
        """
        Envía un correo electrónico.

        Args:
            subject (str): Asunto del correo.
            message (str): Mensaje de texto plano.
            recipient_list (list): Lista de destinatarios.
            from_email (str, optional): Remitente. Defaults to settings.DEFAULT_FROM_EMAIL.
            html_message (str, optional): Mensaje en HTML.

        Returns:
            bool: True si se envió correctamente, False en caso de error.
        """
        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL

        try:
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Email sent successfully to {recipient_list}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_list}: {str(e)}")
            return False

    @staticmethod
    def send_template_email(subject, template_name, context, recipient_list, from_email=None):
        """
        Envía un correo renderizando un template HTML.

        Args:
            subject (str): Asunto.
            template_name (str): Ruta al template (ej: 'academy/emails/welcome.html').
            context (dict): Contexto para el template.
            recipient_list (list): Lista de destinatarios.
        """
        try:
            html_message = render_to_string(template_name, context)
            plain_message = strip_tags(html_message)
            return EmailService.send_email(subject, plain_message, recipient_list, from_email, html_message=html_message)
        except Exception as e:
            logger.error(f"Error rendering/sending template email '{template_name}': {str(e)}")
            return False
