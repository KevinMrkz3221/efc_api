from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from django.template.loader import render_to_string

def send_password_reset_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    # Enlace directo al frontend
    reset_link = f"http://localhost:5173/user/password-reset-confirm/{uid}/{token}/"
    subject = 'Recuperación de contraseña'
    context = {
        'username': user.username,
        'reset_link': reset_link,
    }
    text_content = f'Hola {user.username},\nPara restablecer tu contraseña haz clic en el siguiente enlace: {reset_link}'
    html_content = render_to_string('email/password_reset_email.html', context)
    email = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)
