from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("atms/", views.atm_list, name="atm_list"),
    path("atms/new/", views.atm_create, name="atm_create"),
    path("atms/<int:pk>/edit/", views.atm_edit, name="atm_edit"),
    path("incidents/", views.incident_list, name="incident_list"),
    path("incidents/new/", views.incident_create, name="incident_create"),
    path("incidents/<int:pk>/edit/", views.incident_edit, name="incident_edit"),
    path("maintenance/", views.maintenance_list, name="maintenance_list"),
    path("maintenance/new/", views.maintenance_create, name="maintenance_create"),
    path("sla/", views.sla_dashboard, name="sla_dashboard"),
    path("reports/incidents.csv", views.incident_csv, name="incident_csv"),
]
