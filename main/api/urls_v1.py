from django.urls import path

from .views import (
    Employees,
    Workstations,
    SystemUnits,
    Monitors,
    Printers,
    IpPhones,
    Ups,
    Iss,
    Assets,
    asset_categories
)

urlpatterns = [
    path("employees/", Employees.as_view()),
    path("employees/<int:employee_id>/", Employees.as_view()),
    path("workstations/", Workstations.as_view()),
    path("workstations/<int:employee_id>/", Workstations.as_view()),
    path("system-units/", SystemUnits.as_view()),
    path("system-units/<int:system_unit_id>/", SystemUnits.as_view()),
    path("monitors/", Monitors.as_view()),
    path("monitors/<int:equipment_id>/", Monitors.as_view()),
    path("printers/", Printers.as_view()),
    path("printers/<int:equipment_id>/", Printers.as_view()),
    path("ip-phones/", IpPhones.as_view()),
    path("ip-phones/<int:equipment_id>/", IpPhones.as_view()),
    path("ups/", Ups.as_view()),
    path("ups/<int:equipment_id>/", Ups.as_view()),
    path("iss/", Iss.as_view()),
    path("iss/<int:equipment_id>/", Iss.as_view()),
    path("assets/", Assets.as_view()),
    path("assets/<int:category_id>/", Assets.as_view()),
    path("asset-categories/", asset_categories),
]
