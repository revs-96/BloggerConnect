"""
AI Service Module for BloggerConnect
Provides AI-powered content enhancement and tag generation
"""

import re
import random
from typing import List, Dict, Tuple
import html

class AIContentEnhancer:
    """AI service for content enhancement and tag generation"""
    
    def __init__(self):
        self.common_tags = [
            'technology', 'programming', 'web-development', 'python', 'javascript',
            'tutorial', 'guide', 'tips', 'best-practices', 'coding', 'software',
            'development', 'frontend', 'backend', 'database', 'api', 'framework',
            'learning', 'career', 'productivity', 'innovation', 'digital', 'tech',
            'startup', 'business', 'design', 'ux', 'ui', 'mobile', 'cloud',
            'security', 'data', 'analytics', 'machine-learning', 'ai', 'automation'
        ]
        
        self.formatting_patterns = [
            # Headers
            (r'^([A-Z][^.!?]*[.!?]?)$', r'## \1'),
            # Bold important phrases
            (r'\b(important|note|warning|tip|remember|key point)\b:?', r'**\1**:'),
            # Code blocks
            (r'`([^`]+)`', r'```\n\1\n```'),
            # Lists
            (r'^[-*]\s+(.+)$', r'- \1'),
        ]
    
    def enhance_content(self, content: str, title: str = "") -> str:
        """
        Enhance blog content with better formatting and structure
        """
        if not content or len(content.strip()) < 10:
            return content
        
        enhanced = content.strip()
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in enhanced.split('\n\n') if p.strip()]
        
        enhanced_paragraphs = []
        
        for i, paragraph in enumerate(paragraphs):
            # Skip if already formatted
            if paragraph.startswith('#') or paragraph.startswith('```'):
                enhanced_paragraphs.append(paragraph)
                continue
            
            # Add introduction header for first paragraph if it's long
            if i == 0 and len(paragraph) > 200 and not paragraph.startswith('##'):
                enhanced_paragraphs.append("## Introduction\n")
                enhanced_paragraphs.append(paragraph)
            else:
                # Enhance paragraph formatting
                enhanced_para = self._enhance_paragraph(paragraph)
                enhanced_paragraphs.append(enhanced_para)
        
        # Join paragraphs
        enhanced = '\n\n'.join(enhanced_paragraphs)
        
        # Add conclusion if content is long enough
        if len(enhanced) > 1000 and not enhanced.lower().endswith(('conclusion', 'summary', 'final thoughts')):
            enhanced += "\n\n## Conclusion\n\nThank you for reading! Feel free to share your thoughts and experiences in the comments below."
        
        return enhanced
    
    def _enhance_paragraph(self, paragraph: str) -> str:
        """Enhance individual paragraph formatting"""
        enhanced = paragraph
        
        # Apply formatting patterns
        for pattern, replacement in self.formatting_patterns:
            enhanced = re.sub(pattern, replacement, enhanced, flags=re.MULTILINE | re.IGNORECASE)
        
        # Enhance lists
        lines = enhanced.split('\n')
        enhanced_lines = []
        in_list = False
        
        for line in lines:
            line = line.strip()
            if not line:
                enhanced_lines.append(line)
                in_list = False
                continue
            
            # Detect list items
            if re.match(r'^\d+\.?\s+', line) or re.match(r'^[-*•]\s+', line):
                if not in_list:
                    in_list = True
                # Normalize list formatting
                line = re.sub(r'^(\d+\.?|[-*•])\s+', '- ', line)
                enhanced_lines.append(line)
            else:
                if in_list:
                    in_list = False
                enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)
    
    def generate_tags(self, title: str, content: str, max_tags: int = 8) -> List[str]:
        """
        Generate relevant tags based on title and content
        """
        if not title and not content:
            return []
        
        text = f"{title} {content}".lower()
        
        # Remove HTML tags and special characters
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'[^\w\s-]', ' ', text)
        
        # Extract potential tags
        words = text.split()
        
        # Find relevant tags
        relevant_tags = []
        
        # Check for exact matches
        for tag in self.common_tags:
            if tag in text or tag.replace('-', ' ') in text:
                relevant_tags.append(tag)
        
        # Extract technical terms and keywords
        technical_patterns = [
            r'\b(python|javascript|java|html|css|react|vue|angular|node|django|flask)\b',
            r'\b(tutorial|guide|tips|howto|how-to)\b',
            r'\b(web|mobile|app|application|software|development)\b',
            r'\b(database|sql|api|rest|json|xml)\b',
            r'\b(security|performance|optimization|testing)\b'
        ]
        
        for pattern in technical_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                tag = match.lower()
                if tag not in relevant_tags and len(tag) > 2:
                    relevant_tags.append(tag)
        
        # Add category-based tags
        if any(word in text for word in ['tutorial', 'guide', 'how', 'learn']):
            if 'tutorial' not in relevant_tags:
                relevant_tags.append('tutorial')
        
        if any(word in text for word in ['tip', 'trick', 'best', 'practice']):
            if 'tips' not in relevant_tags:
                relevant_tags.append('tips')
        
        if any(word in text for word in ['beginner', 'start', 'introduction', 'basic']):
            if 'beginner' not in relevant_tags:
                relevant_tags.append('beginner')
        
        # Remove duplicates and limit
        unique_tags = list(dict.fromkeys(relevant_tags))
        
        # If we don't have enough tags, add some general ones
        if len(unique_tags) < 3:
            general_tags = ['programming', 'technology', 'development', 'coding', 'tech']
            for tag in general_tags:
                if tag not in unique_tags:
                    unique_tags.append(tag)
                if len(unique_tags) >= 3:
                    break
        
        return unique_tags[:max_tags]
    
    def suggest_image_placements(self, content: str, num_images: int) -> List[Dict]:
        """
        Suggest optimal positions for image placement in content
        """
        if not content or num_images <= 0:
            return []
        
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if len(paragraphs) <= 1:
            return [{'position': 0, 'type': 'header', 'caption': 'Featured image'}]
        
        placements = []
        
        # Always place first image at the beginning
        placements.append({
            'position': 0,
            'type': 'header',
            'caption': 'Featured image for this article'
        })
        
        if num_images > 1:
            # Distribute remaining images throughout content
            content_length = len(paragraphs)
            
            if content_length >= 3:
                # Place images at strategic points
                positions = []
                
                # Middle of content
                if num_images >= 2:
                    mid_pos = content_length // 2
                    positions.append(mid_pos)
                
                # Near end
                if num_images >= 3 and content_length >= 5:
                    end_pos = int(content_length * 0.75)
                    positions.append(end_pos)
                
                # Additional images distributed evenly
                if num_images > 3:
                    remaining = num_images - 3
                    step = max(1, content_length // (remaining + 1))
                    for i in range(remaining):
                        pos = (i + 1) * step
                        if pos < content_length and pos not in positions:
                            positions.append(pos)
                
                # Create placement objects
                for i, pos in enumerate(positions[:num_images-1]):
                    placement_type = 'inline'
                    caption = f'Illustration {i + 2}'
                    
                    # Determine placement type based on content
                    if pos < len(paragraphs):
                        para_text = paragraphs[pos].lower()
                        if any(word in para_text for word in ['example', 'code', 'result']):
                            placement_type = 'example'
                            caption = 'Example illustration'
                        elif any(word in para_text for word in ['step', 'process', 'method']):
                            placement_type = 'process'
                            caption = 'Process illustration'
                    
                    placements.append({
                        'position': pos,
                        'type': placement_type,
                        'caption': caption
                    })
        
        return placements[:num_images]
    
    def optimize_content_with_images(self, content: str, image_urls: List[str]) -> str:
        """
        Insert images into content at optimal positions
        """
        if not image_urls or not content:
            return content
        
        placements = self.suggest_image_placements(content, len(image_urls))
        paragraphs = content.split('\n\n')
        
        # Insert images from bottom to top to maintain positions
        for i, placement in enumerate(reversed(placements)):
            if i < len(image_urls):
                image_url = image_urls[-(i+1)]
                position = placement['position']
                caption = placement['caption']
                
                # Create image markdown
                image_md = f'\n\n![{caption}]({image_url})\n*{caption}*\n\n'
                
                # Insert at position
                if position < len(paragraphs):
                    paragraphs.insert(position, image_md.strip())
                else:
                    paragraphs.append(image_md.strip())
        
        return '\n\n'.join(paragraphs)

# Global AI service instance
ai_service = AIContentEnhancer()