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
)
from rest_framework.validators import ValidationError


class EmployeeReadSerializer(ModelSerializer):
    management = CharField(
        source="management.name"
    )

    class Meta:
        model = Employee
        fields = [
            "id",
            "fullname",
            "cabinet",
            "management"
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

    model = CharField(source="model.name")
    domain = CharField(source="domain.name")
    os = CharField(source="os.name")
    cpu = CharField(source="cpu.name")
    ram_capacity = CharField(source="ram_capacity.name")
    disks = CharField(source="disks.name")

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

    model = CharField(source="model.name", read_only=True)

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

    model = CharField(source="model.name", read_only=True)
    print_color = CharField(source="print_color.name", read_only=True)

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

    model = CharField(source="model.name", read_only=True)

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

    model = CharField(source="model.name", read_only=True)

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

    antivirus = CharField(source="antivirus.name", read_only=True)
    dlp = CharField(source="dlp.name", read_only=True)

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
