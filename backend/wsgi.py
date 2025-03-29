"""
WSGI config for backend project.
Exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
application = get_wsgi_application()

# Для явного указания порта при локальном запуске
if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    print(f"Starting server on port {port}")  # Логирование порта
    from waitress import serve
    serve(application, host="0.0.0.0", port=port, threads=4)