from inventory.models import (
    Asset,
    AssetCategory,
    Employee,
    Equipment,
    Management,
    SystemUnit,
    Workstation,
)
from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    Serializer,
    SerializerMethodField,
    SlugRelatedField,
)
from rest_framework.validators import ValidationError


class EmployeeReadSerializer(ModelSerializer):
    department = CharField(
        source="department.name", read_only=True, allow_null=True
    )
    management = CharField(
        source="management.name"
    )

    class Meta:
        model = Employee
        fields = [
            "id",
            "fullname",
            "cabinet",
            "management",
            "department",
        ]


class EmployeeWriteSerializer(ModelSerializer):
    management = CharField()

    class Meta:
        model = Employee
        fields = [
            "fullname",
            "cabinet",
            "management",
        ]

    def validate(self, attrs):
        management_name = attrs.get("management")

        management, _ = Management.objects.get_or_create(
            name=management_name
        )

        duplicate_exists = Employee.objects.filter(
            fullname=attrs.get("fullname"),
            cabinet=attrs.get("cabinet"),
            management=management,
        ).exists()

        if duplicate_exists:
            raise ValidationError(
                {
                    "non_field_errors": [
                        "Такой сотрудник уже существует."
                    ]
                }
            )

        attrs["management"] = management

        return attrs


class EmployeeShortSerializer(ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "id",
            "fullname",
        ]


class EmployeeMixin(Serializer):
    employee = SerializerMethodField()

    employee_relation = None

    def get_employee(self, obj):
        if self.employee_relation is None:
            return None

        workstation = getattr(obj, self.employee_relation).first()

        if not workstation or not workstation.employee:
            return None

        return EmployeeShortSerializer(workstation.employee).data


class WorkstationSerializer(ModelSerializer):
    employee = EmployeeShortSerializer(read_only=True)
    system_unit = SerializerMethodField()
    monitor = SerializerMethodField()
    printer = SerializerMethodField()
    ip_phone = SerializerMethodField()
    ups = SerializerMethodField()
    iss = SerializerMethodField()

    class Meta:
        model = Workstation
        fields = [
            "id",
            "employee",
            "system_unit",
            "monitor",
            "printer",
            "ip_phone",
            "ups",
            "iss",
        ]

    def get_system_unit(self, obj):
        su = obj.system_unit

        if not su:
            return None

        return {
            "id": su.id,
            "model": su.model.name if su.model else None,
            "serial_number": su.serial_number,
            "inventory_number": su.inventory_number,
            "computer_name": su.computer_name,
            "account": su.account,
            "domain": su.domain.name if su.domain else None,
            "ip": su.ip_address,
            "os": su.os.name if su.os else None,
            "cpu": su.cpu.name if su.cpu else None,
            "ram_capacity": su.ram_capacity.name if su.ram_capacity else None,
            "disks": su.disks.name if su.disks else None,
        }

    def get_monitor(self, obj):
        monitor = obj.monitor

        if not monitor:
            return None

        return {
            "id": monitor.id,
            "model": monitor.model.name if monitor.model else None,
            "serial_number": monitor.serial_number,
            "inventory_number": monitor.inventory_number,
        }

    def get_printer(self, obj):
        printer = obj.printer

        if not printer:
            return None

        return {
            "id": printer.id,
            "model": printer.model.name if printer.model else None,
            "print_color": printer.print_color.name if printer.print_color else None,
            "serial_number": printer.serial_number,
            "inventory_number": printer.inventory_number,
        }

    def get_ip_phone(self, obj):
        phone = obj.ip_phone

        if not phone:
            return None

        return {
            "id": phone.id,
            "model": phone.model.name if phone.model else None,
            "mac_address": phone.mac_address,
            "serial_number": phone.serial_number,
            "inventory_number": phone.inventory_number,
        }

    def get_ups(self, obj):
        ups = obj.ups

        if not ups:
            return None

        return {
            "id": ups.id,
            "model": ups.model.name if ups.model else None,
            "serial_number": ups.serial_number,
            "inventory_number": ups.inventory_number,
        }

    def get_iss(self, obj):
        iss = obj.iss

        if not iss:
            return None

        return {
            "id": iss.id,
            "antivirus": iss.antivirus.name if iss.antivirus else None,
            "dlp": iss.dlp.name if iss.dlp else None,
        }


class SystemUnitReadSerializer(EmployeeMixin, ModelSerializer):
    employee_relation = "workstations"

    model = CharField(source="model.name", read_only=True, allow_null=True)
    domain = CharField(source="domain.name", read_only=True, allow_null=True)
    os = CharField(source="os.name", read_only=True, allow_null=True)
    cpu = CharField(source="cpu.name", read_only=True, allow_null=True)
    ram_capacity = CharField(source="ram_capacity.name", read_only=True, allow_null=True)
    disks = CharField(source="disks.name", read_only=True, allow_null=True)

    class Meta:
        model = SystemUnit
        fields = [
            "id",
            "employee",
            "model",
            "serial_number",
            "inventory_number",
            "computer_name",
            "account",
            "domain",
            "ip_address",
            "os",
            "cpu",
            "ram_capacity",
            "disks",
        ]


class MonitorSerializer(EmployeeMixin, ModelSerializer):
    employee_relation = "monitor_workstations"

    model = CharField(source="model.name", read_only=True, allow_null=True)

    class Meta:
        model = Equipment
        fields = [
            "id",
            "employee",
            "model",
            "serial_number",
            "inventory_number",
        ]


class PrinterSerializer(EmployeeMixin, ModelSerializer):
    employee_relation = "printer_workstations"

    model = CharField(source="model.name", read_only=True, allow_null=True)
    print_color = CharField(source="print_color.name", read_only=True, allow_null=True)

    class Meta:
        model = Equipment
        fields = [
            "id",
            "employee",
            "model",
            "print_color",
            "serial_number",
            "inventory_number",
        ]


class IpPhoneSerializer(EmployeeMixin, ModelSerializer):
    employee_relation = "ip_phone_workstations"

    model = CharField(source="model.name", read_only=True, allow_null=True)

    class Meta:
        model = Equipment
        fields = [
            "id",
            "employee",
            "model",
            "mac_address",
            "serial_number",
            "inventory_number",
        ]


class UpsSerializer(EmployeeMixin, ModelSerializer):
    employee_relation = "ups_workstations"

    model = CharField(source="model.name", read_only=True, allow_null=True)

    class Meta:
        model = Equipment
        fields = [
            "id",
            "employee",
            "model",
            "serial_number",
            "inventory_number",
        ]


class IssSerializer(ModelSerializer, EmployeeMixin):
    employee_relation = "iss_workstations"

    antivirus = CharField(source="antivirus.name", read_only=True, allow_null=True)
    dlp = CharField(source="dlp.name", read_only=True, allow_null=True)

    class Meta:
        model = Equipment
        fields = [
            "id",
            "employee",
            "antivirus",
            "dlp",
        ]

class AssetCategoriesSerializer(ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = [
            "id",
            "name",
            "code"
        ]

class AssetsSerializer(ModelSerializer):
    code = CharField(source="category.code", read_only=True)

    class Meta:
        model = Asset
        fields = [
            "id",
            "name",
            "code"
        ]


SYSTEM_UNIT_ASSET_CATEGORIES = {
    "model": "system_unit_model",
    "domain": "domain",
    "os": "os",
    "cpu": "cpu",
    "ram_capacity": "ram_capacity",
    "disks": "disks",
}


class SystemUnitWriteSerializer(ModelSerializer):
    class Meta:
        model = SystemUnit
        fields = [
            "model", "domain", "os", "cpu", "ram_capacity", "disks",
            "serial_number", "inventory_number", "computer_name", "account",
            "ip_address",
        ]

    def get_fields(self):
        fields = super().get_fields()
        for name, code in SYSTEM_UNIT_ASSET_CATEGORIES.items():
            fields[name] = SlugRelatedField(
                slug_field="name",
                queryset=Asset.objects.filter(category__code=code),
                required=False,
                allow_null=True,
            )
        return fields


EQUIPMENT_ASSET_CATEGORIES = {
    "monitor": {"model": "monitor_model"},
    "printer": {"model": "printer_model", "print_color": "print_color"},
    "ip_phone": {"model": "ip_phone_model"},
    "ups": {"model": "ups_model"},
    "iss": {"antivirus": "antivirus", "dlp": "dlp"},
}


class EquipmentWriteSerializer(ModelSerializer):
    class Meta:
        model = Equipment
        fields = [
            "model", "print_color", "antivirus", "dlp", "serial_number",
            "inventory_number", "mac_address",
        ]

    def get_fields(self):
        fields = super().get_fields()
        equipment_type = self.context["equipment_type"]
        categories = EQUIPMENT_ASSET_CATEGORIES[equipment_type]
        allowed = set(categories)
        if equipment_type != "iss":
            allowed.update(("serial_number", "inventory_number"))
        if equipment_type == "ip_phone":
            allowed.add("mac_address")
        fields = {name: field for name, field in fields.items() if name in allowed}
        for name, code in categories.items():
            fields[name] = SlugRelatedField(
                slug_field="name",
                queryset=Asset.objects.filter(category__code=code),
                required=False,
                allow_null=True,
            )
        return fields
