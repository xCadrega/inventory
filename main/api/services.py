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

@transaction.atomic
def update_system_unit(system_unit_id, data, admin_id):
    from django.shortcuts import get_object_or_404
    from inventory.models import AssetCategory, ChangeLog
    from rest_framework.exceptions import ValidationError

    from .serializers import (
        SYSTEM_UNIT_ASSET_CATEGORIES,
        SystemUnitWriteSerializer,
    )

    system_unit = get_object_or_404(
        SystemUnit.objects.select_for_update(), id=system_unit_id
    )
    serializer = SystemUnitWriteSerializer(system_unit, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    category_codes = set(AssetCategory.objects.filter(
        code__in=SYSTEM_UNIT_ASSET_CATEGORIES.values()
    ).values_list("code", flat=True))
    changes = []
    for field, code in SYSTEM_UNIT_ASSET_CATEGORIES.items():
        if field not in serializer.validated_data or code not in category_codes:
            continue
        before = getattr(system_unit, field)
        after = serializer.validated_data[field]
        if (before.pk if before else None) == (after.pk if after else None):
            continue
        before_value = before.name if before else None
        after_value = data[field]
        if any(value is not None and len(value) > 256
               for value in (before_value, after_value)):
            raise ValidationError({field: "Значение не помещается в журнал изменений."})
        changes.append((code, before_value, after_value))

    for field, after_value in serializer.validated_data.items():
        if field in SYSTEM_UNIT_ASSET_CATEGORIES:
            continue
        before_value = getattr(system_unit, field)
        if before_value == after_value:
            continue
        if any(value is not None and len(value) > 256
               for value in (before_value, after_value)):
            raise ValidationError({field: "Значение не помещается в журнал изменений."})
        changes.append((field, before_value, after_value))

    if changes:
        equipment_type = EquipmentType.objects.get(code="system_unit")
        try:
            workstation = Workstation.objects.select_for_update().get(
                system_unit_id=system_unit.pk
            )
        except Workstation.DoesNotExist:
            workstation = None
        except Workstation.MultipleObjectsReturned:
            raise ValidationError({
                "id": "Системный блок ошибочно привязан к нескольким рабочим местам."
            }) from None
        for code, before_value, after_value in changes:
            ChangeLog.objects.create(
                admin_id=admin_id,
                employee_id=workstation.employee_id if workstation else None,
                workstation=workstation,
                equipment_type=equipment_type,
                field_name=code,
                value_before=before_value,
                value_after=after_value,
            )
    return serializer.save()


@transaction.atomic
def update_equipment(equipment_id, equipment_type, data, admin_id):
    from django.shortcuts import get_object_or_404
    from inventory.models import ChangeLog
    from rest_framework.exceptions import ValidationError

    from .serializers import EQUIPMENT_ASSET_CATEGORIES, EquipmentWriteSerializer

    equipment = get_object_or_404(
        Equipment.objects.select_for_update(),
        id=equipment_id,
        equipment_type__code=equipment_type,
    )
    serializer = EquipmentWriteSerializer(
        equipment, data=data, partial=True,
        context={"equipment_type": equipment_type},
    )
    serializer.is_valid(raise_exception=True)
    categories = EQUIPMENT_ASSET_CATEGORIES[equipment_type]
    changes = []
    for field, after in serializer.validated_data.items():
        before = getattr(equipment, field)
        if field in categories:
            if (before.pk if before else None) == (after.pk if after else None):
                continue
            before_value = before.name if before else None
            after_value = data[field]
        else:
            if before == after:
                continue
            before_value, after_value = before, after
        if any(value is not None and len(value) > 256
               for value in (before_value, after_value)):
            raise ValidationError({field: "Значение не помещается в журнал изменений."})
        changes.append((categories.get(field, field), before_value, after_value))

    if changes:
        try:
            workstation = Workstation.objects.select_for_update().get(
                **{equipment_type + "_id": equipment.pk}
            )
        except Workstation.DoesNotExist:
            workstation = None
        except Workstation.MultipleObjectsReturned:
            raise ValidationError({
                "id": "Оборудование ошибочно привязано к нескольким рабочим местам."
            }) from None
        for field_name, before_value, after_value in changes:
            ChangeLog.objects.create(
                admin_id=admin_id,
                employee_id=workstation.employee_id if workstation else None,
                workstation=workstation,
                equipment_type_id=equipment.equipment_type_id,
                field_name=field_name,
                value_before=before_value,
                value_after=after_value,
            )
    return serializer.save()
