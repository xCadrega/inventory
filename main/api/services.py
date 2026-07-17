from django.db import transaction
from inventory.models import (
    Employee,
    Workstation,
    SystemUnit,
    Equipment,
    EquipmentType
)


@transaction.atomic
def create_employee_with_workstation(employee_data):
    employee = Employee.objects.create(**employee_data)

    create_workstation(employee)

    return employee


def create_workstation(employee):
    system_unit = SystemUnit.objects.create()

    monitor_type = EquipmentType.objects.get(code="monitor")
    printer_type = EquipmentType.objects.get(code="printer")
    ip_phone_type = EquipmentType.objects.get(code="ip_phone")
    ups_type = EquipmentType.objects.get(code="ups")
    iss_type = EquipmentType.objects.get(code="iss")

    monitor = Equipment.objects.create(equipment_type=monitor_type)
    printer = Equipment.objects.create(equipment_type=printer_type)
    ip_phone = Equipment.objects.create(equipment_type=ip_phone_type)
    ups = Equipment.objects.create(equipment_type=ups_type)
    iss = Equipment.objects.create(equipment_type=iss_type)

    return Workstation.objects.create(
        employee=employee,
        system_unit=system_unit,
        monitor=monitor,
        printer=printer,
        ip_phone=ip_phone,
        ups=ups,
        iss=iss,
    )