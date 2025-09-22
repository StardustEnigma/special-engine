from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.utils import timezone
from django.urls import reverse
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError
from django.db import transaction

import json
import re
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Cache timeout constants
CACHE_TIMEOUT_SHORT = 60 * 5      # 5 minutes
CACHE_TIMEOUT_MEDIUM = 60 * 30     # 30 minutes  
CACHE_TIMEOUT_LONG = 60 * 60 * 24  # 24 hours


@method_decorator([
    cache_page(CACHE_TIMEOUT_LONG),
    vary_on_headers('User-Agent')
], name='dispatch')
class HomeView(TemplateView):
    """
    Enhanced Home page view with caching, SEO optimization, and structured data
    """
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Enhanced SEO metadata
        structured_data = {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": "Atharva Mandle",
            "jobTitle": "Full-Stack Developer",
            "description": "Computer Science student and Full-Stack Developer specializing in Django, Python, Machine Learning, and modern web technologies.",
            "url": self.request.build_absolute_uri(),
            "sameAs": [
                "https://github.com/StardustEnigma",
                "https://www.linkedin.com/in/atharva-mandle-5214312aa/",
                "https://x.com/atharvamandle19"
            ],
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "Nagpur",
                "addressRegion": "Maharashtra",
                "addressCountry": "India"
            },
            "alumniOf": {
                "@type": "EducationalOrganization",
                "name": "RBU Nagpur",
                "description": "Computer Science Engineering"
            },
            "knowsAbout": [
                "Django", "Python", "JavaScript", "React", "Machine Learning",
                "Full-Stack Development", "Web Development", "DevOps"
            ],
            "hasOccupation": {
                "@type": "Occupation",
                "name": "Full-Stack Developer",
                "occupationLocation": {
                    "@type": "City",
                    "name": "Nagpur, Maharashtra, India"
                },
                "skills": "Django, Python, React, Machine Learning, DevOps"
            }
        }
        
        # Featured skills for homepage
        featured_skills = [
            {
                'name': 'Django & Python',
                'description': 'Backend development with robust server-side solutions',
                'proficiency': 95,
                'icon': 'code'
            },
            {
                'name': 'Machine Learning',
                'description': 'Data science and ML model development',
                'proficiency': 70,
                'icon': 'brain'
            },
            {
                'name': 'DevOps & Automation',
                'description': 'CI/CD pipelines and containerization',
                'proficiency': 65,
                'icon': 'tools'
            }
        ]
        
        context.update({
            'page_title': 'Atharva Mandle | Full-Stack Developer & CS Student | Django, ML & DevOps Expert',
            'page_description': 'Atharva Mandle - Computer Science student and Full-Stack Developer from Nagpur specializing in Django, Python, Machine Learning, and DevOps. Available for web development projects and ML solutions.',
            'page_keywords': 'Atharva Mandle, Full-Stack Developer, Django Developer, Python Developer, Machine Learning Engineer, Computer Science Student, Nagpur Developer, Web Development, DevOps, GitHub Actions, Docker',
            'structured_data': json.dumps(structured_data),
            'canonical_url': self.request.build_absolute_uri(),
            'featured_skills': featured_skills,
            'robots': 'index, follow',
            'author': 'Atharva Mandle',
            'og_image': self.request.build_absolute_uri('/static/images/atharva-og.jpg'),  # Add your OG image
            'twitter_card': 'summary_large_image',
        })
        return context


@method_decorator([
    cache_page(CACHE_TIMEOUT_LONG),
    vary_on_headers('User-Agent')
], name='dispatch')
class AboutView(TemplateView):
    """
    Enhanced About page view with comprehensive SEO and structured data
    """
    template_name = 'about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Enhanced structured data for About page
        structured_data = {
            "@context": "https://schema.org",
            "@type": "ProfilePage",
            "mainEntity": {
                "@type": "Person",
                "name": "Atharva Mandle",
                "jobTitle": "Full-Stack Developer & Computer Science Student",
                "description": "Passionate Computer Science student from RBU Nagpur specializing in full-stack development with Django, React, Machine Learning, and DevOps practices.",
                "url": self.request.build_absolute_uri(),
                "birthPlace": {
                    "@type": "Place",
                    "name": "Nagpur, Maharashtra, India"
                },
                "alumniOf": {
                    "@type": "EducationalOrganization", 
                    "name": "Rashtrasant Tukadoji Maharaj Nagpur University (RBU)",
                    "description": "Computer Science Engineering"
                },
                "hasOccupation": [
                    {
                        "@type": "Occupation",
                        "name": "Full-Stack Developer",
                        "skills": "Django, Python, JavaScript, React, REST APIs"
                    },
                    {
                        "@type": "Occupation", 
                        "name": "Machine Learning Engineer",
                        "skills": "Scikit-learn, Data Analysis, Model Training"
                    }
                ],
                "knowsAbout": [
                    "Django Framework", "Python Programming", "JavaScript", "React",
                    "Machine Learning", "DevOps", "GitHub Actions", "Docker",
                    "PostgreSQL", "REST APIs", "Web Development"
                ]
            }
        }
        
        context.update({
            'page_title': 'About Atharva Mandle | Full-Stack Developer & CS Student from Nagpur | Django & ML Expert',
            'page_description': 'Learn about Atharva Mandle, a passionate Computer Science student from RBU Nagpur specializing in full-stack development with Django, React, Machine Learning, and DevOps practices. Completed 2+ ML client projects.',
            'page_keywords': 'Atharva Mandle, Computer Science Student, RBU Nagpur, Full-Stack Developer, Django Developer, React Developer, Machine Learning Engineer, DevOps Engineer, GitHub Actions, Docker, Python Developer',
            'canonical_url': self.request.build_absolute_uri(),
            'structured_data': json.dumps(structured_data),
            'robots': 'index, follow',
            'author': 'Atharva Mandle',
            
            # Timeline data
            'timeline_data': [
                {
                    'year': '2024',
                    'title': 'Started CSE Journey',
                    'description': 'Began Computer Science Engineering at RBU Nagpur, diving deep into programming fundamentals and discovering my passion for web development.',
                    'icon': 'graduation',
                    'color': 'cyan'
                },
                {
                    'year': '2025',
                    'title': 'Full-Stack Development',
                    'description': 'Mastered Django backend development, learned React fundamentals, started exploring Machine Learning basics, and completed 2 ML client projects.',
                    'icon': 'code',
                    'color': 'blue'
                },
                {
                    'year': 'Present',
                    'title': 'Expanding Horizons',
                    'description': 'Currently strengthening Django & APIs, diving into Machine Learning fundamentals, and exploring DevOps tools like GitHub Actions and Docker.',
                    'icon': 'rocket',
                    'color': 'purple'
                }
            ],
            
            # Core values data
            'core_values': [
                {
                    'title': 'Backend Development',
                    'description': 'Building robust server-side solutions with Django and REST APIs.',
                    'icon': 'server',
                    'details': 'Currently strengthening my backend expertise with advanced Django patterns, API development, database optimization, and secure authentication systems. Focus on scalable architectures.',
                    'skills': ['Django', 'Python', 'REST APIs', 'PostgreSQL', 'Authentication', 'Database Design']
                },
                {
                    'title': 'Machine Learning', 
                    'description': 'Exploring ML fundamentals and applying them to real-world problems.',
                    'icon': 'brain',
                    'details': 'Learning Machine Learning basics including data preprocessing, model training, and evaluation. Successfully completed 2 ML client projects, gaining hands-on experience with practical applications.',
                    'skills': ['Python', 'Scikit-learn', 'Data Analysis', 'Model Training', 'Client Projects', 'Problem Solving']
                },
                {
                    'title': 'DevOps & Automation',
                    'description': 'Exploring modern DevOps practices and automation tools.',
                    'icon': 'tools',
                    'details': 'Currently exploring DevOps tools and practices including GitHub Actions for CI/CD, Docker for containerization, and automated deployment workflows to improve development efficiency.',
                    'skills': ['GitHub Actions', 'Docker', 'CI/CD', 'Automation', 'Version Control', 'Deployment']
                }
            ],
            
            # Currently working on
            'current_focus': [
                {
                    'title': 'Strengthening Backend',
                    'description': 'Deepening Django expertise and advanced API development',
                    'progress': 75
                },
                {
                    'title': 'Machine Learning Basics',
                    'description': 'Learning ML fundamentals and practical applications',
                    'progress': 60
                },
                {
                    'title': 'DevOps Tools',
                    'description': 'Exploring GitHub Actions, Docker, and automation practices',
                    'progress': 50
                }
            ],
            
            # Personal info
            'personal_info': {
                'name': 'Atharva Mandle',
                'title': 'Full-Stack Developer & CS Student',
                'location': 'Nagpur, Maharashtra, India',
                'education': 'Computer Science Engineering at RBU Nagpur',
                'focus': 'Full-Stack Web Development, Machine Learning, DevOps',
                'learning': 'Currently strengthening Django & APIs, exploring ML basics, and learning DevOps tools',
                'passion': 'Building scalable solutions and exploring new technologies to solve real-world problems'
            },
            
            # Achievement highlights
            'achievements': [
                'Completed 2 Machine Learning client projects successfully',
                'Built multiple Django applications with complex backend logic',
                'Developed responsive web applications with modern frameworks',
                'Integrated REST APIs and third-party services',
                'Currently exploring DevOps automation and CI/CD practices'
            ]
        })
        return context


@method_decorator([
    cache_page(CACHE_TIMEOUT_LONG),
    vary_on_headers('User-Agent')
], name='dispatch')
class SkillsView(TemplateView):
    """
    Enhanced Skills page view with technical skills, SEO optimization, and caching
    """
    template_name = 'skills.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Structured data for skills
        structured_data = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": "Technical Skills - Atharva Mandle",
            "description": "Comprehensive overview of Atharva Mandle's technical skills including Django, Python, React, Machine Learning, and modern web technologies.",
            "author": {
                "@type": "Person",
                "name": "Atharva Mandle",
                "jobTitle": "Full-Stack Developer"
            },
            "mainEntity": {
                "@type": "ItemList",
                "name": "Technical Skills",
                "itemListElement": [
                    {
                        "@type": "Skill",
                        "name": "Django Framework",
                        "description": "Expert level backend development with Django"
                    },
                    {
                        "@type": "Skill", 
                        "name": "Python Programming",
                        "description": "Advanced Python development for web and ML applications"
                    },
                    {
                        "@type": "Skill",
                        "name": "Machine Learning",
                        "description": "ML model development and data analysis"
                    }
                ]
            }
        }
        
        # Define skill categories with details
        skill_categories = {
            'backend': {
                'title': 'Backend Development',
                'description': 'Server-side development with robust frameworks and efficient database management.',
                'skills': ['Django', 'Python', 'FastAPI', 'REST APIs', 'GraphQL'],
                'icon': 'server'
            },
            'frontend': {
                'title': 'Frontend Development', 
                'description': 'Modern, responsive user interfaces with cutting-edge frameworks and libraries.',
                'skills': ['React', 'JavaScript', 'TypeScript', 'Tailwind CSS', 'Alpine.js', 'Three.js'],
                'icon': 'code'
            },
            'database': {
                'title': 'Database & Storage',
                'description': 'Efficient data storage, retrieval, and management across various database systems.',
                'skills': ['PostgreSQL', 'MySQL', 'SQLite', 'Redis', 'MongoDB'],
                'icon': 'database'
            },
            'ml_ai': {
                'title': 'Machine Learning & AI',
                'description': 'Data science, machine learning algorithms, and AI model development and deployment.',
                'skills': ['Scikit-learn', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Matplotlib'],
                'icon': 'brain'
            },
            'devops': {
                'title': 'DevOps & Deployment',
                'description': 'Automated deployment pipelines, containerization, and cloud infrastructure management.',
                'skills': ['Docker', 'AWS', 'GitHub Actions', 'Nginx', 'Linux'],
                'icon': 'tools'
            },
            'tools': {
                'title': 'Version Control & Tools',
                'description': 'Code versioning, collaboration tools, and development workflow optimization.',
                'skills': ['Git', 'GitHub', 'VS Code', 'PyCharm', 'Postman'],
                'icon': 'wrench'
            }
        }
        
        # Define proficiency levels
        proficiencies = [
            {'name': 'Python & Django', 'percentage': 95, 'level': 'Expert'},
            {'name': 'JavaScript & React', 'percentage': 88, 'level': 'Advanced'},
            {'name': 'Machine Learning', 'percentage': 70, 'level': 'Intermediate'},
            {'name': 'Database Design', 'percentage': 90, 'level': 'Advanced'},
            {'name': 'DevOps & Deployment', 'percentage': 65, 'level': 'Intermediate'},
            {'name': 'UI/UX Design', 'percentage': 75, 'level': 'Intermediate'},
        ]
        
        # Define tools with categories
        tools = [
            {'name': 'Python', 'category': 'Language'},
            {'name': 'Django', 'category': 'Framework'},
            {'name': 'React', 'category': 'Frontend'},
            {'name': 'JavaScript', 'category': 'Language'},
            {'name': 'Tailwind CSS', 'category': 'Styling'},
            {'name': 'PostgreSQL', 'category': 'Database'},
            {'name': 'Scikit-learn', 'category': 'ML'},
            {'name': 'Docker', 'category': 'DevOps'},
            {'name': 'Git', 'category': 'Version Control'},
            {'name': 'AWS', 'category': 'Cloud'},
            {'name': 'FastAPI', 'category': 'Framework'},
            {'name': 'Alpine.js', 'category': 'Frontend'},
        ]
        
        context.update({
            'page_title': 'Technical Skills & Expertise | Atharva Mandle | Django, ML & DevOps Specialist',
            'page_description': 'Comprehensive overview of Atharva Mandle\'s technical skills including Django, Python, React, Machine Learning, DevOps, and modern web technologies. Expert-level backend development with 95% Django proficiency.',
            'page_keywords': 'Django Expert, Python Developer, React Skills, Machine Learning Engineer, DevOps Skills, Technical Expertise, Full-Stack Skills, Web Development Skills, Database Design, API Development',
            'structured_data': json.dumps(structured_data),
            'canonical_url': self.request.build_absolute_uri(),
            'skill_categories': skill_categories,
            'proficiencies': proficiencies,
            'tools': tools,
            'robots': 'index, follow',
            'author': 'Atharva Mandle',
        })
        
        return context


class ContactView(TemplateView):
    """
    Enhanced Contact page view with form handling, validation, and SEO
    """
    template_name = 'contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Structured data for contact page
        structured_data = {
            "@context": "https://schema.org",
            "@type": "ContactPage",
            "name": "Contact Atharva Mandle",
            "description": "Get in touch with Atharva Mandle for web development projects, machine learning solutions, and technical collaborations.",
            "author": {
                "@type": "Person",
                "name": "Atharva Mandle",
                "jobTitle": "Full-Stack Developer"
            },
            "contactPoint": {
                "@type": "ContactPoint",
                "contactType": "Professional Services",
                "areaServed": "Worldwide",
                "availableLanguage": ["English", "Hindi", "Marathi"],
                "serviceType": [
                    "Web Development", 
                    "Django Development",
                    "Machine Learning Solutions",
                    "DevOps Consulting"
                ]
            }
        }
        
        context.update({
            'page_title': 'Contact Atharva Mandle | Hire Django Developer & ML Engineer | Web Development Services',
            'page_description': 'Get in touch with Atharva Mandle for your next web development project, Django application, or machine learning solution. Available for freelance work and technical collaborations. Based in Nagpur, India.',
            'page_keywords': 'Contact Atharva Mandle, Hire Django Developer, Web Development Services, Machine Learning Engineer, Freelance Developer, Technical Consultation, Nagpur Developer, Django Projects',
            'structured_data': json.dumps(structured_data),
            'canonical_url': self.request.build_absolute_uri(),
            'robots': 'index, follow',
            'author': 'Atharva Mandle',
            'contact_info': {
                'email': 'atharvamandle19@gmail.com',  # Update with real email
                'linkedin': 'https://www.linkedin.com/in/atharva-mandle-5214312aa/',
                'github': 'https://github.com/StardustEnigma',
                'location': 'Nagpur, Maharashtra, India',
                'availability': 'Available for freelance projects',
                'response_time': 'Usually responds within 24 hours'
            },
            'services_offered': [
                'Django Web Development',
                'REST API Development', 
                'Machine Learning Solutions',
                'Database Design & Optimization',
                'DevOps & Deployment',
                'Technical Consultation'
            ]
        })
        return context

    def post(self, request, *args, **kwargs):
        """
        Enhanced contact form submission with validation and rate limiting
        """
        try:
            with transaction.atomic():
                # Get and sanitize form data
                name = strip_tags(request.POST.get('name', '').strip())
                email = request.POST.get('email', '').strip().lower()
                subject = strip_tags(request.POST.get('subject', '').strip())
                message = strip_tags(request.POST.get('message', '').strip())

                # Enhanced validation
                errors = []
                
                if not name or len(name) < 2:
                    errors.append('Name must be at least 2 characters long.')
                elif len(name) > 100:
                    errors.append('Name must be less than 100 characters.')

                # Email validation
                email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
                if not email or not email_regex.match(email):
                    errors.append('Please enter a valid email address.')

                if not subject or len(subject) < 5:
                    errors.append('Subject must be at least 5 characters long.')
                elif len(subject) > 200:
                    errors.append('Subject must be less than 200 characters.')

                if not message or len(message) < 10:
                    errors.append('Message must be at least 10 characters long.')
                elif len(message) > 2000:
                    errors.append('Message must be less than 2000 characters.')

                # Simple rate limiting (check cache)
                cache_key = f"contact_form_{request.META.get('REMOTE_ADDR', 'unknown')}"
                recent_submissions = cache.get(cache_key, 0)
                
                if recent_submissions >= 3:
                    errors.append('Too many messages sent. Please wait before sending another message.')

                if errors:
                    for error in errors:
                        messages.error(request, error)
                    return self.get(request, *args, **kwargs)

                # Prepare email content
                email_subject = f'Portfolio Contact: {subject}'
                email_message = f"""
New contact form submission:

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}

---
Submitted at: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
IP Address: {request.META.get('REMOTE_ADDR', 'Unknown')}
User Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')[:100]}
"""

                try:
                    # Send email (configure your email settings in settings.py)
                    if hasattr(settings, 'DEFAULT_FROM_EMAIL'):
                        send_mail(
                            email_subject,
                            email_message,
                            settings.DEFAULT_FROM_EMAIL,
                            ['atharvamandel19@gmail.com'],  # Replace with your email
                            fail_silently=False,
                        )
                    
                    # Update rate limiting cache
                    cache.set(cache_key, recent_submissions + 1, 3600)  # 1 hour
                    
                    # Log successful contact
                    logger.info(f"Contact form submitted by {name} ({email})")
                    
                    messages.success(request, 'Thank you for your message! I\'ll get back to you within 24 hours.')
                    
                except Exception as e:
                    logger.error(f"Error sending contact email: {str(e)}")
                    messages.error(request, 'Sorry, there was an error sending your message. Please try emailing me directly.')

        except Exception as e:
            logger.error(f"Error in contact form: {str(e)}")
            messages.error(request, 'An unexpected error occurred. Please try again.')

        return self.get(request, *args, **kwargs)


# Enhanced API Views with caching
@cache_page(CACHE_TIMEOUT_MEDIUM)
@require_http_methods(["GET"])
def skills_api(request):
    """
    Enhanced API endpoint to return skills data as JSON with caching
    """
    try:
        skills_data = [
            {
                'name': 'Django',
                'level': 'Expert',
                'proficiency': 95,
                'category': 'Backend',
                'description': 'High-level Python web framework for rapid development with clean, pragmatic design.',
                'experience_years': 2,
                'projects_completed': 10
            },
            {
                'name': 'Python',
                'level': 'Advanced', 
                'proficiency': 90,
                'category': 'Language',
                'description': 'Backend development, automation, data processing, and API development.',
                'experience_years': 2,
                'projects_completed': 15
            },
            {
                'name': 'Machine Learning',
                'level': 'Intermediate',
                'proficiency': 70,
                'category': 'AI/ML',
                'description': 'Data preprocessing, model training, evaluation, and practical ML applications.',
                'experience_years': 1,
                'projects_completed': 2
            },
            {
                'name': 'React',
                'level': 'Advanced',
                'proficiency': 85,
                'category': 'Frontend',
                'description': 'Modern React development with hooks, context, and component-based architecture.',
                'experience_years': 1,
                'projects_completed': 8
            },
            {
                'name': 'PostgreSQL',
                'level': 'Advanced',
                'proficiency': 85,
                'category': 'Database',
                'description': 'Advanced database design, optimization, and complex query development.',
                'experience_years': 2,
                'projects_completed': 12
            },
            {
                'name': 'Docker',
                'level': 'Intermediate',
                'proficiency': 65,
                'category': 'DevOps',
                'description': 'Containerization, deployment automation, and DevOps practices.',
                'experience_years': 1,
                'projects_completed': 5
            }
        ]

        return JsonResponse({
            'success': True,
            'skills': skills_data,
            'total_skills': len(skills_data),
            'last_updated': timezone.now().isoformat(),
            'categories': list(set([skill['category'] for skill in skills_data]))
        })
        
    except Exception as e:
        logger.error(f"Error in skills API: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Unable to fetch skills data'
        }, status=500)


# Enhanced function-based views with caching
@cache_page(CACHE_TIMEOUT_LONG)
@vary_on_headers('User-Agent')
def home_view(request):
    """
    Enhanced function-based view for home page with caching and SEO
    """
    context = {
        'page_title': 'Atharva Mandle | Full-Stack Developer & CS Student | Django, ML & DevOps Expert',
        'page_description': 'Atharva Mandle - Computer Science student and Full-Stack Developer from Nagpur specializing in Django, Python, Machine Learning, and DevOps.',
        'page_keywords': 'Atharva Mandle, Full-Stack Developer, Django, Python, Machine Learning, Computer Science Student',
        'canonical_url': request.build_absolute_uri(),
        'robots': 'index, follow',
    }
    return render(request, 'home.html', context)


@cache_page(CACHE_TIMEOUT_LONG)
@vary_on_headers('User-Agent')
def about_view(request):
    """
    Enhanced function-based view for about page with caching
    """
    context = {
        'page_title': 'About Atharva Mandle | Full-Stack Developer & CS Student from Nagpur',
        'page_description': 'Learn about Atharva Mandle - Computer Science student and Full-Stack Developer with expertise in Django, Python, Machine Learning, and modern web technologies.',
        'canonical_url': request.build_absolute_uri(),
        'robots': 'index, follow',
    }
    return render(request, 'about.html', context)


def contact_view_function(request):
    """
    Enhanced function-based view for contact page with form handling
    """
    if request.method == 'POST':
        try:
            # Get form data
            name = strip_tags(request.POST.get('name', '').strip())
            email = request.POST.get('email', '').strip().lower()
            subject = strip_tags(request.POST.get('subject', '').strip())
            message = strip_tags(request.POST.get('message', '').strip())

            # Basic validation
            if not all([name, email, subject, message]):
                messages.error(request, 'All fields are required.')
            else:
                # Email validation
                email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
                if email_regex.match(email):
                    # Process form (add your logic here)
                    logger.info(f"Contact form submitted by {name} ({email})")
                    messages.success(request, 'Thank you for your message! I\'ll get back to you soon.')
                else:
                    messages.error(request, 'Please enter a valid email address.')

        except Exception as e:
            logger.error(f"Error processing contact form: {str(e)}")
            messages.error(request, 'An error occurred. Please try again.')

    context = {
        'page_title': 'Contact Atharva Mandle | Hire Django Developer & ML Engineer',
        'page_description': 'Get in touch with Atharva Mandle for your next web development project, Django application, or machine learning solution.',
        'canonical_url': request.build_absolute_uri(),
        'robots': 'index, follow',
    }
    return render(request, 'contact.html', context)


# Health check endpoint
def health_check(request):
    """
    Simple health check endpoint for monitoring
    """
    try:
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)
