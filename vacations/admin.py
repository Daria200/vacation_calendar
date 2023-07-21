from django.contrib import admin

from .models import Vacation, PublicHolidays, AvailableDays


class PublicHolidaysAdmin(admin.ModelAdmin):
    list_display = ["city", "date"]
    list_filter = ["city"]


class VacationAdmin(admin.ModelAdmin):
    list_display = [
        "employee_name",
        "employee_surname",
        "date",
        "full_day",
        "type",
        "description",
    ]
    search_fields = ["employee__user__last_name", "employee__user__first_name"]

    list_filter = [
        "date",
        "employee__user__last_name",
    ]
    list_per_page = 30

    def employee_name(self, obj):
        return obj.employee.user.first_name

    def employee_surname(self, obj):
        return obj.employee.user.last_name

    employee_name.short_description = "First Name"
    employee_surname.short_description = "Last Name"


admin.site.register(Vacation, VacationAdmin)
admin.site.register(PublicHolidays, PublicHolidaysAdmin)
admin.site.register(AvailableDays)
