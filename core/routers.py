from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.views import PrinterViewSet, CheckViewSet, download_check

router = DefaultRouter()

router.register(prefix="printers", viewset=PrinterViewSet)
router.register(prefix="checks", viewset=CheckViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "download-check/<int:check_id>/", download_check, name="download_check"
    ),
]

app_name = "core"
