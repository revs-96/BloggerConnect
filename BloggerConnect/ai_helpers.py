import re
import os
import json
import textstat
from PIL import Image
import magic
from werkzeug.utils import secure_filename

class ContentEnhancer:
    """AI-like content enhancement without external APIs"""
    
    @staticmethod
    def enhance_blog_content(title, content, summary=""):
        """Enhance blog content with better formatting and structure"""
        enhanced_content = content
        
        # Add proper paragraph breaks
        enhanced_content = re.sub(r'\n\s*\n', '\n\n', enhanced_content)
        
        # Enhance headings
        lines = enhanced_content.split('\n')
        enhanced_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                enhanced_lines.append('')
                continue
                
            # Detect potential headings (lines that are short and followed by content)
            if (len(line) < 80 and 
                not line.endswith('.') and 
                not line.endswith(',') and
                not line.startswith('-') and
                not line.startswith('*') and
                len(line.split()) <= 8):
                # Check if it looks like a heading
                if any(word in line.lower() for word in ['introduction', 'conclusion', 'overview', 'summary', 'benefits', 'features', 'how to', 'what is', 'why', 'steps', 'guide', 'tutorial']):
                    enhanced_lines.append(f"## {line}")
                else:
                    enhanced_lines.append(line)
            else:
                enhanced_lines.append(line)
        
        enhanced_content = '\n'.join(enhanced_lines)
        
        # Add bullet points for lists
        enhanced_content = re.sub(r'^(\d+\.?\s+)', r'- ', enhanced_content, flags=re.MULTILINE)
        
        # Enhance emphasis
        enhanced_content = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', enhanced_content)
        enhanced_content = re.sub(r'\*([^*]+)\*', r'*\1*', enhanced_content)
        
        return enhanced_content
    
    @staticmethod
    def analyze_readability(content):
        """Analyze content readability"""
        try:
            # Calculate various readability scores
            flesch_reading_ease = textstat.flesch_reading_ease(content)
            flesch_kincaid_grade = textstat.flesch_kincaid_grade(content)
            
            # Determine readability level
            if flesch_reading_ease >= 90:
                level = "Very Easy"
            elif flesch_reading_ease >= 80:
                level = "Easy"
            elif flesch_reading_ease >= 70:
                level = "Fairly Easy"
            elif flesch_reading_ease >= 60:
                level = "Standard"
            elif flesch_reading_ease >= 50:
                level = "Fairly Difficult"
            elif flesch_reading_ease >= 30:
                level = "Difficult"
            else:
                level = "Very Difficult"
            
            return {
                'score': round(flesch_reading_ease, 1),
                'grade_level': round(flesch_kincaid_grade, 1),
                'level': level,
                'word_count': textstat.lexicon_count(content),
                'sentence_count': textstat.sentence_count(content),
                'avg_sentence_length': round(textstat.avg_sentence_length(content), 1)
            }
        except:
            return {
                'score': 50.0,
                'grade_level': 8.0,
                'level': 'Standard',
                'word_count': len(content.split()),
                'sentence_count': content.count('.') + content.count('!') + content.count('?'),
                'avg_sentence_length': 15.0
            }
    
    @staticmethod
    def generate_improvement_suggestions(readability_data, content):
        """Generate content improvement suggestions"""
        suggestions = []
        
        if readability_data['score'] < 50:
            suggestions.append("Consider using shorter sentences to improve readability")
            suggestions.append("Use simpler words where possible")
            
        if readability_data['avg_sentence_length'] > 20:
            suggestions.append("Break down long sentences into shorter ones")
            
        if readability_data['word_count'] < 300:
            suggestions.append("Consider expanding your content for better SEO")
            
        if not re.search(r'##?\s', content):
            suggestions.append("Add section headings to improve structure")
            
        if content.count('\n\n') < 3:
            suggestions.append("Add more paragraph breaks for better readability")
            
        return suggestions
    
    @staticmethod
    def extract_key_phrases(content, limit=10):
        """Extract key phrases from content"""
        # Simple keyword extraction based on frequency and importance
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        # Filter out common words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count frequencies
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top phrases
        key_phrases = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [phrase[0] for phrase in key_phrases]

class ImageProcessor:
    """Handle image processing and management"""
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_IMAGES_PER_BLOG = 8
    
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ImageProcessor.ALLOWED_EXTENSIONS
    
    @staticmethod
    def process_image(file, upload_folder):
        """Process and save uploaded image"""
        if not file or not ImageProcessor.allowed_file(file.filename):
            return None
            
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > ImageProcessor.MAX_FILE_SIZE:
            return None
            
        # Secure filename
        filename = secure_filename(file.filename)
        
        # Create unique filename
        import uuid
        from datetime import datetime
        
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}_{int(datetime.now().timestamp())}.{file_ext}"
        
        # Ensure upload folder exists
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        
        try:
            # Save and process image
            file.save(file_path)
            
            # Get image dimensions
            with Image.open(file_path) as img:
                width, height = img.size
                
                # Resize if too large (keep aspect ratio)
                max_width = 1200
                max_height = 800
                
                if width > max_width or height > max_height:
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                    img.save(file_path, optimize=True, quality=85)
                    width, height = img.size
            
            return {
                'filename': unique_filename,
                'original_filename': filename,
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'width': width,
                'height': height
            }
            
        except Exception as e:
            # Clean up file if processing failed
            if os.path.exists(file_path):
                os.remove(file_path)
            return None
    
    @staticmethod
    def generate_thumbnail(image_path, thumb_path, size=(300, 200)):
        """Generate thumbnail for image"""
        try:
            with Image.open(image_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(thumb_path, optimize=True, quality=80)
            return True
        except:
            return False
    
    @staticmethod
    def suggest_layout(image_count, content_length):
        """Suggest optimal image layout based on content"""
        if image_count == 0:
            return "no-images"
        elif image_count == 1:
            return "single-featured"
        elif image_count == 2:
            return "side-by-side"
        elif image_count <= 4:
            return "grid-2x2"
        else:
            return "gallery"

class ContentFormatter:
    """Format content for beautiful display"""
    
    @staticmethod
    def format_for_display(content, images=None):
        """Format content with images for beautiful display"""
        if not images:
            images = []
            
        formatted_content = content
        
        # Convert markdown-style formatting to HTML
        formatted_content = re.sub(r'^## (.+)$', r'<h2 class="blog-heading">\1</h2>', formatted_content, flags=re.MULTILINE)
        formatted_content = re.sub(r'^### (.+)$', r'<h3 class="blog-subheading">\1</h3>', formatted_content, flags=re.MULTILINE)
        
        # Convert paragraphs
        paragraphs = formatted_content.split('\n\n')
        formatted_paragraphs = []
        
        image_index = 0
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                # Add image every 2-3 paragraphs
                if images and image_index < len(images) and i > 0 and i % 3 == 0:
                    img = images[image_index]
                    img_html = f'''
                    <div class="blog-image-container my-4">
                        <img src="/static/uploads/{img.filename}" 
                             alt="{img.original_filename}" 
                             class="img-fluid rounded shadow-sm blog-image"
                             loading="lazy">
                        <div class="image-caption text-muted text-center mt-2">
                            <small>{img.original_filename}</small>
                        </div>
                    </div>
                    '''
                    formatted_paragraphs.append(img_html)
                    image_index += 1
                
                formatted_paragraphs.append(f'<p class="blog-paragraph">{paragraph}</p>')
        
        # Add remaining images at the end
        while image_index < len(images):
            img = images[image_index]
            img_html = f'''
            <div class="blog-image-container my-4">
                <img src="/static/uploads/{img.filename}" 
                     alt="{img.original_filename}" 
                     class="img-fluid rounded shadow-sm blog-image"
                     loading="lazy">
                <div class="image-caption text-muted text-center mt-2">
                    <small>{img.original_filename}</small>
                </div>
            </div>
            '''
            formatted_paragraphs.append(img_html)
            image_index += 1
        
        return '\n'.join(formatted_paragraphs)
    
    @staticmethod
    def create_table_of_contents(content):
        """Generate table of contents from headings"""
        headings = re.findall(r'^##+ (.+)$', content, flags=re.MULTILINE)
        if not headings:
            return ""
            
        toc_html = '<div class="table-of-contents card p-3 mb-4">'
        toc_html += '<h6><i class="fas fa-list me-2"></i>Table of Contents</h6>'
        toc_html += '<ul class="list-unstyled mb-0">'
        
        for heading in headings:
            # Create anchor link
            anchor = re.sub(r'[^a-zA-Z0-9\s]', '', heading).replace(' ', '-').lower()
            toc_html += f'<li><a href="#{anchor}" class="text-decoration-none">{heading}</a></li>'
        
        toc_html += '</ul></div>'
        return toc_html

def smart_auto_enhance_blog(title, content, summary=""):
    """Main function to auto-enhance blog content"""
    enhancer = ContentEnhancer()
    
    # Enhance content structure
    enhanced_content = enhancer.enhance_blog_content(title, content, summary)
    
    # Analyze readability
    readability = enhancer.analyze_readability(content)
    
    # Generate auto-tags
    key_phrases = enhancer.extract_key_phrases(title + " " + content)
    
    # Generate improvement suggestions
    suggestions = enhancer.generate_improvement_suggestions(readability, content)
    
    return {
        'enhanced_content': enhanced_content,
        'readability': readability,
        'auto_tags': key_phrases[:8],
        'suggestions': suggestions,
        'word_count': readability['word_count'],
        'reading_time': max(1, round(readability['word_count'] / 200))
    }