from django.contrib import admin

from .models import Employee, City, GERMAN_STATES


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["name", "surname", "city", "manager", "is_manager"]
    list_display_links = [
        "name",
        "surname",
    ]
    list_filter = ["city", "manager"]
    list_editable = ["is_manager"]
    # TODO: Search does not work
    search_fields = ["user__first_name", "user__last_name", "city"]
    list_per_page = 25

    def name(self, obj):
        return obj.user.first_name

    def surname(self, obj):
        return obj.user.last_name

    name.short_description = "First Name"
    surname.short_description = "Last Name"


class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "state"]
    list_filter = ["state"]
    search_fields = ["name", "state"]


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(City, CityAdmin)
