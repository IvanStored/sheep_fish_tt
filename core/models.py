from django.db import models


class Type(models.TextChoices):
    KITCHEN = "KITCHEN"
    CLIENT = "CLIENT"


class Printer(models.Model):
    name = models.CharField(max_length=32)
    api_key = models.CharField(max_length=100, unique=True)
    check_type = models.CharField(max_length=7, choices=Type.choices)
    point_id = models.IntegerField()

    def __str__(self):
        return f"Printer {self.name} for {self.check_type} checks"


class Check(models.Model):
    NEW = "new"
    RENDERED = "rendered"
    PRINTED = "printed"

    STATUSES = [
        (NEW, "new"),
        (RENDERED, "rendered"),
        (PRINTED, "printed"),
    ]

    printer_id = models.ForeignKey(
        Printer, on_delete=models.CASCADE, related_name="checks"
    )
    check_type = models.CharField(max_length=7, choices=Type.choices)
    order = models.JSONField()
    status = models.CharField(max_length=8, choices=STATUSES, default=NEW)
    pdf_file = models.FileField(upload_to="pdf/", null=True, blank=True)
