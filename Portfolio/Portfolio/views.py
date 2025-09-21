from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import json


class HomeView(TemplateView):
    """
    Home page view with hero section and skills overview
    """
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Home - Atharva Mandle | Full-Stack Developer',
            'page_description': 'Atharva Mandle - Full-Stack Developer specializing in Django, Python, Tailwind CSS, and modern web technologies.',
            'page_keywords': 'Atharva Mandle, Full-Stack Developer, Django Developer, Python Developer, Tailwind CSS, Three.js, Web Development',
        })
        return context


class AboutView(TemplateView):
    """
    About page view with detailed journey and skills information
    """
    template_name = 'about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'About Me - Atharva Mandle | Full-Stack Developer & CS Student',
            'page_description': 'Learn about Atharva Mandle, a passionate Computer Science student from RBU Nagpur specializing in full-stack development with Django, React, Machine Learning, and DevOps practices.',
            'page_keywords': 'Atharva Mandle, Computer Science Student, RBU Nagpur, Full-Stack Developer, Django Developer, React Developer, Machine Learning, DevOps, GitHub Actions, Docker',
            'canonical_url': self.request.build_absolute_uri(),
            
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


class SkillsView(TemplateView):
    """
    Skills page view with technical skills and expertise
    """
    template_name = 'skills.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Define skill categories with details
        skill_categories = {
            'backend': {
                'title': 'Backend Development',
                'description': 'Server-side development with robust frameworks and efficient database management.',
                'skills': ['Django', 'Python', 'FastAPI', 'REST APIs', 'GraphQL']
            },
            'frontend': {
                'title': 'Frontend Development', 
                'description': 'Modern, responsive user interfaces with cutting-edge frameworks and libraries.',
                'skills': ['React', 'JavaScript', 'TypeScript', 'Tailwind CSS', 'Alpine.js', 'Three.js']
            },
            'database': {
                'title': 'Database & Storage',
                'description': 'Efficient data storage, retrieval, and management across various database systems.',
                'skills': ['PostgreSQL', 'MySQL', 'SQLite', 'Redis', 'MongoDB']
            },
            'ml_ai': {
                'title': 'Machine Learning & AI',
                'description': 'Data science, machine learning algorithms, and AI model development and deployment.',
                'skills': ['Scikit-learn', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Matplotlib']
            },
            'devops': {
                'title': 'DevOps & Deployment',
                'description': 'Automated deployment pipelines, containerization, and cloud infrastructure management.',
                'skills': ['Docker', 'AWS', 'GitHub Actions', 'Nginx', 'Linux']
            },
            'tools': {
                'title': 'Version Control & Tools',
                'description': 'Code versioning, collaboration tools, and development workflow optimization.',
                'skills': ['Git', 'GitHub', 'VS Code', 'PyCharm', 'Postman']
            }
        }
        
        # Define proficiency levels
        proficiencies = [
            {'name': 'Python & Django', 'percentage': 95},
            {'name': 'JavaScript & React', 'percentage': 88},
            {'name': 'Machine Learning', 'percentage': 70},
            {'name': 'Database Design', 'percentage': 90},
            {'name': 'DevOps & Deployment', 'percentage': 65},
            {'name': 'UI/UX Design', 'percentage': 75},
        ]
        
        # Define tools
        tools = [
            {'name': 'Python'},
            {'name': 'Django'},
            {'name': 'React'},
            {'name': 'JavaScript'},
            {'name': 'Tailwind CSS'},
            {'name': 'PostgreSQL'},
            {'name': 'Scikit-learn'},
            {'name': 'Docker'},
            {'name': 'Git'},
            {'name': 'AWS'},
            {'name': 'FastAPI'},
            {'name': 'Alpine.js'},
        ]
        
        context.update({
            'page_title': 'Skills & Expertise - Atharva Mandle',
            'page_description': 'Comprehensive overview of Atharva Mandle\'s technical skills including Django, Python, React, Machine Learning, and modern web technologies.',
            'page_keywords': 'Django, Python, React, Machine Learning, Full-Stack Development, Technical Skills, DevOps',
            'skill_categories': skill_categories,
            'proficiencies': proficiencies,
            'tools': tools,
        })
        
        return context


class ContactView(TemplateView):
    """
    Contact page view with contact form
    """
    template_name = 'contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Contact - Atharva Mandle',
            'page_description': 'Get in touch with Atharva Mandle for your next web development project. Available for Django and full-stack development work.',
            'page_keywords': 'Contact Atharva Mandle, Web Development Services, Django Developer, Freelance Developer',
            'contact_info': {
                'email': 'atharva@example.com',
                'linkedin': 'https://linkedin.com/in/atharvamandle',
                'github': 'https://github.com/atharvamandle',
                'location': 'Nagpur, Maharashtra, India'
            }
        })
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle contact form submission
        """
        try:
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            subject = request.POST.get('subject', '').strip()
            message = request.POST.get('message', '').strip()

            # Basic validation
            if not all([name, email, subject, message]):
                messages.error(request, 'All fields are required.')
                return self.get(request, *args, **kwargs)

            # Send email (configure your email settings)
            email_subject = f'Portfolio Contact: {subject}'
            email_message = f"""
Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}
"""

            try:
                send_mail(
                    email_subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    ['your-email@example.com'],  # Replace with your email
                    fail_silently=False,
                )
                messages.success(request, 'Thank you! Your message has been sent successfully.')
            except Exception as e:
                messages.error(request, 'Sorry, there was an error sending your message. Please try again later.')

        except Exception as e:
            messages.error(request, 'An error occurred. Please try again.')

        return self.get(request, *args, **kwargs)


# API Views for AJAX requests
def skills_api(request):
    """
    API endpoint to return skills data as JSON
    """
    skills_data = [
        {
            'name': 'Django',
            'level': 'Expert',
            'proficiency': 95,
            'description': 'High-level Python web framework for rapid development with clean, pragmatic design.'
        },
        {
            'name': 'Python',
            'level': 'Advanced', 
            'proficiency': 90,
            'description': 'Backend development, automation, data processing, and API development.'
        },
        {
            'name': 'Tailwind CSS',
            'level': 'Expert',
            'proficiency': 92,
            'description': 'Utility-first CSS framework for rapidly building custom user interfaces.'
        },
        {
            'name': 'JavaScript',
            'level': 'Advanced',
            'proficiency': 88,
            'description': 'Interactive frontend development, ES6+, async programming, and DOM manipulation.'
        },
        {
            'name': 'Machine Learning',
            'level': 'Intermediate',
            'proficiency': 70,
            'description': 'Data preprocessing, model training, evaluation, and practical ML applications.'
        },
        {
            'name': 'PostgreSQL',
            'level': 'Advanced',
            'proficiency': 85,
            'description': 'Advanced database design, optimization, and complex query development.'
        },
        {
            'name': 'Git',
            'level': 'Advanced',
            'proficiency': 87,
            'description': 'Version control, collaborative development, and project management.'
        },
        {
            'name': 'Docker',
            'level': 'Intermediate',
            'proficiency': 65,
            'description': 'Containerization, deployment automation, and DevOps practices.'
        }
    ]

    return JsonResponse({'skills': skills_data})


# Function-based views (alternative approach)
def home_view(request):
    """
    Alternative function-based view for home page
    """
    context = {
        'page_title': 'Home - Atharva Mandle',
        'page_description': 'Atharva Mandle - Full-Stack Developer specializing in Django, Python, Tailwind CSS, and modern web technologies.',
    }
    return render(request, 'home.html', context)


def about_view(request):
    """
    Alternative function-based view for about page
    """
    context = {
        'page_title': 'About - Atharva Mandle',
        'page_description': 'Learn more about Atharva Mandle - Full-Stack Developer with expertise in Django, Python, and modern web technologies.',
    }
    return render(request, 'about.html', context)


def contact_view(request):
    """
    Alternative function-based view for contact page
    """
    if request.method == 'POST':
        # Handle form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Add your contact form logic here
        messages.success(request, 'Thank you for your message!')

    context = {
        'page_title': 'Contact - Atharva Mandle',
        'page_description': 'Get in touch with Atharva Mandle for your next web development project.',
    }
    return render(request, 'contact.html', context)
class ProjectsView(TemplateView):
    template_name = 'projects.html'