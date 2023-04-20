import os

from celery import shared_task
from django.template.loader import get_template
from xhtml2pdf import pisa

from core.models import Check
from sheepfish_tt import settings


@shared_task
def render_checks(check_id: int) -> None:
    check = Check.objects.get(id=check_id)
    check.status = Check.RENDERED

    template = get_template("check.html")

    html = template.render(
        {
            "id": check.id,
            "type": check.check_type,
            "point": check.order["point_id"],
            "order": check.order,
        }
    )

    filename = f"{check.id}_{check.check_type}.pdf"
    path = os.path.join(settings.MEDIA_ROOT, filename)

    with open(path, "wb") as f:
        pisa.CreatePDF(src=html, dest=f)

    check.pdf_file.name = os.path.join("pdf", filename)

    check.save()
