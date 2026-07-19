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


class BaseEquipmentView(APIView):
    equipment_type = None
    serializer_class = None

    def get_queryset(self):
        if self.equipment_type is None:
            raise NotImplementedError(
                "Необходимо указать equipment_type"
            )

        return get_equipment_by_type(self.equipment_type)

    def get_serializer_class(self):
        if self.serializer_class is None:
            raise NotImplementedError(
                "Необходимо указать serializer_class"
            )

        return self.serializer_class

    def get(self, request, equipment_id=None):
        queryset = self.get_queryset()
        serializer_class = self.get_serializer_class()

        if equipment_id is not None:
            equipment = get_object_or_404(
                queryset,
                id=equipment_id
            )

            serializer = serializer_class(equipment)
            return Response(serializer.data)

        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data)

    def patch(self, request, equipment_id):
        queryset = self.get_queryset()
        serializer_class = self.get_serializer_class()

        equipment = get_object_or_404(
            queryset,
            id=equipment_id
        )

        serializer = serializer_class(
            equipment,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=HTTP_200_OK
        )


class Monitors(BaseEquipmentView):
    equipment_type = "monitor"
    serializer_class = MonitorSerializer


class Printers(BaseEquipmentView):
    equipment_type = "printer"
    serializer_class = PrinterSerializer


class IpPhones(BaseEquipmentView):
    equipment_type = "ip_phone"
    serializer_class = IpPhoneSerializer


class Ups(BaseEquipmentView):
    equipment_type = "ups"
    serializer_class = UpsSerializer


class Iss(BaseEquipmentView):
    equipment_type = "iss"
    serializer_class = IssSerializer


class Assets(APIView):
    def get(self, request, category_id=None):
        categories = Asset.objects.all()

        if category_id:
            categories = categories.filter(category_id=category_id)

        serializer = AssetsSerializer(categories, many=True)
        return Response(serializer.data)


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


@api_view(["GET"])
def asset_categories(request):
    categories = AssetCategory.objects.all()
    serializer = AssetCategoriesSerializer(categories, many=True)
    return Response(serializer.data)
