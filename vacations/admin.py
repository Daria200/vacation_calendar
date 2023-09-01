import calendar

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    AvailableDays,
    PublicHolidays,
    VacationDay,
    Request,
)


class MonthFilter(admin.SimpleListFilter):
    title = _("Month")
    parameter_name = "month"

    def lookups(self, request, model_admin):
        return [(str(i), calendar.month_name[i]) for i in range(1, 13)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date__month=int(self.value()))


class PublicHolidaysAdmin(admin.ModelAdmin):
    list_display = ["date", "name", "in_cities"]

    list_filter = [
        "cities",
    ]

    def in_cities(self, day):
        return ",\n".join([city.name for city in day.cities.all()])


class VacationDayAdmin(admin.ModelAdmin):
    list_display = [
        "employee_name",
        "employee_surname",
        "date",
        "duration",
        "type",
        "description",
        "approved",
    ]
    search_fields = ["employee__user__last_name", "employee__user__first_name"]

    list_filter = [
        "type",
        "employee__user__last_name",
        MonthFilter,
    ]
    list_per_page = 30

    def employee_name(self, obj):
        return obj.employee.user.first_name

    def employee_surname(self, obj):
        return obj.employee.user.last_name

    employee_name.short_description = "First Name"
    employee_surname.short_description = "Last Name"


class AvailableDaysAdmin(admin.ModelAdmin):
    list_display = [
        "employee_name",
        "employee_surname",
        "year",
        "allotted_days",
        "transferred_days",
    ]
    list_filter = ["employee__user__last_name", "year"]
    search_fields = ["employee__user__last_name", "employee__user__first_name"]
    list_display_links = ["employee_name", "employee_surname"]

    def employee_name(self, obj):
        return obj.employee.user.first_name

    def employee_surname(self, obj):
        return obj.employee.user.last_name


class RequestAdmin(admin.ModelAdmin):
    list_display = [
        "employee_name",
        "employee_surname",
        "request_type",
        "start_date",
        "end_date",
        "request_status",
        "created_at",
        "last_modified",
    ]
    search_fields = ["employee__user__last_name", "employee__user__first_name"]
    list_display_links = ["employee_name", "employee_surname"]

    def employee_name(self, obj):
        return obj.employee.user.first_name

    def employee_surname(self, obj):
        return obj.employee.user.last_name


admin.site.register(VacationDay, VacationDayAdmin)
admin.site.register(PublicHolidays, PublicHolidaysAdmin)
admin.site.register(AvailableDays, AvailableDaysAdmin)
admin.site.register(Request, RequestAdmin)
