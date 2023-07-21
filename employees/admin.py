from django.contrib import admin

from .models import Employee


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


admin.site.register(Employee, EmployeeAdmin)
