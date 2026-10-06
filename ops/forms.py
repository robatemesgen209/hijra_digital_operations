from django import forms
from .models import ATM, Incident, Maintenance

class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

class ATMForm(StyledModelForm):
    class Meta:
        model = ATM
        fields = ["terminal_id","name","branch","device_type","manufacturer","status","cash_level","network_status","notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

class IncidentForm(StyledModelForm):
    class Meta:
        model = Incident
        fields = ["atm","problem_type","priority","description","caller_name","contact_number","status","assigned_to","root_cause","corrective_action"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3}), "root_cause": forms.Textarea(attrs={"rows": 2}), "corrective_action": forms.Textarea(attrs={"rows": 2})}

class MaintenanceForm(StyledModelForm):
    class Meta:
        model = Maintenance
        fields = ["atm","maintenance_type","vendor","scheduled_date","technician","status","remarks"]
        widgets = {"scheduled_date": forms.DateInput(attrs={"type":"date"}), "remarks": forms.Textarea(attrs={"rows": 3})}
