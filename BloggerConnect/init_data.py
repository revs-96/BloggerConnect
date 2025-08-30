from BloggerConnect.app import db
from BloggerConnect.models import User, Blog

def initialize_sample_data():
    """Initialize sample users and blogs for testing"""
    
    # Check if data already exists
    if User.query.count() > 0:
        return
    
    # Create sample admin user
    admin = User(
        username='admin',
        email='admin@blogging.com',
        full_name='System Administrator',
        role='admin',
        credits=1000
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Create sample regular users
    user1 = User(
        username='john_doe',
        email='john@example.com',
        full_name='John Doe',
        role='user',
        credits=25
    )
    user1.set_password('password123')
    db.session.add(user1)
    
    user2 = User(
        username='jane_smith',
        email='jane@example.com',
        full_name='Jane Smith',
        role='user',
        credits=30
    )
    user2.set_password('password123')
    db.session.add(user2)
    
    user3 = User(
        username='mike_johnson',
        email='mike@example.com',
        full_name='Mike Johnson',
        role='user',
        credits=15
    )
    user3.set_password('password123')
    db.session.add(user3)
    
    # Commit users first to get their IDs
    db.session.commit()
    
    # Create sample blogs
    blog1 = Blog(
        title='Getting Started with Python Web Development',
        summary='A comprehensive guide to building web applications with Python and Flask.',
        content='''Python web development has become increasingly popular due to its simplicity and powerful frameworks. 
        
Flask is a micro web framework that provides the tools, libraries and technologies to build a web application. This framework is more Pythonic than Django because Flask web application code is more explicit.

In this blog, we'll explore the fundamentals of Flask development, including routing, templates, and database integration. We'll also cover best practices for building scalable web applications.

Key topics include:
- Setting up a Flask development environment
- Creating routes and handling HTTP requests
- Working with templates using Jinja2
- Database integration with SQLAlchemy
- User authentication and session management
- Deployment considerations

Whether you're a beginner or experienced developer, this guide will help you master Flask web development.''',
        user_id=user1.id,
        is_published=True
    )
    db.session.add(blog1)
    
    blog2 = Blog(
        title='The Future of Artificial Intelligence',
        summary='Exploring the latest trends and developments in AI technology.',
        content='''Artificial Intelligence is rapidly transforming industries and reshaping our world. From machine learning algorithms to neural networks, AI technologies are becoming more sophisticated and accessible.

Recent breakthroughs in AI include:
- Large Language Models (LLMs) like GPT and BERT
- Computer vision advancements
- Reinforcement learning applications
- AI ethics and responsible development

The impact of AI spans across various sectors including healthcare, finance, transportation, and education. As we move forward, it's crucial to understand both the opportunities and challenges that AI presents.

This blog explores the current state of AI technology and its potential future applications, while also addressing important considerations around ethics, bias, and societal impact.''',
        user_id=user2.id,
        is_published=True
    )
    db.session.add(blog2)
    
    blog3 = Blog(
        title='Building Responsive Web Designs',
        summary='Tips and techniques for creating mobile-friendly websites.',
        content='''In today's mobile-first world, responsive web design is no longer optional—it's essential. With users accessing websites from various devices, ensuring your site looks and functions well across all screen sizes is crucial.

Key principles of responsive design:
- Fluid grid systems
- Flexible images and media
- Media queries for different breakpoints
- Mobile-first approach
- Touch-friendly navigation

Tools and frameworks that can help:
- Bootstrap CSS framework
- CSS Grid and Flexbox
- Responsive image techniques
- Progressive web app features

By implementing these techniques, you can create websites that provide an optimal viewing experience across desktop computers, tablets, and mobile phones. This blog will guide you through the essential concepts and practical implementation strategies.''',
        user_id=user3.id,
        is_published=True
    )
    db.session.add(blog3)
    
    blog4 = Blog(
        title='Database Design Best Practices',
        summary='Guidelines for designing efficient and scalable database schemas.',
        content='''Good database design is the foundation of any successful application. Poor design decisions early on can lead to performance issues, data integrity problems, and maintenance nightmares as your application scales.

Essential database design principles:
- Normalization and denormalization strategies
- Primary and foreign key relationships
- Indexing for performance
- Data type selection
- Constraint implementation

Common pitfalls to avoid:
- Over-normalization leading to complex queries
- Missing indexes on frequently queried columns
- Inconsistent naming conventions
- Lack of data validation at the database level

This comprehensive guide covers both relational and NoSQL database design patterns, helping you make informed decisions for your next project.''',
        user_id=user1.id,
        is_published=True
    )
    db.session.add(blog4)
    
    # Draft blog (not published)
    draft_blog = Blog(
        title='Work in Progress: Advanced Flask Patterns',
        summary='Exploring advanced Flask development patterns and techniques.',
        content='''This is a draft blog post about advanced Flask patterns. Content is being developed...

Topics to cover:
- Application factories
- Blueprints for large applications
- Custom decorators
- Error handling strategies
- Testing best practices

More content coming soon!''',
        user_id=user2.id,
        is_published=False
    )
    db.session.add(draft_blog)
    
    db.session.commit()
    print("Sample data initialized successfully!")
    print("Admin credentials: admin/admin123")
    print("User credentials: john_doe/password123, jane_smith/password123, mike_johnson/password123")
