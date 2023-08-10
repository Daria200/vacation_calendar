from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("calendarapp.urls")),
    path("admin/", admin.site.urls),
    path("", include("vacations.urls")),
    path("", include("employees.urls")),
    path("manager/", include("manager.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
