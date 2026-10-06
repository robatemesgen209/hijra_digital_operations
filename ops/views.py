import csv
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import ATM, Incident, Maintenance, AuditLog
from .forms import ATMForm, IncidentForm, MaintenanceForm

def log_action(user, action, obj=None):
    AuditLog.objects.create(user=user, action=action,
        object_type=obj.__class__.__name__ if obj else "",
        object_id=str(obj.pk) if obj else "")

@login_required
def dashboard(request):
    atms = ATM.objects.all()
    incidents = Incident.objects.all()
    context = {
        "total_atms": atms.count(),
        "online_atms": atms.filter(status="ONLINE").count(),
        "offline_atms": atms.filter(status="OFFLINE").count(),
        "cash_low": atms.filter(status="CASH_LOW").count(),
        "open_incidents": incidents.exclude(status__in=["RESOLVED","CLOSED"]).count(),
        "resolved_incidents": incidents.filter(status__in=["RESOLVED","CLOSED"]).count(),
        "breached_incidents": [i for i in incidents if i.sla_breached],
        "within_target_count": sum(1 for i in incidents if not i.sla_breached),
        "recent_incidents": incidents.select_related("atm","atm__branch")[:7],
        "status_data": [
            {"label":"Online","value":atms.filter(status="ONLINE").count(),"color":"#10b981"},
            {"label":"Offline","value":atms.filter(status="OFFLINE").count(),"color":"#ef4444"},
            {"label":"Cash Low","value":atms.filter(status="CASH_LOW").count(),"color":"#f59e0b"},
            {"label":"Maintenance","value":atms.filter(status="MAINTENANCE").count(),"color":"#64748b"},
        ],
        "type_data": list(incidents.values("problem_type").annotate(total=Count("id")).order_by("-total")),
    }
    return render(request, "ops/dashboard.html", context)

@login_required
def atm_list(request):
    qs = ATM.objects.select_related("branch","branch__district")
    status = request.GET.get("status")
    q = request.GET.get("q","").strip()
    if status: qs = qs.filter(status=status)
    if q: qs = qs.filter(terminal_id__icontains=q) | qs.filter(name__icontains=q) | qs.filter(branch__name__icontains=q)
    return render(request, "ops/atm_list.html", {"atms": qs, "status_choices": ATM.STATUS_CHOICES, "selected_status": status, "q":q})

@login_required
def atm_create(request):
    form = ATMForm(request.POST or None)
    if form.is_valid():
        obj = form.save()
        log_action(request.user, "Created ATM", obj)
        messages.success(request, "ATM/device registered successfully.")
        return redirect("atm_list")
    return render(request, "ops/form.html", {"form":form,"title":"Register digital device","cancel_url":"atm_list"})

@login_required
def atm_edit(request, pk):
    obj = get_object_or_404(ATM, pk=pk)
    form = ATMForm(request.POST or None, instance=obj)
    if form.is_valid():
        obj = form.save()
        log_action(request.user, "Updated ATM", obj)
        messages.success(request, "Device updated.")
        return redirect("atm_list")
    return render(request, "ops/form.html", {"form":form,"title":f"Edit {obj.terminal_id}","cancel_url":"atm_list"})

@login_required
def incident_list(request):
    qs = Incident.objects.select_related("atm","atm__branch","created_by","assigned_to")
    status = request.GET.get("status")
    q = request.GET.get("q","").strip()
    if status: qs = qs.filter(status=status)
    if q: qs = qs.filter(incident_id__icontains=q) | qs.filter(atm__terminal_id__icontains=q) | qs.filter(description__icontains=q)
    return render(request, "ops/incident_list.html", {"incidents":qs,"status_choices":Incident.STATUS_CHOICES,"selected_status":status,"q":q})

@login_required
def incident_create(request):
    form = IncidentForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.save()
        log_action(request.user, "Created incident", obj)
        messages.success(request, f"Incident {obj.incident_id} created.")
        return redirect("incident_list")
    return render(request, "ops/form.html", {"form":form,"title":"Register incident","cancel_url":"incident_list"})

@login_required
def incident_edit(request, pk):
    obj = get_object_or_404(Incident, pk=pk)
    form = IncidentForm(request.POST or None, instance=obj)
    if form.is_valid():
        obj = form.save()
        log_action(request.user, "Updated incident", obj)
        messages.success(request, f"Incident {obj.incident_id} updated.")
        return redirect("incident_list")
    return render(request, "ops/form.html", {"form":form,"title":f"Update {obj.incident_id}","cancel_url":"incident_list"})

@login_required
def maintenance_list(request):
    jobs = Maintenance.objects.select_related("atm","atm__branch")
    return render(request, "ops/maintenance_list.html", {"jobs":jobs})

@login_required
def maintenance_create(request):
    form = MaintenanceForm(request.POST or None)
    if form.is_valid():
        obj = form.save()
        log_action(request.user, "Created maintenance job", obj)
        messages.success(request, "Maintenance job created.")
        return redirect("maintenance_list")
    return render(request, "ops/form.html", {"form":form,"title":"Schedule maintenance","cancel_url":"maintenance_list"})

@login_required
def sla_dashboard(request):
    incidents = list(Incident.objects.select_related("atm","atm__branch"))
    breached = [i for i in incidents if i.sla_breached]
    return render(request, "ops/sla.html", {"incidents":incidents,"breached":breached})

@login_required
def incident_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="hijra_incidents_report.csv"'
    writer = csv.writer(response)
    writer.writerow(["Incident ID","Terminal ID","Branch","District","Problem","Priority","Status","Created At","Resolved At","SLA Hours","Resolution Hours","SLA Breached","Description"])
    for i in Incident.objects.select_related("atm","atm__branch","atm__branch__district"):
        writer.writerow([i.incident_id,i.atm.terminal_id,i.atm.branch.name,i.atm.branch.district.name,
            i.get_problem_type_display(),i.priority,i.get_status_display(),i.created_at,
            i.resolved_at or "",i.sla_hours,i.resolution_hours,"Yes" if i.sla_breached else "No",i.description])
    return response
