"""
ASGI entrypoint (mainly for deployments).

For local dev we usually just use `runserver`, but keeping ASGI/WGSI around is
standard Django boilerplate.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
