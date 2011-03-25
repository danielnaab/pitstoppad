from django.contrib import admin

from models import *

class MaintenanceActionOptions(admin.TabularInline):
    model = MaintenanceAction
    extra = 2

class FillupActionOptions(admin.TabularInline):
    model = FillupAction
    extra = 2

class MaintenanceLogOptions(admin.ModelAdmin):
    inlines = [MaintenanceActionOptions, FillupActionOptions]

admin.site.register(MaintenanceLog, MaintenanceLogOptions)
