from django.shortcuts import get_object_or_404, get_list_or_404
from inventory.models import (
    Asset,
    AssetCategory,
    Employee,
    Equipment,
    SystemUnit,
    Workstation,
)
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
)
from rest_framework.decorators import APIView, api_view
from rest_framework.response import Response

from .serializers import (
    AssetCategoriesSerializer,
    AssetsSerializer,
    EmployeeReadSerializer,
    EmployeeWriteSerializer,
    IpPhoneSerializer,
    IssSerializer,
    MonitorSerializer,
    PrinterSerializer,
    SystemUnitReadSerializer,
    UpsSerializer,
    WorkstationSerializer,
)
from .services import (
    create_employee_with_workstation,
    create_workstation,
)


class Employees(APIView):
    def get(self, request, employee_id=None):
        employees = (
            Employee.objects
            .select_related("management")
            .filter(is_active=True)
        )

        if employee_id:
            employee = get_object_or_404(employees, id=employee_id)

            serializer = EmployeeReadSerializer(employee)
            return Response(serializer.data)

        serializer = EmployeeReadSerializer(
            employees,
            many=True,
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = EmployeeWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employee = create_employee_with_workstation(
            serializer.validated_data
        )

        response_serializer = EmployeeReadSerializer(employee)

        return Response(
            response_serializer.data,
            status=HTTP_201_CREATED
        )

    def patch(self, request, employee_id):
        employee = get_object_or_404(Employee, id=employee_id)

        serializer = EmployeeWriteSerializer(
            employee,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        updated_employee = serializer.save()

        response_serializer = EmployeeReadSerializer(updated_employee)
        return Response(
            response_serializer.data,
            status=HTTP_200_OK
        )

    def delete(self, request, employee_id):
        employee = get_object_or_404(
            Employee,
            id=employee_id,
            is_active=True
        )

        employee.is_active = False
        employee.save(update_fields=["is_active"])

        return Response(
            status=HTTP_204_NO_CONTENT
        )


class Workstations(APIView):
    def get(self, request, employee_id=None):
        workstations = (
            Workstation.objects
            .select_related("employee")
        )

        if employee_id:
            workstations = get_list_or_404(workstations, employee_id=employee_id)

            serializer = WorkstationSerializer(workstations, many=True)
            return Response(serializer.data)

        serializer = WorkstationSerializer(workstations, many=True)
        return Response(serializer.data)

    def post(self, request, employee_id):
        employee = get_object_or_404(
            Employee,
            id=employee_id,
            is_active=True,
        )

        workstation = create_workstation(employee)

        response_serializer = WorkstationSerializer(workstation)

        return Response(
            response_serializer.data,
            status=HTTP_201_CREATED,
        )


class SystemUnits(APIView):
    def get(self, request, system_unit_id=None):
        system_units = (
            SystemUnit.objects
            .select_related(
                "model",
                "domain",
                "os",
                "cpu",
                "ram_capacity",
                "disks",
            )
        )

        if system_unit_id:
            system_unit = get_object_or_404(system_units, id=system_unit_id)

            serializer = SystemUnitReadSerializer(system_unit)
            return Response(serializer.data)

        serializer = SystemUnitReadSerializer(system_units, many=True)
        return Response(serializer.data)

    def patch(self, request, system_unit_id):
        system_unit = get_object_or_404(SystemUnit, id=system_unit_id)

        serializer = SystemUnitReadSerializer(
            system_unit,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        updated_system_unit = serializer.save()

        response_serializer = SystemUnitReadSerializer(updated_system_unit)
        return Response(
            response_serializer.data,
            status=HTTP_200_OK
        )


class Monitors(APIView):
    def get(self, request, monitor_id=None):
        monitors = get_equipment_by_type("monitor")

        if monitor_id:
            monitor = get_object_or_404(monitors, id=monitor_id)

            serializer = MonitorSerializer(monitor)
            return Response(serializer.data)

        serializer = MonitorSerializer(monitors, many=True)
        return Response(serializer.data)

    def patch(self, request, monitor_id):
        monitors = get_equipment_by_type("monitor")

        monitor = get_object_or_404(monitors, id=monitor_id)

        serializer = MonitorSerializer(
            monitor,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        updated_monitor = serializer.save()

        response_serializer = MonitorSerializer(updated_monitor)
        return Response(
            response_serializer.data,
            status=HTTP_200_OK
        )


class Printers(APIView):
    def get(self, request, printer_id=None):
        printers = get_equipment_by_type("printer")

        if printer_id:
            printer = get_object_or_404(printers, id=printer_id)

            serializer = PrinterSerializer(printer)
            return Response(serializer.data)

        serializer = PrinterSerializer(printers, many=True)
        return Response(serializer.data)

    def patch(self, request, printer_id):
        printers = get_equipment_by_type("printer")

        printer = get_object_or_404(printers, id=printer_id)

        serializer = PrinterSerializer(
            printer,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        updated_printer = serializer.save()

        response_serializer = PrinterSerializer(updated_printer)
        return Response(
            response_serializer.data,
            status=HTTP_200_OK
        )


class IpPhones(APIView):
    def get(self, request, ip_phone_id=None):
        ip_phones = get_equipment_by_type("ip_phone")

        if ip_phone_id:
            ip_phone = get_object_or_404(ip_phones, id=ip_phone_id)

            serializer = IpPhoneSerializer(ip_phone)
            return Response(serializer.data)

        serializer = IpPhoneSerializer(ip_phones, many=True)
        return Response(serializer.data)

    def patch(self, request, ip_phone_id):
        ip_phones = get_equipment_by_type("ip_phone")

        ip_phone = get_object_or_404(ip_phones, id=ip_phone_id)

        serializer = IpPhoneSerializer(
            ip_phone,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        updated_ip_phone = serializer.save()

        response_serializer = IpPhoneSerializer(updated_ip_phone)
        return Response(
            response_serializer.data,
            status=HTTP_200_OK
        )


class Ups(APIView):
    def get(self, request, ups_id=None):
        ups = get_equipment_by_type("ups")

        if ups_id:
            current_ups = get_object_or_404(ups, id=ups_id)

            serializer = UpsSerializer(current_ups)
            return Response(serializer.data)

        serializer = UpsSerializer(ups, many=True)
        return Response(serializer.data)

    def patch(self, request, ups_id):
        ups = get_equipment_by_type("ups")

        current_ups = get_object_or_404(ups, id=ups_id)

        serializer = UpsSerializer(
            current_ups,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        updated_ups = serializer.save()

        response_serializer = UpsSerializer(updated_ups)
        return Response(
            response_serializer.data,
            status=HTTP_200_OK
        )


class Iss(APIView):
    def get(self, request, iss_id=None):
        iss = get_equipment_by_type("iss")

        if iss_id:
            current_iss = get_object_or_404(iss, id=iss_id)

            serializer = IssSerializer(current_iss)
            return Response(serializer.data)

        serializer = IssSerializer(iss, many=True)
        return Response(serializer.data)

    def patch(self, request, iss_id):
        iss = get_equipment_by_type("iss")

        current_iss = get_object_or_404(iss, id=iss_id)

        serializer = IssSerializer(
            current_iss,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        updated_iss = serializer.save()

        response_serializer = IssSerializer(updated_iss)
        return Response(
            response_serializer.data,
            status=HTTP_200_OK
        )


def get_equipment_by_type(code):
    return (
        Equipment.objects
        .select_related(
            "equipment_type",
            "model",
            "print_color",
            "antivirus",
            "dlp",
        )
        .filter(equipment_type__code=code)
    )


class Assets(APIView):
    def get(self, request, category_id=None):
        categories = Asset.objects.all()

        if category_id:
            categories = categories.filter(category_id=category_id)

        serializer = AssetsSerializer(categories, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def asset_categories(request):
    categories = AssetCategory.objects.all()
    serializer = AssetCategoriesSerializer(categories, many=True)
    return Response(serializer.data)
