from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
from ops.models import District, Branch, ATM, Incident, Maintenance

class Command(BaseCommand):
    help = "Create demo users and sample operational data"

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(username="demo", defaults={"email":"demo@example.com","is_staff":True})
        if created:
            user.set_password("Demo12345!")
            user.save()
        districts = {}
        for name in ["Addis Ababa","Adama","Jimma","Hawassa"]:
            districts[name], _ = District.objects.get_or_create(name=name)
        branch_specs = [
            ("Bole Branch","Addis Ababa"),("Mexico Branch","Addis Ababa"),
            ("Adama Main Branch","Adama"),("Jimma Branch","Jimma"),("Hawassa Branch","Hawassa")
        ]
        branches = {}
        for name, district in branch_specs:
            branches[name], _ = Branch.objects.get_or_create(name=name,district=districts[district])
        atm_specs = [
            ("HJR-ATM-001","Bole ATM","Bole Branch","NCR","ONLINE",78),
            ("HJR-ATM-002","Bole CRM","Bole Branch","CRM","CASH_LOW",17),
            ("HJR-ATM-003","Mexico ATM","Mexico Branch","NCR","OFFLINE",62),
            ("HJR-ATM-004","Adama ATM","Adama Main Branch","NCR","ONLINE",83),
            ("HJR-ATM-005","Jimma CRM","Jimma Branch","CRM","MAINTENANCE",54),
            ("HJR-ATM-006","Hawassa ATM","Hawassa Branch","NCR","ONLINE",91),
        ]
        atms = {}
        for tid,name,branch,typ,status,cash in atm_specs:
            atms[tid], _ = ATM.objects.get_or_create(terminal_id=tid, defaults={
                "name":name,"branch":branches[branch],"device_type":typ,"manufacturer":"Demo Vendor",
                "status":status,"cash_level":cash,"network_status":"OFFLINE" if status=="OFFLINE" else "ONLINE"})
        incident_specs = [
            ("HJR-ATM-002","CASH_LOW","HIGH","Cash level below replenishment threshold.","PENDING",3),
            ("HJR-ATM-003","NETWORK","CRITICAL","ATM is unreachable from monitoring network.","IN_PROGRESS",5),
            ("HJR-ATM-005","DISPENSER","MEDIUM","Dispenser test failed during maintenance check.","NEW",1),
            ("HJR-ATM-001","CARD_READER","MEDIUM","Intermittent card reader response.","RESOLVED",8),
        ]
        for tid,typ,priority,desc,status,hours in incident_specs:
            incident_id = f"DEMO-{tid}-{typ}"
            if not Incident.objects.filter(incident_id=incident_id).exists():
                obj = Incident(atm=atms[tid],problem_type=typ,priority=priority,description=desc,
                               status=status,created_by=user,incident_id=incident_id,
                               created_at=timezone.now()-timedelta(hours=hours))
                if status == "RESOLVED":
                    obj.resolved_at = timezone.now()-timedelta(hours=1)
                obj.save()
        Maintenance.objects.get_or_create(maintenance_id="DEMO-PM-001", defaults={
            "atm":atms["HJR-ATM-004"],"maintenance_type":"PREVENTIVE","vendor":"Demo Vendor",
            "scheduled_date":date.today()+timedelta(days=3),"technician":"Demo Technician","status":"SCHEDULED"})
        self.stdout.write(self.style.SUCCESS("Demo data ready. Login: demo / Demo12345!"))
