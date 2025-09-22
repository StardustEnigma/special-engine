from django.urls import path, re_path
from django.views.decorators.cache import cache_page
from . import views

app_name = 'info'

# Cache timeouts
CACHE_TIMEOUT_SHORT = 60 * 5   # 5 minutes
CACHE_TIMEOUT_MEDIUM = 60 * 30  # 30 minutes
CACHE_TIMEOUT_LONG = 60 * 60 * 24  # 24 hours

urlpatterns = [
    # Main projects page with SEO-friendly URL
    path('projects/', views.projects_view, name='projects'),
    
    # Projects with pagination
    path('projects/page/<int:page>/', views.projects_view, name='projects_page'),
    
    # Projects filtered by technology (SEO-friendly)
    path('projects/tech/<str:tech_name>/', views.projects_view, name='projects_by_tech'),
    
    # Project detail page with SEO-friendly slug
    path('projects/<int:project_id>/<slug:slug>/', views.project_detail_view, name='project_detail'),
    path('projects/<int:project_id>/', views.project_detail_view, name='project_detail_simple'),
    
    # Contact page
    path('contact/', views.contact_view, name='contact'),
    
    # AJAX endpoints (API-like structure)
    path('api/projects/<int:project_id>/', views.project_detail_ajax, name='project_detail_ajax'),
    path('api/projects/filter/', views.filter_projects_ajax, name='filter_projects_ajax'),
    path('api/contact/copy-email/', views.copy_email_ajax, name='copy_email_ajax'),
    path('api/contact/typing-simulation/', views.typing_simulation_ajax, name='typing_simulation_ajax'),
    
    # Health check endpoint for monitoring
    path('health/', views.health_check, name='health_check'),
    
    # SEO and utility endpoints
    path('sitemap/projects/', views.projects_sitemap, name='projects_sitemap'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    
    # RSS feed for projects
    path('projects/feed/', views.projects_feed, name='projects_feed'),
    
    # Admin utility endpoints (for authenticated users)
    path('admin/cache-clear/', views.clear_cache, name='clear_cache'),
    path('admin/stats/', views.admin_stats, name='admin_stats'),
]

# Optional: Add regex patterns for more complex URLs
urlpatterns += [
    # Catch-all for project slugs (fallback)
    re_path(r'^projects/(?P<project_id>\d+)/(?P<slug>[\w-]+)/$', 
            views.project_detail_view, 
            name='project_detail_slug'),
    
    # Legacy URL redirects (if you had old URLs)
    re_path(r'^project/(?P<project_id>\d+)/$', 
            views.project_legacy_redirect, 
            name='project_legacy_redirect'),
]
