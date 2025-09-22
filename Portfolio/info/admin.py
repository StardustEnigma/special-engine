from django.contrib import admin
from .models import TechTag, Project, ProjectImage

# Inline for ProjectImage (so you can add multiple screenshots in Project admin)
class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1  # Number of extra blank forms
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="height: 100px;" />'
        return ""
    image_preview.allow_tags = True
    image_preview.short_description = "Preview"


# Main Project Admin
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_featured', 'created_at', 'updated_at')
    list_filter = ('is_featured', 'tech_stack')
    search_fields = ('title', 'short_description', 'description')
    filter_horizontal = ('tech_stack',)
    inlines = [ProjectImageInline]


# TechTag Admin
@admin.register(TechTag)
class TechTagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# Optional: ProjectImage Admin (if you want to manage separately)
@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ('project', 'caption', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="height: 100px;" />'
        return ""
    image_preview.allow_tags = True
    image_preview.short_description = "Preview"

from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject_preview', 'created_at', 'is_read', 'replied')
    list_filter = ('is_read', 'replied', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at', 'message_preview')
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'subject')
        }),
        ('Message', {
            'fields': ('message_preview', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'replied', 'created_at')
        }),
    )

    def subject_preview(self, obj):
        return obj.subject[:50] + '...' if obj.subject and len(obj.subject) > 50 else obj.subject or 'No Subject'
    subject_preview.short_description = 'Subject'

    def message_preview(self, obj):
        preview = obj.message[:200] + '...' if len(obj.message) > 200 else obj.message
        return mark_safe(f'<div style="max-width: 400px; white-space: pre-wrap;">{preview}</div>')
    message_preview.short_description = 'Message Preview'

    def save_model(self, request, obj, form, change):
        if change and 'is_read' in form.changed_data:
            obj.is_read = True
        super().save_model(request, obj, form, change)
