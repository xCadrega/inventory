from django.db.models import (
    DO_NOTHING,
    AutoField,
    IntegerField,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    Model,
    UniqueConstraint,
)


class Department(Model):
    id = AutoField(primary_key=True)
    name = CharField(max_length=255)
    code = CharField(max_length=4, unique=True)

    class Meta:
        app_label = "inventory"
        db_table = "departments"


class Management(Model):
    id = AutoField(primary_key=True)
    name = CharField(max_length=256, blank=True, null=True)

    class Meta:
        app_label = "inventory"
        db_table = "managements"


class Employee(Model):
    id = AutoField(primary_key=True)
    fullname = CharField(max_length=256, blank=True, null=True)
    cabinet = CharField(max_length=128, blank=True, null=True)
    management = ForeignKey(
        Management,
        on_delete=DO_NOTHING,
        db_column="management_id",
        blank=True,
        null=True,
        related_name="employees"
    )
    department = ForeignKey(
        Department,
        on_delete=DO_NOTHING,
        db_column="department_id",
        blank=True,
        null=True,
        related_name="employees"
    )
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    is_active = BooleanField(default=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["fullname", "cabinet", "management"],
                name="unique_employee"
            )
        ]
        app_label = "inventory"
        db_table = "employees"

    def __str__(self):
        return self.fullname or ""


class EquipmentType(Model):
    id = AutoField(primary_key=True)
    name = CharField(max_length=64, blank=True, null=True)
    code = CharField(max_length=64, blank=True, null=True)

    class Meta:
        app_label = "inventory"
        db_table = "equipment_types"

    def __str__(self):
        return self.name or ""


class AssetCategory(Model):
    id = AutoField(primary_key=True)
    name = CharField(max_length=64, blank=True, null=True)
    code = CharField(max_length=64, blank=True, null=True)

    class Meta:
        app_label = "inventory"
        db_table = "asset_categories"

    def __str__(self):
        return self.name or ""


class Asset(Model):
    id = AutoField(primary_key=True)
    category = ForeignKey(
        AssetCategory,
        on_delete=DO_NOTHING,
        db_column="category_id",
        blank=True,
        null=True,
        related_name="assets"
    )
    name = CharField(max_length=256, blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        app_label = "inventory"
        db_table = "assets"

    def __str__(self):
        return self.name or ""


class SystemUnit(Model):
    id = AutoField(primary_key=True)
    model = ForeignKey(
        Asset,
        on_delete=DO_NOTHING,
        db_column="model_id",
        blank=True,
        null=True,
        related_name="system_unit_models"
    )
    serial_number = CharField(max_length=64, blank=True, null=True)
    inventory_number = CharField(max_length=64, blank=True, null=True)
    computer_name = CharField(max_length=128, blank=True, null=True)
    account = CharField(max_length=128, blank=True, null=True)
    domain = ForeignKey(
        Asset,
        on_delete=DO_NOTHING,
        db_column="domain_id",
        blank=True,
        null=True,
        related_name="system_unit_domains"
    )
    ip_address = CharField(max_length=20, blank=True, null=True)
    os = ForeignKey(
        Asset,
        on_delete=DO_NOTHING,
        db_column="os_id",
        blank=True,
        null=True,
        related_name="system_unit_operating_systems"
    )
    cpu = ForeignKey(
        Asset,
        on_delete=DO_NOTHING,
        db_column="cpu_id",
        blank=True,
        null=True,
        related_name="system_unit_cpus"
    )
    ram_capacity = ForeignKey(
        Asset,
        on_delete=DO_NOTHING,
        db_column="ram_capacity_id",
        blank=True,
        null=True,
        related_name="system_unit_ram_capacities"
    )
    disks = ForeignKey(
        Asset,
        on_delete=DO_NOTHING,
        db_column="disks_id",
        blank=True,
        null=True,
        related_name="system_unit_disks"
    )
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        app_label = "inventory"
        db_table = "system_units"


class Equipment(Model):
    id = AutoField(primary_key=True)
    equipment_type = ForeignKey(
        EquipmentType,
        on_delete=DO_NOTHING,
        db_column="equipment_type_id",
        blank=True,
        null=True,
        related_name="equipment"
    )
    model = ForeignKey(
        Asset,
        on_delete=DO_NOTHING,
        db_column="model_id",
        blank=True,
        null=True,
        related_name="equipment_models"
    )
    serial_number = CharField(max_length=64, blank=True, null=True)
    inventory_number = CharField(max_length=64, blank=True, null=True)
    mac_address = CharField(max_length=64, blank=True, null=True)
    print_color = ForeignKey(
        Asset,
        on_delete=DO_NOTHING,
        db_column="print_color_id",
        blank=True,
        null=True,
        related_name="equipment_print_colors"
    )
    antivirus = ForeignKey(
        Asset,
        on_delete=DO_NOTHING,
        db_column="antivirus_id",
        blank=True,
        null=True,
        related_name="equipment_antiviruses"
    )
    dlp = ForeignKey(
        Asset,
        on_delete=DO_NOTHING,
        db_column="dlp_id",
        blank=True,
        null=True,
        related_name="equipment_dlps"
    )
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        app_label = "inventory"
        db_table = "equipment"


class Workstation(Model):
    id = AutoField(primary_key=True)
    employee = ForeignKey(
        Employee,
        on_delete=DO_NOTHING,
        db_column="employee_id",
        blank=True,
        null=True,
        related_name="workstations"
    )
    system_unit = ForeignKey(
        SystemUnit,
        on_delete=DO_NOTHING,
        db_column="system_unit_id",
        blank=True,
        null=True,
        related_name="workstations"
    )
    monitor = ForeignKey(
        Equipment,
        on_delete=DO_NOTHING,
        db_column="monitor_id",
        blank=True,
        null=True,
        related_name="monitor_workstations"
    )
    printer = ForeignKey(
        Equipment,
        on_delete=DO_NOTHING,
        db_column="printer_id",
        blank=True,
        null=True,
        related_name="printer_workstations"
    )
    ip_phone = ForeignKey(
        Equipment,
        on_delete=DO_NOTHING,
        db_column="ip_phone_id",
        blank=True,
        null=True,
        related_name="ip_phone_workstations"
    )
    ups = ForeignKey(
        Equipment,
        on_delete=DO_NOTHING,
        db_column="ups_id",
        blank=True,
        null=True,
        related_name="ups_workstations"
    )
    iss = ForeignKey(
        Equipment,
        on_delete=DO_NOTHING,
        db_column="iss_id",
        blank=True,
        null=True,
        related_name="iss_workstations"
    )

    class Meta:
        app_label = "inventory"
        db_table = "workstations"


class ChangeLog(Model):
    id = AutoField(primary_key=True)
    employee = ForeignKey(
        Employee,
        on_delete=DO_NOTHING,
        db_column="employee_id",
        blank=True,
        null=True,
        related_name="change_logs"
    )
    admin_id = IntegerField(blank=True, null=True)
    workstation = ForeignKey(
        Workstation,
        on_delete=DO_NOTHING,
        db_column="workstation_id",
        blank=True,
        null=True,
        related_name="change_logs"
    )
    equipment_type = ForeignKey(
        EquipmentType,
        on_delete=DO_NOTHING,
        db_column="equipment_type_id",
        blank=True,
        null=True,
        related_name="change_logs"
    )
    field_name = CharField(max_length=64, blank=True, null=True)
    value_before = CharField(max_length=256, blank=True, null=True)
    value_after = CharField(max_length=256, blank=True, null=True)
    changed_at = DateTimeField(auto_now=True)

    class Meta:
        app_label = "inventory"
        db_table = "change_logs"
