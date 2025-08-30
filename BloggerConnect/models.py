from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from BloggerConnect.app import db
import re
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' or 'user'
    credits = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    theme_preference = db.Column(db.String(20), default='dark')  # 'light', 'dark', 'hacker'
    
    # Relationship to blogs
    blogs = db.relationship('Blog', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # New AI-enhanced fields
    tags = db.Column(db.Text)  # JSON string of tags
    readability_score = db.Column(db.Float)
    word_count = db.Column(db.Integer)
    reading_time = db.Column(db.Integer)  # in minutes
    enhanced_content = db.Column(db.Text)  # AI-enhanced formatted content
    featured_image = db.Column(db.String(255))  # Main blog image
    
    # Relationship to blog images
    images = db.relationship('BlogImage', backref='blog', lazy=True, cascade='all, delete-orphan')
    # Relationship to blog attachments (documents)
    attachments = db.relationship('BlogAttachment', backref='blog', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Blog {self.title}>'
    
    def get_summary(self):
        if self.summary:
            return self.summary
        # Create summary from first 200 characters of content
        return self.content[:200] + '...' if len(self.content) > 200 else self.content
    
    def get_tags(self):
        """Get tags as a list"""
        if self.tags:
            try:
                return json.loads(self.tags)
            except:
                return []
        return []
    
    def set_tags(self, tag_list):
        """Set tags from a list"""
        self.tags = json.dumps(tag_list)
    
    def calculate_reading_time(self):
        """Calculate reading time based on word count"""
        if self.word_count:
            return max(1, round(self.word_count / 200))  # 200 words per minute
        return 1
    
    def auto_generate_tags(self):
        """Generate tags based on content analysis"""
        content_lower = (self.title + ' ' + self.content).lower()
        
        # Common programming/tech keywords
        tech_keywords = {
            'python': ['python', 'django', 'flask', 'pandas'],
            'javascript': ['javascript', 'js', 'react', 'node', 'vue'],
            'web': ['html', 'css', 'frontend', 'backend', 'web'],
            'data': ['data', 'analytics', 'database', 'sql'],
            'ai': ['ai', 'artificial intelligence', 'machine learning', 'ml'],
            'programming': ['code', 'programming', 'development', 'software'],
            'tutorial': ['tutorial', 'guide', 'how to', 'step by step'],
            'review': ['review', 'comparison', 'vs', 'analysis']
        }
        
        found_tags = []
        for tag, keywords in tech_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    found_tags.append(tag)
                    break
        
        # Add content-based tags
        word_counts = {}
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content_lower)
        for word in words:
            if word not in ['this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'were', 'said', 'each', 'which', 'their', 'time', 'more', 'very', 'what', 'know', 'just', 'first', 'into', 'over', 'think', 'also', 'your', 'work', 'life', 'only', 'can', 'still', 'should', 'after', 'being', 'now', 'made', 'before', 'here', 'through', 'when', 'where', 'much', 'some', 'these', 'many', 'would', 'there']:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get top words as tags
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        found_tags.extend([word for word, count in top_words if count >= 2])
        
        return list(set(found_tags))[:8]  # Limit to 8 tags

class BlogImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_size = db.Column(db.Integer)  # in bytes
    image_width = db.Column(db.Integer)
    image_height = db.Column(db.Integer)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)
    is_featured = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<BlogImage {self.filename}>'

class BlogAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # stored unique filename
    original_filename = db.Column(db.String(255), nullable=False)  # original name shown to users
    file_path = db.Column(db.String(500), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_size = db.Column(db.Integer)  # in bytes
    mime_type = db.Column(db.String(120))
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)

    def __repr__(self):
        return f'<BlogAttachment {self.filename}>'
