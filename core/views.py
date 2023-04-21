from django.http import FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import Printer, Check
from core.schemas import PrinterSchema, CheckSchema
from core.tasks import render_checks
from sheepfish_tt import settings


class PrinterViewSet(viewsets.ModelViewSet):
    queryset = Printer.objects.all()
    serializer_class = PrinterSchema


class CheckViewSet(viewsets.ModelViewSet):
    queryset = Check.objects.select_related("printer_id")
    serializer_class = CheckSchema

    def create(self, request: Request, *args, **kwargs) -> Response:
        order = request.data.get("order")

        printers = Printer.objects.filter(point_id=order.get("point_id"))

        if Check.objects.filter(
            order__order_id=order.get("order_id")
        ).exists():
            return Response(
                {"message": "Check for this order already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not printers:
            return Response(
                {"message": "Not printers for this point"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        checks = []
        for printer in printers:
            data = {
                "printer_id": printer.id,
                "check_type": printer.check_type,
                "order": order,
            }
            serializer = CheckSchema(data=data)
            serializer.is_valid(raise_exception=True)
            check = serializer.save()

            checks.append(check)

        return Response({"checks": CheckSchema(checks, many=True).data})

    @action(
        detail=False,
        methods=["get"],
        url_path=r"print/(?P<api_key>[\w-]+)",
        url_name="print",
    )
    def send_checks_to_print(self, request: Request, api_key: str) -> Response:
        new_checks = Check.objects.filter(
            printer_id__api_key=api_key, status=Check.NEW
        )

        if not new_checks:
            return Response(
                {"message": f"There are no checks available"},
                status=status.HTTP_404_NOT_FOUND,
            )

        for check in new_checks:
            render_checks.delay(check.id)

        serializer = self.get_serializer(new_checks, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def download_check(request: Request, check_id: int) -> Response | FileResponse:
    try:
        check = Check.objects.get(id=check_id)
    except Check.DoesNotExist:
        return Response(
            {"message": "Check does not exist"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if check.status != Check.RENDERED:
        return Response(
            {"message": f"Check {check_id} is not available for download."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    path = f"{check.id}_{check.check_type}.pdf"
    filepath = settings.MEDIA_ROOT / path

    if not filepath.exists():
        return Response(
            {"message": "There is no available check for download."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    response = FileResponse(open(filepath, "rb"))
    response["Content-Disposition"] = f"attachment; filename={filepath.name}"
    check.status = Check.PRINTED
    check.save()
    return response
