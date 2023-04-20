from rest_framework import serializers

from core.models import Printer, Check


class PrinterSchema(serializers.ModelSerializer):
    class Meta:
        model = Printer
        fields = "__all__"


class CheckSchema(serializers.ModelSerializer):
    class Meta:
        model = Check
        fields = "__all__"
