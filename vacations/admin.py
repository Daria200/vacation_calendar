from django.contrib import admin

from .models import Vacation, PublicHolidays, ExtraDays

admin.site.register(Vacation)
admin.site.register(PublicHolidays)
admin.site.register(ExtraDays)