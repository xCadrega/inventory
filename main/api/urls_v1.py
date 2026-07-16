from django.urls import path

from . import views

urlpatterns = [
    path("employees/", views.Employees.as_view()),
    path("employees/<int:employee_id>/", views.Employees.as_view()),
    path("workstations/", views.workstations),
    path("system-units/", views.system_units),
    path("monitors/", views.monitors),
    path("printers/", views.printers),
    path("ip-phones/", views.ip_phones),
    path("ups/", views.ups),
    path("iss/", views.iss),
    path("asset-categories/", views.asset_categories),
    path("assets/", views.assets)
]
