from django.contrib import admin

from .models import Operation, Record


class OperationAdmin(admin.ModelAdmin):
    list_display = ("type", "cost", "id")
    list_filter = ("type",)


class RecordAdmin(admin.ModelAdmin):
    list_display = ("operation", "user", "amount", "user_balance", "operation_response")
    list_filter = ("operation", "user")


admin.site.register(Operation, OperationAdmin)
admin.site.register(Record, RecordAdmin)
