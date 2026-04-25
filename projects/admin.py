from django.contrib import admin

from projects.models import Project, Skill


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'participants_count',
                    'status', 'created_at')
    list_filter = ('status', 'skills')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)

    @admin.display(description='Участники')
    def participants_count(self, obj):
        return obj.participants.count()


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
