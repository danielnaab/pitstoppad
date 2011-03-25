from django.contrib import admin

from models import *

class ScheduleItemActionOptions(admin.TabularInline):
    model = ScheduleItemAction
    extra = 2
    
class ScheduleItemOptions(admin.ModelAdmin):
    inlines = [ScheduleItemActionOptions]

admin.site.register(Schedule)
admin.site.register(ScheduleItem, ScheduleItemOptions)
admin.site.register(ScheduleItemAction)
