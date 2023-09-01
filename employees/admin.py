from django import forms
from django.contrib import admin

from .models import City, Employee


class EmployeeAdminForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(EmployeeAdminForm, self).__init__(*args, **kwargs)
        # Customize the way the user field is displayed in the admin form
        self.fields["user"].label_from_instance = self.get_user_display_name

    def get_user_display_name(self, user):
        return f"{user.first_name} {user.last_name}"


class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeAdminForm
    list_display = ["name", "surname", "city", "display_manager", "is_manager"]
    list_display_links = [
        "name",
        "surname",
    ]
    list_filter = [
        "city",
        "manager",
    ]
    list_editable = ["is_manager"]
    # TODO: Search does not work
    search_fields = ["user__first_name", "user__last_name", "city"]
    list_per_page = 25

    def name(self, obj):
        return obj.user.first_name

    def surname(self, obj):
        return obj.user.last_name

    def display_manager(self, obj):
        if obj.manager:
            return f"{obj.manager.first_name} {obj.manager.last_name}"
        return None

    display_manager.short_description = "Manager"
    name.short_description = "First Name"
    surname.short_description = "Last Name"


class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "state"]
    list_filter = ["state"]
    search_fields = ["name", "state"]


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(City, CityAdmin)
