"""
ASGI config for registrant_dashboard project.
It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registrant_dashboard.settings')

application = get_asgi_application()

cc_dashboard_app = ProtocolTypeRouter({
    "http": application,
})

ASGI_APPLICATION = "cc_registrant_dashboard.asgi.cc_dashboard_app"