import uuid
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

def send_activation_email(user, request):
    """
    Envía un correo de activación al usuario con un link único.
    """
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_link = request.build_absolute_uri(
        reverse('cuser:activate', kwargs={'uidb64': uid, 'token': token})
    )
    subject = 'Activa tu cuenta'
    context = {
        'username': user.username,
        'activation_link': activation_link,
    }
    text_content = f'Hola {user.username},\nPor favor haz clic en el siguiente enlace para activar tu cuenta: {activation_link}'
    html_content = render_to_string('email/activation_email.html', context)
    email = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)
