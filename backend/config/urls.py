"""
Root URL routes.

I kept it simple on purpose:
- `/admin/` for Django admin (optional, mostly for debugging)
- `/api/` for the REST endpoints used by the frontend
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
