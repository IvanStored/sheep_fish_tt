from django.contrib import admin

from core import models


@admin.register(models.Printer)
class PrinterAdmin(admin.ModelAdmin):
    search_fields = ("name", )
    list_filter = ("name", "check_type")


@admin.register(models.Check)
class CheckAdmin(admin.ModelAdmin):
    list_filter = ("printer_id", "check_type", "status")
