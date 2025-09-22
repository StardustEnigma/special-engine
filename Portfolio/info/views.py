from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404, HttpResponse, HttpResponsePermanentRedirect
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch, Count
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.utils.html import strip_tags
from django.db import transaction
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed

import json
import logging
import re
from typing import Optional, Dict, Any, List
import xml.etree.ElementTree as ET

from .models import Project, TechTag, ProjectImage, ContactMessage

# Set up logging
logger = logging.getLogger(__name__)

# Cache timeout constants
CACHE_TIMEOUT_SHORT = 60 * 5  # 5 minutes
CACHE_TIMEOUT_MEDIUM = 60 * 30  # 30 minutes
CACHE_TIMEOUT_LONG = 60 * 60 * 24  # 24 hours


def projects_view(request, page=None, tech_name=None):
    """
    FIXED: Enhanced projects page view - removed problematic query slicing
    """
    try:
        # Handle URL parameters
        if page:
            request.GET = request.GET.copy()
            request.GET['page'] = page
            
        if tech_name:
            request.GET = request.GET.copy()
            request.GET['tech'] = tech_name.replace('-', ' ')
        
        # Get search parameters
        search_query = request.GET.get('search', '').strip()
        tech_filter = request.GET.get('tech', '').strip()
        page_number = request.GET.get('page', '1')
        
        # Validate and sanitize inputs
        if search_query:
            search_query = strip_tags(search_query)[:100]
        
        if tech_filter:
            tech_filter = strip_tags(tech_filter)[:50]
        
        # FIXED: Simplified query without problematic Prefetch
        projects_query = Project.objects.select_related().prefetch_related('tech_stack', 'images')
        
        # Apply filters
        if search_query:
            projects_query = projects_query.filter(
                Q(title__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(tech_stack__name__icontains=search_query)
            ).distinct()
        
        if tech_filter:
            if TechTag.objects.filter(name__icontains=tech_filter).exists():
                projects_query = projects_query.filter(tech_stack__name__icontains=tech_filter)
            else:
                print(f"WARNING: Invalid tech filter attempted: {tech_filter}")
        
        # Order projects
        projects_query = projects_query.order_by('-created_at', '-id')
        
        # Get total count for SEO
        total_projects = projects_query.count()
        
        # Pagination with error handling
        paginator = Paginator(projects_query, 6)
        
        try:
            page_number = int(page_number)
            projects_page = paginator.get_page(page_number)
        except (ValueError, TypeError):
            projects_page = paginator.get_page(1)
        except EmptyPage:
            raise Http404("Page not found")
        
        # Get tech tags for filter (simplified)
        tech_tags = list(TechTag.objects.values('name', 'id').order_by('name'))
        
        # SEO Meta Data
        page_title = "Projects - Atharva Mandle | Full Stack Developer Portfolio"
        page_description = f"Explore {total_projects} innovative projects built with Django, React, Machine Learning, and modern web technologies."
        
        if search_query:
            page_title = f"Projects: {search_query} - Atharva Mandle"
            page_description = f"Search results for '{search_query}' in Atharva Mandle's project portfolio."
        
        if tech_filter:
            page_title = f"{tech_filter} Projects - Atharva Mandle"
            page_description = f"Projects built with {tech_filter} technology."
        
        # FIXED: Simplified structured data without problematic slice
        structured_data = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Projects Portfolio",
            "description": page_description,
            "creator": {
                "@type": "Person",
                "name": "Atharva Mandle",
                "jobTitle": "Full Stack Developer",
                "url": request.build_absolute_uri('/'),
            },
            "mainEntity": {
                "@type": "ItemList",
                "numberOfItems": total_projects,
            }
        }
        
        context = {
            'projects': projects_page,
            'tech_tags': tech_tags,
            'search_query': search_query,
            'tech_filter': tech_filter,
            'total_projects': total_projects,
            'page_title': page_title,
            'page_description': page_description,
            'structured_data': json.dumps(structured_data),
            'canonical_url': request.build_absolute_uri(request.path),
            'current_page': projects_page.number,
            'total_pages': projects_page.paginator.num_pages,
            'keywords': f"Django projects, React applications, {tech_filter}, full stack development, machine learning",
            'author': 'Atharva Mandle',
            'robots': 'index, follow',
        }
        
        print(f"Projects view served - {total_projects} projects, page {projects_page.number}")
        return render(request, 'projects.html', context)
        
    except Exception as e:
        print(f"Error in projects_view: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Fallback context for error cases
        context = {
            'projects': [],
            'tech_tags': [],
            'search_query': '',
            'tech_filter': '',
            'total_projects': 0,
            'page_title': 'Projects - Atharva Mandle',
            'page_description': 'Full-stack developer portfolio showcasing innovative projects.',
            'error_message': 'Sorry, there was an issue loading the projects. Please try again.',
        }
        return render(request, 'projects.html', context, status=500)


@require_GET
def project_detail_view(request, project_id: int, slug: str = None):
    """
    Enhanced project detail view with caching, SEO optimization, and slug support
    """
    try:
        # Optimized query with prefetch
        project = get_object_or_404(
            Project.objects.select_related().prefetch_related(
                'tech_stack',
                'images'
            ),
            id=project_id
        )
        
        # Generate the correct slug
        correct_slug = slugify(project.title)
        
        # Redirect to correct URL if slug is missing or incorrect
        if slug and slug != correct_slug:
            return HttpResponsePermanentRedirect(
                reverse('info:project_detail', 
                       kwargs={'project_id': project_id, 'slug': correct_slug})
            )
        
        # If no slug provided, redirect to include slug
        if not slug:
            return HttpResponsePermanentRedirect(
                reverse('info:project_detail', 
                       kwargs={'project_id': project_id, 'slug': correct_slug})
            )
        
        # Get related projects
        related_projects = Project.objects.filter(
            tech_stack__in=project.tech_stack.all()
        ).exclude(id=project.id).distinct()[:4]
        
        # SEO Meta Data
        page_title = f"{project.title} - Project Details | Atharva Mandle"
        page_description = f"{project.short_description} Built with {', '.join([tag.name for tag in project.tech_stack.all()[:3]])} and more technologies."
        
        # Structured data for project
        structured_data = {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": project.title,
            "description": project.description,
            "creator": {
                "@type": "Person",
                "name": "Atharva Mandle",
                "jobTitle": "Full Stack Developer"
            },
            "dateCreated": project.created_at.isoformat(),
            "keywords": ", ".join([tag.name for tag in project.tech_stack.all()]),
            "url": request.build_absolute_uri(),
        }
        
        if project.thumbnail:
            structured_data["image"] = request.build_absolute_uri(project.thumbnail.url)
        
        if project.github_link:
            structured_data["codeRepository"] = project.github_link
        
        if project.live_demo_link:
            structured_data["url"] = project.live_demo_link
        
        context = {
            'project': project,
            'project_images': project.images.all(),
            'related_projects': related_projects,
            'page_title': page_title,
            'page_description': page_description,
            'structured_data': json.dumps(structured_data),
            'canonical_url': request.build_absolute_uri(),
            'keywords': f"{project.title}, {', '.join([tag.name for tag in project.tech_stack.all()])}, project showcase",
            'author': 'Atharva Mandle',
            'robots': 'index, follow',
        }
        
        print(f"Project detail viewed: {project.title}")
        return render(request, 'project_detail.html', context)
        
    except Exception as e:
        print(f"Error in project_detail_view: {str(e)}")
        raise Http404("Project not found")


@require_GET
def project_detail_ajax(request, project_id: int):
    """
    AJAX view for project details with error handling
    """
    try:
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Invalid request method'}, status=400)
        
        project = get_object_or_404(
            Project.objects.prefetch_related('tech_stack', 'images'),
            id=project_id
        )
        
        # Prepare tech stack list
        tech_stack = [tag.name for tag in project.tech_stack.all()]
        
        # Prepare image URLs
        image_urls = [img.image.url for img in project.images.all()]
        
        data = {
            'success': True,
            'title': project.title,
            'description': project.description,
            'short_description': project.short_description,
            'thumbnail': project.thumbnail.url if project.thumbnail else None,
            'github_link': project.github_link,
            'live_demo_link': project.live_demo_link,
            'tech_stack': tech_stack,
            'images': image_urls,
            'created_at': project.created_at.strftime('%B %Y'),
        }
        
        print(f"Project AJAX data served: {project.title}")
        return JsonResponse(data)
        
    except Project.DoesNotExist:
        print(f"Project not found in AJAX request: {project_id}")
        return JsonResponse({'error': 'Project not found'}, status=404)
    except Exception as e:
        print(f"Error in project_detail_ajax: {str(e)}")
        return JsonResponse({'error': 'Server error'}, status=500)


@require_GET
def filter_projects_ajax(request):
    """
    Enhanced AJAX view for filtering projects with validation
    """
    try:
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Invalid request method'}, status=400)
        
        # Get and validate parameters
        tech_filter = strip_tags(request.GET.get('tech', '').strip())[:50]
        search_query = strip_tags(request.GET.get('search', '').strip())[:100]
        
        # Base query with optimizations
        projects = Project.objects.select_related().prefetch_related(
            'tech_stack'
        ).order_by('-created_at')
        
        # Apply filters
        if search_query:
            projects = projects.filter(
                Q(title__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(tech_stack__name__icontains=search_query)
            ).distinct()
        
        if tech_filter:
            projects = projects.filter(tech_stack__name__iexact=tech_filter)
        
        # Limit results for performance
        projects = projects[:20]
        
        projects_data = []
        for project in projects:
            tech_stack = [tag.name for tag in project.tech_stack.all()[:5]]
            
            projects_data.append({
                'id': project.id,
                'title': project.title,
                'short_description': project.short_description,
                'thumbnail': project.thumbnail.url if project.thumbnail else None,
                'github_link': project.github_link,
                'live_demo_link': project.live_demo_link,
                'tech_stack': tech_stack,
                'tech_count': len(tech_stack),
                'created_at': project.created_at.strftime('%B %Y'),
            })
        
        response_data = {
            'success': True,
            'projects': projects_data,
            'count': len(projects_data),
        }
        
        print(f"Filtered projects served: {len(projects_data)} projects")
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"Error in filter_projects_ajax: {str(e)}")
        return JsonResponse({'error': 'Server error', 'success': False}, status=500)


def contact_view(request):
    """
    Enhanced contact view with better validation, SEO, and security
    """
    # SEO Meta Data
    context = {
        'page_title': 'Contact Atharva Mandle | Full Stack Developer & ML Engineer',
        'page_description': 'Get in touch with Atharva Mandle for web development projects, machine learning solutions, and tech collaborations. Based in Nagpur, India.',
        'keywords': 'contact, hire developer, full stack developer, machine learning engineer, web development services, Nagpur developer',
        'current_status': '🟢 Currently Working on ML & DevOps',
        'availability': '🟡 Open to Collaborations',
        'location': 'Nagpur, India',
        'email_college': 'atharvamandle19@gmail.com',  # Update with real email
        'email_personal': 'atharvamandle19@gmail.com',   # Update with real email
        'github_url': 'https://github.com/StardustEnigma',
        'linkedin_url': 'https://linkedin.com/in/atharvamandle',
        'twitter_url': 'https://twitter.com/atharvamandle',
        'canonical_url': request.build_absolute_uri(request.path),
        'robots': 'index, follow',
        'author': 'Atharva Mandle',
    }
    
    # Structured data for contact page
    structured_data = {
        "@context": "https://schema.org",
        "@type": "ContactPage",
        "name": "Contact Atharva Mandle",
        "description": context['page_description'],
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "Professional Services",
            "email": context['email_personal'],
            "areaServed": "Worldwide",
            "availableLanguage": "English"
        }
    }
    context['structured_data'] = json.dumps(structured_data)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Enhanced validation
                name = strip_tags(request.POST.get('name', '').strip())
                email = request.POST.get('email', '').strip().lower()
                subject = strip_tags(request.POST.get('subject', '').strip())
                message = strip_tags(request.POST.get('message', '').strip())
                
                # Validation
                errors = []
                
                if not name or len(name) < 2:
                    errors.append('Name must be at least 2 characters long.')
                elif len(name) > 100:
                    errors.append('Name must be less than 100 characters.')
                
                # Email validation
                email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
                if not email or not email_regex.match(email):
                    errors.append('Please enter a valid email address.')
                
                if not message or len(message) < 10:
                    errors.append('Message must be at least 10 characters long.')
                elif len(message) > 2000:
                    errors.append('Message must be less than 2000 characters.')
                
                if subject and len(subject) > 200:
                    errors.append('Subject must be less than 200 characters.')
                
                # Rate limiting check (simple version)
                recent_messages = ContactMessage.objects.filter(
                    email=email,
                    created_at__gte=timezone.now() - timezone.timedelta(hours=1)
                ).count()
                
                if recent_messages >= 3:
                    errors.append('Too many messages sent. Please wait before sending another message.')
                
                if errors:
                    for error in errors:
                        messages.error(request, error)
                    return render(request, 'contact.html', context)
                
                # Save the message
                contact_message = ContactMessage.objects.create(
                    name=name,
                    email=email,
                    subject=subject or f'Contact from {name}',
                    message=message
                )
                
                print(f"New contact message from {name} ({email})")
                messages.success(request, 'Thank you for your message! I\'ll get back to you soon.')
                
                # Clear form on success
                return redirect('info:contact')
                
        except ValidationError as e:
            print(f"Validation error in contact form: {str(e)}")
            messages.error(request, 'Please check your input and try again.')
        except Exception as e:
            print(f"Error in contact_view: {str(e)}")
            messages.error(request, 'Something went wrong. Please try again later.')
    
    return render(request, 'contact.html', context)


@csrf_exempt
@require_POST
def copy_email_ajax(request):
    """
    Enhanced AJAX endpoint for email copy with validation
    """
    try:
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
        
        data = json.loads(request.body)
        email_type = data.get('type', 'personal')
        
        # Validate email type
        valid_types = ['college', 'personal']
        if email_type not in valid_types:
            return JsonResponse({'success': False, 'message': 'Invalid email type'}, status=400)
        
        emails = {
            'college': 'atharvamandle19@gmail.com',  # Update with real email
            'personal': 'atharvamandle19@gmail.com'     # Update with real email
        }
        
        email = emails.get(email_type, emails['personal'])
        
        print(f"Email copied: {email_type}")
        
        return JsonResponse({
            'success': True,
            'email': email,
            'message': f'{email} copied to clipboard!'
        })
        
    except json.JSONDecodeError:
        print("Invalid JSON in copy_email_ajax")
        return JsonResponse({'success': False, 'message': 'Invalid data format'}, status=400)
    except Exception as e:
        print(f"Error in copy_email_ajax: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Server error'}, status=500)


@require_GET
def typing_simulation_ajax(request):
    """
    Enhanced AJAX endpoint for typing simulation
    """
    try:
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
        
        responses = [
            "Thanks for reaching out! 😊",
            "I'll review your message carefully...",
            "Looking forward to connecting!",
            "Let me get back to you soon!",
            "This sounds interesting! 🚀",
            "Excited to discuss this further!",
            "I appreciate you taking the time to contact me!",
        ]
        
        import random
        response_data = {
            'success': True,
            'response': random.choice(responses),
            'typing_delay': random.randint(2000, 4000)  # 2-4 seconds
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"Error in typing_simulation_ajax: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Server error'}, status=500)


# SEO and Utility Views

def projects_sitemap(request):
    """
    XML sitemap for projects
    """
    try:
        projects = Project.objects.all().order_by('-updated_at')
        
        # Create XML sitemap
        urlset = ET.Element('urlset')
        urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        
        # Add projects page
        url = ET.SubElement(urlset, 'url')
        ET.SubElement(url, 'loc').text = request.build_absolute_uri(reverse('info:projects'))
        ET.SubElement(url, 'changefreq').text = 'weekly'
        ET.SubElement(url, 'priority').text = '0.9'
        
        # Add individual projects
        for project in projects:
            url = ET.SubElement(urlset, 'url')
            project_url = reverse('info:project_detail', 
                                kwargs={'project_id': project.id, 'slug': slugify(project.title)})
            ET.SubElement(url, 'loc').text = request.build_absolute_uri(project_url)
            ET.SubElement(url, 'lastmod').text = project.updated_at.strftime('%Y-%m-%d')
            ET.SubElement(url, 'changefreq').text = 'monthly'
            ET.SubElement(url, 'priority').text = '0.8'
        
        xml_content = ET.tostring(urlset, encoding='unicode')
        
        return HttpResponse(xml_content, content_type='application/xml')
        
    except Exception as e:
        print(f"Error generating sitemap: {str(e)}")
        return HttpResponse("Error generating sitemap", status=500)


def robots_txt(request):
    """
    Robots.txt file
    """
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /api/",
        "",
        f"Sitemap: {request.build_absolute_uri(reverse('info:projects_sitemap'))}",
    ]
    
    return HttpResponse("\n".join(lines), content_type="text/plain")


class ProjectsFeed(Feed):
    """
    RSS feed for projects
    """
    title = "Atharva Mandle - Latest Projects"
    link = "/projects/"
    description = "Latest projects by Atharva Mandle - Full Stack Developer"
    feed_type = Rss201rev2Feed
    
    def items(self):
        return Project.objects.order_by('-created_at')[:10]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.short_description
    
    def item_link(self, item):
        return reverse('info:project_detail', 
                      kwargs={'project_id': item.id, 'slug': slugify(item.title)})
    
    def item_pubdate(self, item):
        return item.created_at

# Create an instance for the URL
projects_feed = ProjectsFeed()


def project_legacy_redirect(request, project_id):
    """
    Redirect old project URLs to new format
    """
    try:
        project = get_object_or_404(Project, id=project_id)
        slug = slugify(project.title)
        
        return HttpResponsePermanentRedirect(
            reverse('info:project_detail', 
                   kwargs={'project_id': project_id, 'slug': slug})
        )
    except:
        raise Http404("Project not found")


# Admin and Monitoring Views

@require_GET
def health_check(request):
    """
    Simple health check endpoint for monitoring
    """
    try:
        # Test database connection
        project_count = Project.objects.count()
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'projects_count': project_count,
        })
    except Exception as e:
        print(f"Health check failed: {str(e)}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)


@user_passes_test(lambda u: u.is_superuser)
def clear_cache(request):
    """
    Clear cache (admin only)
    """
    try:
        cache.clear()
        print("Cache cleared by admin")
        
        return JsonResponse({
            'success': True,
            'message': 'Cache cleared successfully',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        print(f"Error clearing cache: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@user_passes_test(lambda u: u.is_superuser)
def admin_stats(request):
    """
    Admin statistics page
    """
    try:
        stats = {
            'total_projects': Project.objects.count(),
            'total_tech_tags': TechTag.objects.count(),
            'total_project_images': ProjectImage.objects.count(),
            'total_contact_messages': ContactMessage.objects.count(),
            'recent_projects': list(Project.objects.order_by('-created_at')[:5].values('title', 'created_at')),
            'popular_tech_tags': list(TechTag.objects.annotate(
                project_count=Count('projects')
            ).order_by('-project_count')[:10].values('name', 'project_count')),
        }
        
        return JsonResponse(stats)
        
    except Exception as e:
        print(f"Error getting admin stats: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
