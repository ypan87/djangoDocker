from django.contrib import admin
from .models import TestPoints, Turbo, Project

# Register your models here.
class TurboAdmin(admin.ModelAdmin):
    list_display = ["category", "cut_back", "diameter", "fix_loss_one", "fix_loss_two", "var_loss", "size_correction"]
    search_fields = ["category", "cut_back", "diameter", "fix_loss_one", "fix_loss_two", "var_loss", "size_correction"]
    list_filter = ["category", "cut_back", "diameter", "fix_loss_one", "fix_loss_two", "var_loss", "size_correction"]

class TestPointsAdmin(admin.ModelAdmin):
    list_display = ["category", "working_condition", "working_position", "flow_coef", "pressure_coef", "efficiency", "flow_factor", "pressure_factor", "efficiency_factor"]
    search_fields = ["category", "working_condition", "working_position", "flow_coef", "pressure_coef", "efficiency", "flow_factor", "pressure_factor", "efficiency_factor"]
    list_filter = ["category", "working_condition", "working_position"]

class ProjectAdmin(admin.ModelAdmin):
    list_display = ["project_name", "project_index", "project_address", "project_engineer", "creator", "create_time"]
    search_fields = ["project_name", "project_index", "project_address", "project_engineer", "creator", "create_time"]
    list_filter = ["project_name", "project_index", "project_address", "project_engineer", "creator", "create_time"]

admin.site.register(TestPoints, TestPointsAdmin)
admin.site.register(Turbo, TurboAdmin)
admin.site.register(Project, ProjectAdmin)
