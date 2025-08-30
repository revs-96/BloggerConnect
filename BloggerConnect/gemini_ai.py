"""
Google Gemini AI Integration for BloggerConnect
Provides advanced content enhancement using Google's Gemini API
"""

import os
import json
import re
from typing import Dict, List, Optional
import requests
from textstat import flesch_reading_ease, flesch_kincaid_grade

class GeminiAIService:
    """Google Gemini AI service for content enhancement"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found. Using fallback enhancement.")
    
    def enhance_blog_content(self, title: str, content: str, summary: str = "") -> Dict:
        """
        Enhance blog content using Gemini AI
        Returns enhanced content with improved formatting and structure
        """
        try:
            if self.api_key:
                return self._gemini_enhance_content(title, content, summary)
            else:
                return self._fallback_enhance_content(title, content, summary)
        except Exception as e:
            print(f"AI Enhancement error: {e}")
            return self._fallback_enhance_content(title, content, summary)
    
    def _gemini_enhance_content(self, title: str, content: str, summary: str) -> Dict:
        """Use Gemini API for content enhancement"""
        
        prompt = f"""
        You are an expert content editor and SEO specialist. Please enhance the following blog post to make it more readable, engaging, and well-structured.

        **Original Title:** {title}
        **Original Summary:** {summary}
        **Original Content:** {content}

        Please provide the following improvements:

        1. **Enhanced Content**: Rewrite the content with:
           - Better paragraph structure and flow
           - Clear headings and subheadings (use ## for main headings, ### for subheadings)
           - Improved sentence structure and readability
           - Better transitions between paragraphs
           - More engaging language while maintaining the original meaning
           - Proper formatting with bullet points where appropriate

        2. **Smart Tags**: Generate 5-8 relevant tags based on the content

        3. **SEO Improvements**: Suggest improvements for better search engine optimization

        4. **Content Analysis**: Provide insights about the content quality

        Please format your response as JSON with the following structure:
        {
            "enhanced_content": "The improved content with proper markdown formatting",
            "auto_tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
            "seo_suggestions": ["suggestion1", "suggestion2", "suggestion3"],
            "content_insights": {
                "strengths": ["strength1", "strength2"],
                "improvements": ["improvement1", "improvement2"],
                "target_audience": "description of target audience"
            }
        }

        Make sure the enhanced content is significantly better than the original while preserving all key information and the author's voice.
        """
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    generated_text = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # Try to parse JSON response
                    try:
                        # Extract JSON from the response (in case it's wrapped in markdown)
                        json_match = re.search(r'```json\s*(.*?)\s*```', generated_text, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(1)
                        else:
                            # Try to find JSON in the response
                            json_start = generated_text.find('{')
                            json_end = generated_text.rfind('}') + 1
                            if json_start != -1 and json_end > json_start:
                                json_str = generated_text[json_start:json_end]
                            else:
                                json_str = generated_text
                        
                        ai_response = json.loads(json_str)
                        
                        # Calculate readability metrics
                        enhanced_content = ai_response.get('enhanced_content', content)
                        readability_score = flesch_reading_ease(enhanced_content)
                        grade_level = flesch_kincaid_grade(enhanced_content)
                        
                        return {
                            'enhanced_content': enhanced_content,
                            'auto_tags': ai_response.get('auto_tags', []),
                            'readability': {
                                'score': max(0, min(100, readability_score)),
                                'grade_level': f"Grade {grade_level:.1f}"
                            },
                            'suggestions': ai_response.get('seo_suggestions', []),
                            'word_count': len(enhanced_content.split()),
                            'reading_time': max(1, round(len(enhanced_content.split()) / 200)),
                            'content_insights': ai_response.get('content_insights', {}),
                            'ai_powered': True
                        }
                        
                    except json.JSONDecodeError:
                        # If JSON parsing fails, use the text directly
                        return self._process_text_response(generated_text, content)
                        
            else:
                print(f"Gemini API error: {response.status_code} - {response.text}")
                return self._fallback_enhance_content(title, content, summary)
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return self._fallback_enhance_content(title, content, summary)
    
    def _process_text_response(self, generated_text: str, original_content: str) -> Dict:
        """Process non-JSON text response from Gemini"""
        
        # Extract enhanced content (assume it's the main part of the response)
        enhanced_content = generated_text.strip()
        
        # Generate basic tags from content
        auto_tags = self._extract_keywords(enhanced_content)
        
        # Calculate readability
        readability_score = flesch_reading_ease(enhanced_content)
        grade_level = flesch_kincaid_grade(enhanced_content)
        
        return {
            'enhanced_content': enhanced_content,
            'auto_tags': auto_tags[:8],
            'readability': {
                'score': max(0, min(100, readability_score)),
                'grade_level': f"Grade {grade_level:.1f}"
            },
            'suggestions': ["Content enhanced by AI", "Consider adding more examples"],
            'word_count': len(enhanced_content.split()),
            'reading_time': max(1, round(len(enhanced_content.split()) / 200)),
            'ai_powered': True
        }
    
    def _fallback_enhance_content(self, title: str, content: str, summary: str) -> Dict:
        """Fallback enhancement when API is not available"""
        
        enhanced_content = self._basic_content_enhancement(content)
        auto_tags = self._extract_keywords(content)
        
        # Calculate readability metrics
        readability_score = flesch_reading_ease(enhanced_content)
        grade_level = flesch_kincaid_grade(enhanced_content)
        
        return {
            'enhanced_content': enhanced_content,
            'auto_tags': auto_tags[:8],
            'readability': {
                'score': max(0, min(100, readability_score)),
                'grade_level': f"Grade {grade_level:.1f}"
            },
            'suggestions': [
                "Add more headings to structure your content",
                "Include examples to illustrate your points",
                "Consider adding a conclusion section"
            ],
            'word_count': len(enhanced_content.split()),
            'reading_time': max(1, round(len(enhanced_content.split()) / 200)),
            'ai_powered': False
        }
    
    def _basic_content_enhancement(self, content: str) -> str:
        """Basic content enhancement without API"""
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        enhanced_paragraphs = []
        
        for i, paragraph in enumerate(paragraphs):
            # Add heading for first paragraph if it looks like an introduction
            if i == 0 and len(paragraph) > 100:
                if not paragraph.startswith('#'):
                    enhanced_paragraphs.append("## Introduction\n")
            
            # Detect potential headings (short lines that don't end with punctuation)
            if len(paragraph) < 80 and not paragraph.endswith('.') and not paragraph.startswith('#'):
                enhanced_paragraphs.append(f"## {paragraph}\n")
            else:
                # Improve paragraph formatting
                enhanced_paragraph = self._improve_paragraph(paragraph)
                enhanced_paragraphs.append(enhanced_paragraph)
        
        # Add conclusion if content is long enough
        if len(content.split()) > 300:
            last_para = enhanced_paragraphs[-1] if enhanced_paragraphs else ""
            if not any(word in last_para.lower() for word in ['conclusion', 'summary', 'final']):
                enhanced_paragraphs.append("\n## Conclusion\n\nThese insights provide a solid foundation for understanding the topic. Apply these concepts in your own projects and continue exploring to deepen your knowledge.")
        
        return '\n\n'.join(enhanced_paragraphs)
    
    def _improve_paragraph(self, paragraph: str) -> str:
        """Improve individual paragraph formatting"""
        
        # Split long sentences
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        improved_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Capitalize first letter
                sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                improved_sentences.append(sentence)
        
        return ' '.join(improved_sentences)
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords for tagging"""
        
        # Common stop words to exclude
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 
            'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 
            'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 
            'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use', 'this', 'that',
            'with', 'have', 'from', 'they', 'know', 'want', 'been', 'good', 'much',
            'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long',
            'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        # Count word frequency
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get most frequent words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Extract technical terms and important concepts
        keywords = []
        for word, freq in sorted_words[:15]:
            if freq >= 2:  # Word appears at least twice
                keywords.append(word)
        
        # Add some category-based tags
        content_lower = content.lower()
        if 'tutorial' in content_lower or 'guide' in content_lower:
            keywords.append('tutorial')
        if 'tips' in content_lower or 'advice' in content_lower:
            keywords.append('tips')
        if 'beginner' in content_lower:
            keywords.append('beginner')
        if 'advanced' in content_lower:
            keywords.append('advanced')
        if 'python' in content_lower:
            keywords.append('python')
        if 'javascript' in content_lower:
            keywords.append('javascript')
        if 'web' in content_lower:
            keywords.append('web-development')
        
        return keywords[:8]
    
    def generate_title_suggestions(self, content: str) -> List[str]:
        """Generate title suggestions based on content"""
        
        if not self.api_key:
            return self._fallback_title_suggestions(content)
        
        prompt = f"""
        Based on the following blog content, suggest 5 engaging and SEO-friendly titles:

        Content: {content[:500]}...

        Please provide titles that are:
        - Engaging and click-worthy
        - SEO optimized
        - Clear and descriptive
        - Between 30-60 characters

        Format as a simple list, one title per line.
        """
        
        try:
            headers = {'Content-Type': 'application/json'}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.8,
                    "maxOutputTokens": 300,
                }
            }
            
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    generated_text = result['candidates'][0]['content']['parts'][0]['text']
                    titles = [line.strip() for line in generated_text.split('\n') if line.strip()]
                    return titles[:5]
            
        except Exception as e:
            print(f"Title generation error: {e}")
        
        return self._fallback_title_suggestions(content)
    
    def _fallback_title_suggestions(self, content: str) -> List[str]:
        """Fallback title suggestions"""
        
        # Extract key terms
        keywords = self._extract_keywords(content)
        main_keyword = keywords[0] if keywords else "Topic"
        
        return [
            f"Complete Guide to {main_keyword.title()}",
            f"How to Master {main_keyword.title()}: Step-by-Step Guide",
            f"{main_keyword.title()}: Tips and Best Practices",
            f"Understanding {main_keyword.title()}: A Comprehensive Overview",
            f"The Ultimate {main_keyword.title()} Tutorial"
        ]

# Global Gemini AI service instance
gemini_ai = GeminiAIService()