"""
Enhanced URL configuration for Portfolio project with SEO optimization,
caching, security, and performance improvements.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView
from django.http import HttpResponse
from django.utils import timezone
from pathlib import Path
from django.shortcuts import render
from . import views

# Cache timeout constants
CACHE_TIMEOUT_SHORT = 60 * 5      # 5 minutes
CACHE_TIMEOUT_MEDIUM = 60 * 30     # 30 minutes
CACHE_TIMEOUT_LONG = 60 * 60 * 24  # 24 hours

# SEO and Utility Views
def robots_txt(request):
    """Robots.txt for search engines"""
    lines = [
        "User-agent: *",
        "Allow: /",
        "Allow: /static/",
        "Allow: /media/",
        "Disallow: /admin/",
        "Disallow: /api/",
        "Disallow: /alt/",
        "",
        "# Sitemaps",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
        "",
        "# Crawl-delay for being respectful",
        "Crawl-delay: 1",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

def sitemap_xml(request):
    """Basic XML sitemap for SEO"""
    import xml.etree.ElementTree as ET
    from django.urls import reverse
    
    try:
        # Create XML sitemap
        urlset = ET.Element('urlset')
        urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        
        # Static pages with priorities
        pages = [
            {'path': 'home', 'changefreq': 'weekly', 'priority': '1.0'},
            {'path': 'about', 'changefreq': 'monthly', 'priority': '0.9'},
            {'path': 'skills', 'changefreq': 'monthly', 'priority': '0.8'},
            {'path': 'info:projects', 'changefreq': 'weekly', 'priority': '0.9'},
            {'path': 'info:contact', 'changefreq': 'monthly', 'priority': '0.7'},
        ]
        
        for page in pages:
            url = ET.SubElement(urlset, 'url')
            ET.SubElement(url, 'loc').text = request.build_absolute_uri(reverse(page['path']))
            ET.SubElement(url, 'lastmod').text = timezone.now().strftime('%Y-%m-%d')
            ET.SubElement(url, 'changefreq').text = page['changefreq']
            ET.SubElement(url, 'priority').text = page['priority']
        
        xml_content = ET.tostring(urlset, encoding='unicode')
        return HttpResponse(xml_content, content_type='application/xml')
        
    except Exception as e:
        return HttpResponse("Error generating sitemap", status=500)

def security_txt(request):
    """Security.txt for responsible disclosure"""
    lines = [
        "Contact: atharvamandle19@gmail.comv",  # Update with your email
        "Expires: 2025-12-31T23:59:59.000Z",
        "Preferred-Languages: en",
        "Canonical: https://atharvamandle.me/.well-known/security.txt",  # Update with your domain
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

def health_check(request):
    """Health check endpoint for monitoring"""
    try:
        return HttpResponse(
            f"OK - {timezone.now().isoformat()}",
            content_type="text/plain",
            status=200
        )
    except Exception as e:
        return HttpResponse(f"ERROR - {str(e)}", status=500)

# Main URL patterns with enhanced organization
urlpatterns = [
    # Admin interface (secured)
    path('admin/', admin.site.urls),
    
    # Core portfolio pages (cached for performance)
    path('', cache_page(CACHE_TIMEOUT_LONG)(views.HomeView.as_view()), name='home'),
    path('about/', cache_page(CACHE_TIMEOUT_LONG)(views.AboutView.as_view()), name='about'),
    path('skills/', cache_page(CACHE_TIMEOUT_LONG)(views.SkillsView.as_view()), name='skills'),
    path('contact/', views.ContactView.as_view(), name='contact'),  # No cache for contact form
    
    # Info app URLs (projects, contact, etc.)
    path('atharva/', include('info.urls', namespace='info')),
    
    # API endpoints with caching
    path('api/', include([
        path('skills/', cache_page(CACHE_TIMEOUT_MEDIUM)(views.skills_api), name='skills-api'),
        path('health/', health_check, name='health-check'),
    ])),
    
    # SEO and Utility URLs
    path('robots.txt', cache_page(CACHE_TIMEOUT_LONG)(robots_txt), name='robots-txt'),
    path('sitemap.xml', cache_page(CACHE_TIMEOUT_MEDIUM)(sitemap_xml), name='sitemap-xml'),
    path('.well-known/security.txt', cache_page(CACHE_TIMEOUT_LONG)(security_txt), name='security-txt'),
    
    # Redirects for common variations and SEO
    path('home/', RedirectView.as_view(url='/', permanent=True), name='home-redirect'),
    path('index/', RedirectView.as_view(url='/', permanent=True), name='index-redirect'),
    path('portfolio/', RedirectView.as_view(url='/atharva/projects/', permanent=True), name='portfolio-redirect'),
    path('work/', RedirectView.as_view(url='/atharva/projects/', permanent=True), name='work-redirect'),
    path('projects/', RedirectView.as_view(url='/atharva/projects/', permanent=True), name='projects-redirect'),
    
    # Alternative routes for testing/backup (no caching for development)
    path('alt/', include([
        path('home/', views.home_view, name='home-alt'),
        path('about/', views.about_view, name='about-alt'),
        path('contact/', views.contact_view_function, name='contact-alt'),
    ])),
]

# Get base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Development-specific URL patterns
if settings.DEBUG:
    # Development tools
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
        path('__debug__/', include('debug_toolbar.urls')) if 'debug_toolbar' in settings.INSTALLED_APPS else path('', lambda r: None),
    ]
    
    # Static and media files for development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Custom project files serving (if needed)
    urlpatterns += static('/projects/', document_root=BASE_DIR / 'projects')

# Production-specific patterns
else:
    # Error pages for production
    handler404 = 'Portfolio.views.custom_404'
    handler500 = 'Portfolio.views.custom_500'
    handler403 = 'Portfolio.views.custom_403'
    handler400 = 'Portfolio.views.custom_400'

# Advanced URL patterns with regex (if needed for complex routing)
urlpatterns += [
    # Catch-all for legacy URLs or redirects
    re_path(r'^legacy/(?P<path>.*)$', 
            RedirectView.as_view(url='/%(path)s', permanent=True), 
            name='legacy-redirect'),
    
    # Social media verification files (if needed)
    re_path(r'^(?P<filename>google[a-z0-9]+\.html)$', 
            lambda request, filename: HttpResponse(
                f'google-site-verification: {filename}', 
                content_type='text/html'
            ), 
            name='google-verification'),
]

# Admin customization
admin.site.site_header = "Atharva Mandle Portfolio Admin"
admin.site.site_title = "Portfolio Admin"
admin.site.index_title = "Welcome to Portfolio Administration"

# URL pattern for handling trailing slashes consistently
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^(.*)/$', 
                lambda request, path: RedirectView.as_view(
                    url=f'/{path}', 
                    permanent=True
                )(request) if path and not path.endswith('/') else None,
                name='remove-trailing-slash'),
    ]

# Security headers middleware can be added here if needed
# (or better handled in middleware.py)

# Custom error handlers for better UX
def custom_404(request, exception=None):
    """Custom 404 error page"""
    return render(request, '404.html', {
        'page_title': 'Page Not Found - Atharva Mandle',
        'error_code': 404,
        'error_message': 'The page you are looking for does not exist.',
    }, status=404)

def custom_500(request):
    """Custom 500 error page"""
    return render(request, '500.html', {
        'page_title': 'Server Error - Atharva Mandle',
        'error_code': 500,
        'error_message': 'Something went wrong on our end. Please try again later.',
    }, status=500)

def custom_403(request, exception=None):
    """Custom 403 error page"""
    return render(request, '403.html', {
        'page_title': 'Access Forbidden - Atharva Mandle',
        'error_code': 403,
        'error_message': 'You do not have permission to access this resource.',
    }, status=403)

def custom_400(request, exception=None):
    """Custom 400 error page"""
    return render(request, '400.html', {
        'page_title': 'Bad Request - Atharva Mandle',
        'error_code': 400,
        'error_message': 'Your browser sent a request that this server could not understand.',
    }, status=400)

# Performance monitoring URLs (for production)
if not settings.DEBUG and hasattr(settings, 'MONITORING_ENABLED') and settings.MONITORING_ENABLED:
    urlpatterns += [
        path('monitoring/', include([
            path('health/', health_check, name='monitoring-health'),
            path('status/', lambda r: HttpResponse('OK'), name='monitoring-status'),
        ])),
    ]
