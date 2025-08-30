"""
Advanced AI Features for BloggerConnect
Includes smart image placement, content optimization, and SEO enhancement
"""

import re
import json
from typing import List, Dict, Tuple
from datetime import datetime

class AdvancedAIService:
    """Advanced AI service with enhanced capabilities"""
    
    def __init__(self):
        self.seo_keywords = [
            'tutorial', 'guide', 'how-to', 'tips', 'best-practices', 'beginner',
            'advanced', 'complete', 'ultimate', 'comprehensive', 'step-by-step',
            'easy', 'simple', 'quick', 'fast', 'efficient', 'effective'
        ]
        
        self.content_patterns = {
            'introduction': r'(introduction|intro|overview|getting started|what is)',
            'steps': r'(step \d+|first|second|third|next|then|finally)',
            'examples': r'(example|for instance|such as|like|consider)',
            'conclusion': r'(conclusion|summary|final|in summary|to conclude)',
            'benefits': r'(benefit|advantage|pros|good|positive)',
            'problems': r'(problem|issue|challenge|difficulty|cons)'
        }
    
    def enhance_content_with_seo(self, title: str, content: str) -> Dict:
        """Enhance content with SEO optimization"""
        enhanced_content = content
        seo_suggestions = []
        
        # Add meta description suggestion
        first_paragraph = content.split('\n\n')[0] if content else ""
        meta_description = first_paragraph[:150] + "..." if len(first_paragraph) > 150 else first_paragraph
        
        # Optimize headings for SEO
        lines = enhanced_content.split('\n')
        enhanced_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                enhanced_lines.append('')
                continue
            
            # Detect and enhance headings
            if self._is_potential_heading(line):
                # Add SEO-friendly heading structure
                if any(keyword in line.lower() for keyword in self.seo_keywords):
                    enhanced_lines.append(f"## {line}")
                else:
                    enhanced_lines.append(f"### {line}")
            else:
                enhanced_lines.append(line)
        
        enhanced_content = '\n'.join(enhanced_lines)
        
        # Add internal linking suggestions
        internal_links = self._suggest_internal_links(content)
        
        # Generate FAQ section if content is long enough
        faq_section = self._generate_faq_section(title, content)
        if faq_section:
            enhanced_content += f"\n\n{faq_section}"
        
        return {
            'enhanced_content': enhanced_content,
            'meta_description': meta_description,
            'internal_links': internal_links,
            'seo_score': self._calculate_seo_score(title, enhanced_content),
            'keyword_density': self._analyze_keyword_density(enhanced_content)
        }
    
    def smart_image_placement(self, content: str, images: List[Dict]) -> str:
        """Intelligently place images within content"""
        if not images or not content:
            return content
        
        paragraphs = content.split('\n\n')
        if len(paragraphs) <= 1:
            return content
        
        enhanced_paragraphs = []
        image_index = 0
        
        for i, paragraph in enumerate(paragraphs):
            enhanced_paragraphs.append(paragraph)
            
            # Smart placement logic
            should_place_image = False
            
            # Place image after introduction (first paragraph if long enough)
            if i == 0 and len(paragraph) > 200 and image_index < len(images):
                should_place_image = True
                caption = "Featured illustration for this article"
            
            # Place images after sections with examples or steps
            elif i > 0 and image_index < len(images):
                para_lower = paragraph.lower()
                if any(pattern in para_lower for pattern in ['example', 'step', 'process', 'method']):
                    should_place_image = True
                    caption = f"Example illustration {image_index + 1}"
                elif i % 3 == 0:  # Every 3rd paragraph
                    should_place_image = True
                    caption = f"Supporting image {image_index + 1}"
            
            if should_place_image and image_index < len(images):
                image = images[image_index]
                image_html = f'\n\n<div class="ai-placed-image text-center my-4">\n'
                image_html += f'<img src="/static/uploads/{image["filename"]}" '
                image_html += f'alt="{caption}" class="img-fluid rounded shadow-sm" '
                image_html += f'style="max-width: 100%; height: auto;">\n'
                image_html += f'<div class="image-caption mt-2">\n'
                image_html += f'<small class="text-muted">{caption}</small>\n'
                image_html += f'</div>\n</div>\n\n'
                
                enhanced_paragraphs.append(image_html)
                image_index += 1
        
        return '\n\n'.join(enhanced_paragraphs)
    
    def generate_content_outline(self, title: str, content: str) -> Dict:
        """Generate a content outline and table of contents"""
        headings = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
        
        if not headings:
            # Generate outline from content structure
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            suggested_headings = []
            
            for i, para in enumerate(paragraphs):
                if len(para) < 100 and not para.endswith('.'):
                    # Likely a heading
                    suggested_headings.append({
                        'level': 2,
                        'text': para,
                        'position': i
                    })
                elif any(pattern in para.lower() for pattern in self.content_patterns.values()):
                    # Content with identifiable patterns
                    for pattern_name, pattern in self.content_patterns.items():
                        if re.search(pattern, para.lower()):
                            suggested_headings.append({
                                'level': 3,
                                'text': f"{pattern_name.title()} Section",
                                'position': i
                            })
                            break
        else:
            suggested_headings = [{'level': len(h.split('#')), 'text': h, 'position': i} 
                                for i, h in enumerate(headings)]
        
        return {
            'outline': suggested_headings,
            'toc_html': self._generate_toc_html(suggested_headings),
            'estimated_sections': len(suggested_headings)
        }
    
    def analyze_content_quality(self, title: str, content: str) -> Dict:
        """Comprehensive content quality analysis"""
        words = len(content.split())
        sentences = len(re.findall(r'[.!?]+', content))
        paragraphs = len([p for p in content.split('\n\n') if p.strip()])
        
        # Quality metrics
        avg_words_per_sentence = words / max(sentences, 1)
        avg_sentences_per_paragraph = sentences / max(paragraphs, 1)
        
        # Content structure analysis
        has_introduction = bool(re.search(self.content_patterns['introduction'], content.lower()))
        has_conclusion = bool(re.search(self.content_patterns['conclusion'], content.lower()))
        has_examples = bool(re.search(self.content_patterns['examples'], content.lower()))
        has_steps = bool(re.search(self.content_patterns['steps'], content.lower()))
        
        # Calculate quality score
        quality_score = 0
        quality_factors = []
        
        # Word count scoring
        if 300 <= words <= 2000:
            quality_score += 25
            quality_factors.append("Good word count")
        elif words > 2000:
            quality_score += 20
            quality_factors.append("Comprehensive content")
        else:
            quality_factors.append("Consider adding more content")
        
        # Structure scoring
        if has_introduction:
            quality_score += 15
            quality_factors.append("Has introduction")
        
        if has_conclusion:
            quality_score += 15
            quality_factors.append("Has conclusion")
        
        if has_examples:
            quality_score += 10
            quality_factors.append("Includes examples")
        
        if has_steps:
            quality_score += 10
            quality_factors.append("Has step-by-step content")
        
        # Readability scoring
        if 10 <= avg_words_per_sentence <= 20:
            quality_score += 15
            quality_factors.append("Good sentence length")
        
        if paragraphs >= 3:
            quality_score += 10
            quality_factors.append("Well-structured paragraphs")
        
        return {
            'quality_score': min(quality_score, 100),
            'quality_factors': quality_factors,
            'structure_analysis': {
                'has_introduction': has_introduction,
                'has_conclusion': has_conclusion,
                'has_examples': has_examples,
                'has_steps': has_steps
            },
            'readability_metrics': {
                'avg_words_per_sentence': round(avg_words_per_sentence, 1),
                'avg_sentences_per_paragraph': round(avg_sentences_per_paragraph, 1),
                'total_paragraphs': paragraphs
            }
        }
    
    def suggest_improvements(self, title: str, content: str) -> List[str]:
        """Generate specific improvement suggestions"""
        suggestions = []
        quality_analysis = self.analyze_content_quality(title, content)
        
        # Structure suggestions
        if not quality_analysis['structure_analysis']['has_introduction']:
            suggestions.append("Add an introduction to hook readers and explain what they'll learn")
        
        if not quality_analysis['structure_analysis']['has_conclusion']:
            suggestions.append("Include a conclusion to summarize key points and provide next steps")
        
        if not quality_analysis['structure_analysis']['has_examples']:
            suggestions.append("Add examples or case studies to illustrate your points")
        
        # Content length suggestions
        words = len(content.split())
        if words < 300:
            suggestions.append("Expand your content to at least 300 words for better SEO")
        elif words > 3000:
            suggestions.append("Consider breaking this into multiple posts for better readability")
        
        # Readability suggestions
        metrics = quality_analysis['readability_metrics']
        if metrics['avg_words_per_sentence'] > 25:
            suggestions.append("Break down long sentences for better readability")
        
        if metrics['total_paragraphs'] < 3:
            suggestions.append("Add more paragraph breaks to improve visual appeal")
        
        # SEO suggestions
        if not any(keyword in title.lower() for keyword in self.seo_keywords):
            suggestions.append("Consider adding SEO-friendly keywords to your title")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def _is_potential_heading(self, line: str) -> bool:
        """Determine if a line could be a heading"""
        return (len(line) < 80 and 
                not line.endswith('.') and 
                not line.endswith(',') and
                not line.startswith('-') and
                not line.startswith('*') and
                len(line.split()) <= 8 and
                len(line.strip()) > 0)
    
    def _suggest_internal_links(self, content: str) -> List[str]:
        """Suggest internal linking opportunities"""
        # This would typically connect to your blog database
        # For now, return generic suggestions
        suggestions = []
        
        if 'tutorial' in content.lower():
            suggestions.append("Link to related tutorials")
        if 'guide' in content.lower():
            suggestions.append("Link to comprehensive guides")
        if 'tips' in content.lower():
            suggestions.append("Link to tips and tricks posts")
        
        return suggestions
    
    def _generate_faq_section(self, title: str, content: str) -> str:
        """Generate FAQ section for long content"""
        if len(content.split()) < 500:
            return ""
        
        # Generate common questions based on content
        faqs = []
        
        if 'how' in title.lower():
            faqs.append({
                'question': f"How do I get started with {title.lower().replace('how to', '').strip()}?",
                'answer': "Follow the step-by-step instructions provided in this guide."
            })
        
        if 'tutorial' in content.lower():
            faqs.append({
                'question': "Do I need any prior experience?",
                'answer': "This tutorial is designed for beginners, but some basic knowledge may be helpful."
            })
        
        if not faqs:
            return ""
        
        faq_html = "## Frequently Asked Questions\n\n"
        for faq in faqs:
            faq_html += f"**{faq['question']}**\n\n{faq['answer']}\n\n"
        
        return faq_html
    
    def _calculate_seo_score(self, title: str, content: str) -> int:
        """Calculate SEO score"""
        score = 0
        
        # Title optimization
        if 30 <= len(title) <= 60:
            score += 20
        
        # Content length
        words = len(content.split())
        if words >= 300:
            score += 20
        
        # Heading structure
        headings = re.findall(r'^#{1,6}\s+', content, re.MULTILINE)
        if headings:
            score += 15
        
        # Keyword usage
        title_words = title.lower().split()
        content_lower = content.lower()
        keyword_mentions = sum(1 for word in title_words if word in content_lower)
        if keyword_mentions >= 2:
            score += 15
        
        # Internal structure
        if '\n\n' in content:  # Has paragraphs
            score += 10
        
        # Meta elements
        if len(content) >= 150:  # Enough for meta description
            score += 10
        
        return min(score, 100)
    
    def _analyze_keyword_density(self, content: str) -> Dict:
        """Analyze keyword density"""
        words = content.lower().split()
        word_count = {}
        
        for word in words:
            if len(word) > 3:  # Only count meaningful words
                word_count[word] = word_count.get(word, 0) + 1
        
        total_words = len(words)
        keyword_density = {}
        
        for word, count in word_count.items():
            density = (count / total_words) * 100
            if density >= 1:  # Only show words with 1%+ density
                keyword_density[word] = round(density, 2)
        
        return dict(sorted(keyword_density.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _generate_toc_html(self, headings: List[Dict]) -> str:
        """Generate HTML table of contents"""
        if not headings:
            return ""
        
        toc_html = '<div class="table-of-contents card p-3 mb-4">\n'
        toc_html += '<h6><i class="fas fa-list me-2"></i>Table of Contents</h6>\n'
        toc_html += '<ul class="list-unstyled mb-0">\n'
        
        for heading in headings:
            indent = "  " * (heading['level'] - 2) if heading['level'] > 2 else ""
            anchor = re.sub(r'[^a-zA-Z0-9\s]', '', heading['text']).replace(' ', '-').lower()
            toc_html += f'{indent}<li><a href="#{anchor}" class="text-decoration-none">{heading["text"]}</a></li>\n'
        
        toc_html += '</ul>\n</div>'
        return toc_html

# Global advanced AI service instance
advanced_ai = AdvancedAIService()