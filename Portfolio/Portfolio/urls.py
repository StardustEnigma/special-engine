"""
URL configuration for Portfolio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

# Main URL patterns
urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Main portfolio pages
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('skills/', views.SkillsView.as_view(), name='skills'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    
    # API endpoints
    path('api/skills/', views.skills_api, name='skills-api'),
    
    # Alternative function-based view routes (for testing/backup)
    path('alt/home/', views.home_view, name='home-alt'),
    path('alt/about/', views.about_view, name='about-alt'),
    path('alt/contact/', views.contact_view, name='contact-alt'),
    path('projects/', views.ProjectsView.as_view(), name='projects'),
]

# Development-only URL patterns
if settings.DEBUG:
    # Django browser reload for development
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    
    # Serve media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
