from rest_framework.decorators import api_view, APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from inventory.models import Employee, Workstation, SystemUnit, Equipment, AssetCategory, Asset
from .serializers import EmployeeReadSerializer, EmployeeWriteSerializer, WorkstationSerializer, SystemUnitSerializer, \
    MonitorSerializer, PrinterSerializer, IpPhoneSerializer, UpsSerializer, IssSerializer, AssetCategoriesSerializer, \
    AssetsSerializer

class Employees(APIView):
    def get(self, request):
        employees = (
            Employee.objects
            .select_related("management")
        )

        serializer = EmployeeReadSerializer(employees, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EmployeeWriteSerializer(data=request.data)

        if serializer.is_valid():
            employee = serializer.save()

            response_serializer = EmployeeReadSerializer(employee)

            return Response(
                response_serializer.data,
                status=201
            )

        return Response(
            serializer.errors,
            status=400
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
            status=status.HTTP_200_OK
        )


@api_view(["GET"])
def workstations(request):
    workstations = (
        Workstation.objects
        .select_related("employee")
    )

    serializer = WorkstationSerializer(workstations, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def system_units(request):
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

    serializer = SystemUnitSerializer(system_units, many=True)
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
def monitors(request):
    equipment = get_equipment_by_type("monitor")
    serializer = MonitorSerializer(equipment, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def printers(request):
    equipment = get_equipment_by_type("printer")
    serializer = PrinterSerializer(equipment, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def ip_phones(request):
    equipment = get_equipment_by_type("ip_phone")
    serializer = IpPhoneSerializer(equipment, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def ups(request):
    equipment = get_equipment_by_type("ups")
    serializer = UpsSerializer(equipment, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def iss(request):
    equipment = get_equipment_by_type("iss")
    serializer = IssSerializer(equipment, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def asset_categories(request):
    categories = AssetCategory.objects.all()
    serializer = AssetCategoriesSerializer(categories, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def assets(request):
    categories = Asset.objects.all()
    serializer = AssetsSerializer(categories, many=True)
    return Response(serializer.data)
