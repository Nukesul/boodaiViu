import os
from django.conf import settings

bind = f"0.0.0.0:{os.getenv('PORT', getattr(settings, 'PORT', 8000))}"
workers = 4
timeout = 120
accesslog = '-'
errorlog = '-'