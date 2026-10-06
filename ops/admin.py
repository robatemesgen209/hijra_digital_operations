from django.contrib import admin
from .models import District, Branch, ATM, Incident, Maintenance, AuditLog

@admin.register(ATM)
class ATMAdmin(admin.ModelAdmin):
    list_display = ("terminal_id","name","branch","device_type","status","cash_level","network_status")
    list_filter = ("status","device_type","network_status","branch__district")
    search_fields = ("terminal_id","name","branch__name")

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ("incident_id","atm","problem_type","priority","status","created_at","resolved_at")
    list_filter = ("status","priority","problem_type")
    search_fields = ("incident_id","atm__terminal_id","description")

admin.site.register([District, Branch, Maintenance, AuditLog])
