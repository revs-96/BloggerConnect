from flask import render_template, flash, redirect, url_for, request, abort, jsonify, send_file
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse as url_parse
from werkzeug.utils import secure_filename
import os
import json
import re
from BloggerConnect.app import app, db
from BloggerConnect.models import User, Blog, BlogImage, BlogAttachment
from BloggerConnect.forms import LoginForm, RegistrationForm, BlogForm, ProfileForm, AdminUserForm, BlogImageForm
from BloggerConnect.ai_helpers import smart_auto_enhance_blog, ImageProcessor, ContentFormatter
from BloggerConnect.advanced_ai import advanced_ai
from BloggerConnect.gemini_ai import gemini_ai

# Attachment handling
ATTACH_ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv', 'zip', 'md'}
MAX_ATTACHMENT_SIZE = 20 * 1024 * 1024  # 20MB

def allowed_attachment(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ATTACH_ALLOWED_EXTENSIONS

def process_attachment(file, upload_root_folder):
    """Validate and save attachment file; return metadata dict or None"""
    if not file or not file.filename or not allowed_attachment(file.filename):
        return None

    # Check file size
    try:
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
    except Exception:
        file_size = None

    if file_size is not None and file_size > MAX_ATTACHMENT_SIZE:
        return None

    # Secure and unique filename
    original_filename = secure_filename(file.filename)
    file_ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''

    import uuid
    from datetime import datetime

    unique_filename = f"{uuid.uuid4().hex}_{int(datetime.now().timestamp())}.{file_ext}" if file_ext else uuid.uuid4().hex

    # Save under /static/uploads/attachments
    attachments_folder = os.path.join(upload_root_folder, 'attachments')
    os.makedirs(attachments_folder, exist_ok=True)
    file_path = os.path.join(attachments_folder, unique_filename)

    file.save(file_path)

    return {
        'filename': unique_filename,
        'original_filename': original_filename,
        'file_path': file_path,
        'file_size': os.path.getsize(file_path),
        'mime_type': getattr(file, 'mimetype', None)
    }

@app.route('/')
def index():
    # Get latest published blogs
    blogs = Blog.query.filter_by(is_published=True).order_by(Blog.created_at.desc()).limit(6).all()
    return render_template('index.html', blogs=blogs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
        if not user.is_active:
            flash('Your account has been deactivated. Please contact admin.', 'warning')
            return redirect(url_for('login'))
        
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/download/<int:attachment_id>')
def download_attachment(attachment_id):
    attachment = BlogAttachment.query.get_or_404(attachment_id)
    
    # Check if the blog is published or if the current user is the owner or admin
    blog = Blog.query.get(attachment.blog_id)
    if not blog.is_published and (not current_user.is_authenticated or 
                                (current_user.id != blog.user_id and not current_user.is_admin())):
        abort(403)
    
    return send_file(attachment.file_path, 
                     download_name=attachment.original_filename, 
                     as_attachment=True)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data, 
            email=form.email.data,
            full_name=form.full_name.data,
            credits=10  # Welcome bonus credits
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now registered! You have received 10 welcome credits.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    
    # User dashboard
    user_blogs = Blog.query.filter_by(user_id=current_user.id).order_by(Blog.created_at.desc()).all()
    return render_template('user/dashboard.html', blogs=user_blogs)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.email = form.email.data
        current_user.theme_preference = form.theme_preference.data
        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.email.data = current_user.email
        form.theme_preference.data = current_user.theme_preference
    
    return render_template('user/profile.html', form=form)

@app.route('/create_blog', methods=['GET', 'POST'])
@login_required
def create_blog():
    form = BlogForm()
    image_form = BlogImageForm()
    
    if form.validate_on_submit():
        # Create the blog
        blog = Blog(
            title=form.title.data,
            summary=form.summary.data,
            content=form.content.data,
            is_published=form.is_published.data,
            user_id=current_user.id
        )
        
        # AI Enhancement using Gemini AI
        if form.auto_enhance.data:
            # Use Gemini AI for enhanced content processing
            enhancement_data = gemini_ai.enhance_blog_content(
                form.title.data, 
                form.content.data, 
                form.summary.data
            )
            
            blog.enhanced_content = enhancement_data['enhanced_content']
            blog.readability_score = enhancement_data['readability']['score']
            blog.word_count = enhancement_data['word_count']
            blog.reading_time = enhancement_data['reading_time']
            
            # Store AI insights if available
            if 'content_insights' in enhancement_data:
                blog.ai_insights = json.dumps(enhancement_data['content_insights'])
            
            if form.auto_tags.data:
                blog.set_tags(enhancement_data['auto_tags'][:8])  # Limit to 8 tags
        else:
            # Basic analysis without enhancement
            words = len(form.content.data.split())
            blog.word_count = words
            blog.reading_time = max(1, round(words / 200))
            blog.enhanced_content = form.content.data
        
        db.session.add(blog)
        db.session.flush()  # Get the blog ID
        
        # Handle image uploads
        upload_folder = os.path.join(app.static_folder, 'uploads')
        uploaded_files = request.files.getlist('images')
        
        image_count = 0
        for file in uploaded_files:
            if file and file.filename and image_count < ImageProcessor.MAX_IMAGES_PER_BLOG:
                image_data = ImageProcessor.process_image(file, upload_folder)
                if image_data:
                    blog_image = BlogImage(
                        filename=image_data['filename'],
                        original_filename=image_data['original_filename'],
                        file_path=image_data['file_path'],
                        file_size=image_data['file_size'],
                        image_width=image_data['width'],
                        image_height=image_data['height'],
                        blog_id=blog.id,
                        is_featured=(image_count == 0)  # First image is featured
                    )
                    db.session.add(blog_image)
                    image_count += 1
                    
                    if image_count == 1:
                        blog.featured_image = image_data['filename']
        
        # Handle multiple document uploads
        uploaded_documents = request.files.getlist('documents')
        for document in uploaded_documents:
            if document and document.filename:
                attachment_data = process_attachment(document, upload_folder)
                if attachment_data:
                    blog_attachment = BlogAttachment(
                        filename=attachment_data['filename'],
                        original_filename=attachment_data['original_filename'],
                        file_path=attachment_data['file_path'],
                        file_size=attachment_data['file_size'],
                        mime_type=attachment_data['mime_type'],
                        blog_id=blog.id
                    )
                    db.session.add(blog_attachment)
        
        # Apply smart image placement if AI enhancement is enabled and images exist
        if form.auto_enhance.data and image_count > 0:
            # Get image data for AI placement
            blog_images = []
            for image in blog.images:
                blog_images.append({
                    'filename': image.filename,
                    'original_filename': image.original_filename,
                    'is_featured': image.is_featured
                })
            
            # Apply smart image placement
            if blog.enhanced_content:
                blog.enhanced_content = advanced_ai.smart_image_placement(
                    blog.enhanced_content, 
                    blog_images
                )
        
        # Award credits for publishing a blog
        if form.is_published.data:
            current_user.credits += 5
        
        db.session.commit()
        
        success_msg = 'Your blog has been created!'
        if form.is_published.data:
            success_msg += ' You earned 5 credits.'
        if form.auto_enhance.data:
            success_msg += ' Content has been AI-enhanced for better readability.'
            
        flash(success_msg, 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('user/create_blog.html', form=form, image_form=image_form)

@app.route('/edit_blog/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_blog(id):
    blog = Blog.query.get_or_404(id)
    
    # Check if user owns the blog or is admin
    if blog.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    
    form = BlogForm()
    image_form = BlogImageForm()
    
    if form.validate_on_submit():
        was_published = blog.is_published
        
        blog.title = form.title.data
        blog.summary = form.summary.data
        blog.content = form.content.data
        blog.is_published = form.is_published.data
        
        # Re-enhance if requested
        if form.auto_enhance.data:
            enhancement_data = smart_auto_enhance_blog(
                form.title.data, 
                form.content.data, 
                form.summary.data
            )
            
            blog.enhanced_content = enhancement_data['enhanced_content']
            blog.readability_score = enhancement_data['readability']['score']
            blog.word_count = enhancement_data['word_count']
            blog.reading_time = enhancement_data['reading_time']
            
            if form.auto_tags.data:
                blog.set_tags(enhancement_data['auto_tags'])
        else:
            # Update basic stats
            words = len(form.content.data.split())
            blog.word_count = words
            blog.reading_time = max(1, round(words / 200))
            blog.enhanced_content = form.content.data
        
        # Handle new image uploads
        upload_folder = os.path.join(app.static_folder, 'uploads')
        uploaded_files = request.files.getlist('images')
        
        current_image_count = len(blog.images)
        for file in uploaded_files:
            if file and file.filename and current_image_count < ImageProcessor.MAX_IMAGES_PER_BLOG:
                image_data = ImageProcessor.process_image(file, upload_folder)
                if image_data:
                    blog_image = BlogImage(
                        filename=image_data['filename'],
                        original_filename=image_data['original_filename'],
                        file_path=image_data['file_path'],
                        file_size=image_data['file_size'],
                        image_width=image_data['width'],
                        image_height=image_data['height'],
                        blog_id=blog.id,
                        is_featured=(current_image_count == 0 and not blog.featured_image)
                    )
                    db.session.add(blog_image)
                    current_image_count += 1
                    
                    if not blog.featured_image:
                        blog.featured_image = image_data['filename']
        
        # Handle multiple document uploads
        uploaded_documents = request.files.getlist('documents')
        for document in uploaded_documents:
            if document and document.filename:
                attachment_data = process_attachment(document, upload_folder)
                if attachment_data:
                    blog_attachment = BlogAttachment(
                        filename=attachment_data['filename'],
                        original_filename=attachment_data['original_filename'],
                        file_path=attachment_data['file_path'],
                        file_size=attachment_data['file_size'],
                        mime_type=attachment_data['mime_type'],
                        blog_id=blog.id
                    )
                    db.session.add(blog_attachment)
        
        # Award credits if publishing for the first time
        if not was_published and form.is_published.data:
            current_user.credits += 5
        
        db.session.commit()
        
        success_msg = 'Your blog has been updated.'
        if not was_published and form.is_published.data:
            success_msg += ' You earned 5 credits for publishing!'
        if form.auto_enhance.data:
            success_msg += ' Content has been re-enhanced.'
            
        flash(success_msg, 'success')
        return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        form.title.data = blog.title
        form.summary.data = blog.summary
        form.content.data = blog.content
        form.is_published.data = blog.is_published
    
    return render_template('user/edit_blog.html', form=form, image_form=image_form, blog=blog)

@app.route('/delete_blog/<int:id>')
@login_required
def delete_blog(id):
    blog = Blog.query.get_or_404(id)
    
    # Check if user owns the blog or is admin
    if blog.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    
    # Get the blog author for credit deduction
    blog_author = blog.author
    
    # Delete associated image files
    upload_folder = os.path.join(app.static_folder, 'uploads')
    for image in blog.images:
        try:
            if os.path.exists(image.file_path):
                os.remove(image.file_path)
        except:
            pass  # Continue even if file deletion fails
    
    # Deduct credits if the blog was published
    credits_deducted = 0
    if blog.is_published:
        credits_deducted = 5
        blog_author.credits = max(0, blog_author.credits - credits_deducted)
    
    db.session.delete(blog)
    db.session.commit()
    
    # Flash message with credit information
    message = 'Blog and associated images have been deleted.'
    if credits_deducted > 0:
        message += f' {credits_deducted} credits have been deducted from {blog_author.full_name}\'s account.'
    
    flash(message, 'info')
    return redirect(url_for('dashboard'))

@app.route('/delete_image/<int:image_id>')
@login_required
def delete_image(image_id):
    image = BlogImage.query.get_or_404(image_id)
    blog = image.blog
    
    # Check if user owns the blog or is admin
    if blog.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    
    # Delete file
    try:
        if os.path.exists(image.file_path):
            os.remove(image.file_path)
    except:
        pass
    
    # If this was the featured image, update blog
    if blog.featured_image == image.filename:
        remaining_images = [img for img in blog.images if img.id != image_id]
        blog.featured_image = remaining_images[0].filename if remaining_images else None
    
    db.session.delete(image)
    db.session.commit()
    
    flash('Image deleted successfully.', 'success')
    return redirect(url_for('edit_blog', id=blog.id))

@app.route('/blog/<int:id>')
def view_blog(id):
    blog = Blog.query.get_or_404(id)
    
    # Only show published blogs to non-owners/non-admins
    if not blog.is_published and blog.user_id != current_user.id and not (current_user.is_authenticated and current_user.is_admin()):
        abort(404)
    
    return render_template('blog/view.html', blog=blog)

@app.route('/blogs')
def blog_list():
    page = request.args.get('page', 1, type=int)
    blogs = Blog.query.filter_by(is_published=True).order_by(Blog.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    return render_template('blog/list.html', blogs=blogs)

# Admin routes
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        abort(403)
    
    # Get statistics
    total_users = User.query.count()
    total_blogs = Blog.query.count()
    published_blogs = Blog.query.filter_by(is_published=True).count()
    recent_blogs = Blog.query.order_by(Blog.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_blogs=total_blogs,
                         published_blogs=published_blogs,
                         recent_blogs=recent_blogs)

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin():
        abort(403)
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(id):
    if not current_user.is_admin():
        abort(403)
    
    user = User.query.get_or_404(id)
    form = AdminUserForm()
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.full_name = form.full_name.data
        user.role = form.role.data
        user.credits = form.credits.data
        user.is_active = form.is_active.data
        user.theme_preference = form.theme_preference.data
        db.session.commit()
        flash('User has been updated.', 'success')
        return redirect(url_for('admin_users'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.full_name.data = user.full_name
        form.role.data = user.role
        form.credits.data = user.credits
        form.is_active.data = user.is_active
        form.theme_preference.data = user.theme_preference
    
    return render_template('admin/edit_user.html', form=form, user=user)

@app.route('/admin/delete_user/<int:id>')
@login_required
def admin_delete_user(id):
    if not current_user.is_admin():
        abort(403)
    
    user = User.query.get_or_404(id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User has been deleted.', 'info')
    return redirect(url_for('admin_users'))

@app.route('/update_theme', methods=['POST'])
@login_required
def update_theme():
    data = request.get_json()
    theme = data.get('theme')
    
    if theme in ['light', 'dark', 'hacker']:
        current_user.theme_preference = theme
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Invalid theme'}), 400

@app.route('/theme_preview')
@login_required
def theme_preview():
    """Preview page to test all themes"""
    return render_template('theme_preview.html')

@app.route('/ai_preview', methods=['POST'])
@login_required
def ai_preview():
    """AJAX endpoint to preview AI-enhanced content"""
    data = request.get_json()
    title = data.get('title', '')
    content = data.get('content', '')
    
    if not content or len(content) < 50:
        return jsonify({'error': 'Content too short for enhancement'}), 400
    
    try:
        # Use Gemini AI for content enhancement
        enhancement_data = gemini_ai.enhance_blog_content(title, content)
        
        # Get additional advanced AI features
        quality_analysis = advanced_ai.analyze_content_quality(title, enhancement_data['enhanced_content'])
        improvement_suggestions = enhancement_data.get('suggestions', [])
        
        return jsonify({
            'success': True,
            'enhanced_content': enhancement_data['enhanced_content'],
            'auto_tags': enhancement_data['auto_tags'],
            'readability': enhancement_data['readability'],
            'suggestions': improvement_suggestions,
            'word_count': enhancement_data['word_count'],
            'reading_time': enhancement_data['reading_time'],
            'quality_score': quality_analysis.get('quality_score', 0),
            'content_insights': enhancement_data.get('content_insights', {}),
            'ai_powered': enhancement_data.get('ai_powered', False),
            'quality_factors': quality_analysis.get('quality_factors', [])
        })
    except Exception as e:
        return jsonify({'error': f'Enhancement failed: {str(e)}'}), 500

@app.route('/ai_insights/<int:blog_id>')
@login_required
def ai_insights(blog_id):
    """Show detailed AI insights for a blog"""
    blog = Blog.query.get_or_404(blog_id)
    
    # Check permissions
    if not (current_user.id == blog.user_id or current_user.is_admin()):
        abort(403)
    
    # Generate comprehensive AI analysis
    try:
        quality_analysis = advanced_ai.analyze_content_quality(blog.title, blog.content)
        seo_data = advanced_ai.enhance_content_with_seo(blog.title, blog.content)
        improvement_suggestions = advanced_ai.suggest_improvements(blog.title, blog.content)
        content_outline = advanced_ai.generate_content_outline(blog.title, blog.content)
        
        insights = {
            'quality_analysis': quality_analysis,
            'seo_data': seo_data,
            'suggestions': improvement_suggestions,
            'content_outline': content_outline,
            'basic_stats': {
                'word_count': len(blog.content.split()),
                'character_count': len(blog.content),
                'paragraph_count': len([p for p in blog.content.split('\n\n') if p.strip()]),
                'sentence_count': len(re.findall(r'[.!?]+', blog.content))
            }
        }
        
        return render_template('ai_insights.html', blog=blog, insights=insights)
        
    except Exception as e:
        flash(f'Error generating AI insights: {str(e)}', 'error')
        return redirect(url_for('view_blog', id=blog_id))
