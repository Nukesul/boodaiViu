"""
WSGI config for backend project.
Exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()

# Для явного логгирования порта при запуске
if os.getenv('GUNICORN_PORT_LOGGING', 'false').lower() == 'true':
    from django.conf import settings
    print(f"Application is running on port: {getattr(settings, 'PORT', 8000)}")