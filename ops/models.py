from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class District(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name
    class Meta: ordering = ["name"]

class Branch(models.Model):
    name = models.CharField(max_length=150)
    district = models.ForeignKey(District, on_delete=models.PROTECT, related_name="branches")
    code = models.CharField(max_length=30, blank=True)
    def __str__(self): return f"{self.name} ({self.district.name})"
    class Meta: ordering = ["name"]
    class Meta:
        ordering = ["name"]
        unique_together = [("name", "district")]

class ATM(models.Model):
    STATUS_CHOICES = [
        ("ONLINE", "Online"), ("OFFLINE", "Offline"),
        ("CASH_LOW", "Cash Low"), ("MAINTENANCE", "Under Maintenance"),
    ]
    TYPE_CHOICES = [("NCR", "NCR"), ("CRM", "Cash Recycler"), ("POS", "POS")]
    terminal_id = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=150)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="devices")
    device_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="NCR")
    manufacturer = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ONLINE")
    cash_level = models.PositiveSmallIntegerField(default=100, help_text="Percentage from 0 to 100")
    network_status = models.CharField(max_length=20, choices=[("ONLINE","Online"),("OFFLINE","Offline")], default="ONLINE")
    last_checked = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.terminal_id} — {self.name}"
    class Meta: ordering = ["terminal_id"]

class Incident(models.Model):
    TYPE_CHOICES = [
        ("CASH_LOW", "Cash Low"), ("DISPENSER", "Dispenser Error"),
        ("CARD_READER", "Card Reader"), ("NETWORK", "Network Failure"),
        ("POWER", "Power Failure"), ("SOFTWARE", "Software Error"), ("OTHER", "Other"),
    ]
    STATUS_CHOICES = [
        ("NEW", "New"), ("PENDING", "Pending"), ("IN_PROGRESS", "In Progress"),
        ("RESOLVED", "Resolved"), ("CLOSED", "Closed"),
    ]
    PRIORITY_CHOICES = [("LOW","Low"),("MEDIUM","Medium"),("HIGH","High"),("CRITICAL","Critical")]
    incident_id = models.CharField(max_length=30, unique=True, blank=True)
    atm = models.ForeignKey(ATM, on_delete=models.PROTECT, related_name="incidents")
    problem_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="MEDIUM")
    description = models.TextField()
    caller_name = models.CharField(max_length=120, blank=True)
    contact_number = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="NEW")
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_incidents")
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_incidents")
    created_at = models.DateTimeField(default=timezone.now)
    resolved_at = models.DateTimeField(null=True, blank=True)
    root_cause = models.TextField(blank=True)
    corrective_action = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.incident_id:
            last = Incident.objects.order_by("-id").first()
            self.incident_id = f"INC-{timezone.localdate():%Y}-{(last.id + 1) if last else 1:06d}"
        if self.status in ("RESOLVED", "CLOSED") and not self.resolved_at:
            self.resolved_at = timezone.now()
        elif self.status not in ("RESOLVED", "CLOSED"):
            self.resolved_at = None
        super().save(*args, **kwargs)

    @property
    def resolution_hours(self):
        end = self.resolved_at or timezone.now()
        return round((end - self.created_at).total_seconds() / 3600, 2)

    @property
    def sla_hours(self):
        return {"CASH_LOW": 2, "DISPENSER": 4, "CARD_READER": 4, "NETWORK": 2,
                "POWER": 4, "SOFTWARE": 8, "OTHER": 8}.get(self.problem_type, 8)

    @property
    def sla_breached(self):
        return self.resolution_hours > self.sla_hours and self.status not in ("RESOLVED", "CLOSED") or (
            self.resolved_at is not None and self.resolution_hours > self.sla_hours
        )

    def __str__(self): return self.incident_id
    class Meta: ordering = ["-created_at"]

class Maintenance(models.Model):
    TYPE_CHOICES = [("PREVENTIVE","Preventive"),("CORRECTIVE","Corrective")]
    STATUS_CHOICES = [("SCHEDULED","Scheduled"),("IN_PROGRESS","In Progress"),("COMPLETED","Completed"),("CANCELLED","Cancelled")]
    maintenance_id = models.CharField(max_length=30, unique=True, blank=True)
    atm = models.ForeignKey(ATM, on_delete=models.PROTECT, related_name="maintenance_jobs")
    maintenance_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default="PREVENTIVE")
    vendor = models.CharField(max_length=150, blank=True)
    scheduled_date = models.DateField()
    technician = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="SCHEDULED")
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.maintenance_id:
            last = Maintenance.objects.order_by("-id").first()
            self.maintenance_id = f"PM-{timezone.localdate():%Y}-{(last.id + 1) if last else 1:05d}"
        super().save(*args, **kwargs)
    def __str__(self): return self.maintenance_id
    class Meta: ordering = ["scheduled_date"]

class AuditLog(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=200)
    object_type = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-created_at"]
