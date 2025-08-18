"""
AI service for text summarization using rule-based and keyword extraction methods.
"""

import os
import logging
import re
from typing import Optional, Dict, Any, List
from collections import Counter

logger = logging.getLogger(__name__)

class AIService:
    """Service for intelligent text summarization using rule-based methods."""
    
    def __init__(self):
        self.max_length = int(os.getenv("MAX_SUMMARY_LENGTH", "150"))
        self.min_length = int(os.getenv("MIN_SUMMARY_LENGTH", "30"))
        
        # Common stop words for better text processing
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'upon',
            'against', 'within', 'without', 'throughout', 'towards', 'except',
            'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could',
            'can', 'may', 'might', 'must', 'shall', 'this', 'that', 'these', 
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their'
        }
        
        # Technical keywords that are important for GitHub issues
        self.tech_keywords = {
            'bug', 'error', 'fix', 'issue', 'problem', 'feature', 'enhancement',
            'request', 'implement', 'add', 'remove', 'update', 'upgrade', 'improve',
            'performance', 'security', 'documentation', 'test', 'testing', 'refactor',
            'api', 'ui', 'ux', 'database', 'server', 'client', 'frontend', 'backend',
            'mobile', 'web', 'desktop', 'crash', 'freeze', 'slow', 'fast', 'optimize'
        }
        
        logger.info("AI Service initialized with rule-based summarization")
    
    def _initialize_model(self):
        """Initialize the summarization service."""
        # No external model needed for rule-based approach
        logger.info("Rule-based summarization service ready")
    
    def summarize_text(self, text: str, max_length: Optional[int] = None, min_length: Optional[int] = None) -> str:
        """
        Summarize the given text using rule-based intelligent analysis.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary (optional)
            min_length: Minimum length of summary (optional)
            
        Returns:
            Summarized text or error message
        """
        if not text or not text.strip():
            return "No content available to summarize."
        
        try:
            # Clean and prepare text
            text = self._preprocess_text(text)
            
            # Check if text is too short to summarize meaningfully
            if len(text.split()) < 10:
                return text  # Return original text if too short
            
            # Set summary length parameters
            max_len = max_length or self.max_length
            min_len = min_length or self.min_length
            
            # Generate intelligent summary using rule-based approach
            summary = self._generate_rule_based_summary(text, max_len)
            
            # Post-process the summary
            summary = self._postprocess_summary(summary)
            
            # Ensure minimum length if possible
            if len(summary) < min_len and len(text.split()) > 20:
                summary = self._expand_summary(text, summary, min_len)
            
            logger.debug(f"Generated summary: {len(summary)} characters from {len(text)} character input")
            return summary
            
        except Exception as e:
            logger.error(f"Error during text summarization: {str(e)}")
            return "Unable to generate summary. The issue content may be too complex or contain unsupported formatting."
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text before summarization.
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            Cleaned text ready for summarization
        """
        # Remove excessive whitespace and newlines
        text = " ".join(text.split())
        
        # Remove markdown formatting and code blocks
        text = re.sub(r'```[^`]*```', ' [code block] ', text)
        text = re.sub(r'`[^`]*`', ' [code] ', text)
        text = re.sub(r'#{1,6}\s*', '', text)  # Remove markdown headers
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Convert links to text
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' [URL] ', text)
        
        # Clean up extra spaces
        text = " ".join(text.split())
        
        # Truncate if too long (limit to reasonable length)
        max_chars = 2000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        return text
    
    def _generate_rule_based_summary(self, text: str, max_length: int) -> str:
        """
        Generate summary using rule-based analysis.
        
        Args:
            text: Preprocessed text to summarize
            max_length: Maximum summary length
            
        Returns:
            Generated summary
        """
        sentences = self._split_into_sentences(text)
        if not sentences:
            return "Unable to analyze the content structure."
        
        # Score sentences based on importance
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            score = self._score_sentence(sentence, text)
            sentence_scores[i] = score
        
        # Select top sentences
        num_sentences = min(3, max(1, len(sentences) // 3))
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
        
        # Sort selected sentences by original order
        selected_indices = sorted([idx for idx, score in top_sentences])
        summary_sentences = [sentences[i] for i in selected_indices]
        
        summary = " ".join(summary_sentences)
        
        # Ensure it fits within max_length
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
            
        return summary
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        return sentences
    
    def _score_sentence(self, sentence: str, full_text: str) -> float:
        """Score a sentence based on importance indicators."""
        score = 0.0
        sentence_lower = sentence.lower()
        
        # Length bonus (not too short, not too long)
        length = len(sentence.split())
        if 5 <= length <= 20:
            score += 1.0
        elif length > 20:
            score += 0.5
        
        # Technical keyword bonus
        tech_words = sum(1 for word in self.tech_keywords if word in sentence_lower)
        score += tech_words * 0.5
        
        # Position bonus (first sentences are often important)
        if sentence in full_text[:200]:
            score += 0.5
            
        # Question or action indicator
        if any(word in sentence_lower for word in ['how', 'what', 'why', 'when', 'where', 'should', 'need', 'want']):
            score += 0.3
            
        # Error/bug indicators
        if any(word in sentence_lower for word in ['error', 'bug', 'fail', 'issue', 'problem', 'broken']):
            score += 0.4
            
        return score
    
    def _expand_summary(self, text: str, summary: str, min_length: int) -> str:
        """Expand summary if it's too short."""
        if len(summary) >= min_length:
            return summary
            
        # Add key technical details or context
        words = text.lower().split()
        tech_context = []
        
        for keyword in self.tech_keywords:
            if keyword in words and keyword not in summary.lower():
                tech_context.append(keyword)
                if len(tech_context) >= 3:
                    break
        
        if tech_context:
            addition = f" Related to: {', '.join(tech_context)}."
            if len(summary + addition) <= min_length + 20:
                summary += addition
                
        return summary
    
    def _postprocess_summary(self, summary: str) -> str:
        """
        Post-process the generated summary.
        
        Args:
            summary: Raw summary from the model
            
        Returns:
            Cleaned and formatted summary
        """
        if not summary:
            return "No summary could be generated."
            
        # Clean up extra spaces
        summary = " ".join(summary.split())
        
        # Ensure proper capitalization
        if summary and not summary[0].isupper():
            summary = summary[0].upper() + summary[1:]
        
        # Ensure proper punctuation
        if summary and summary[-1] not in '.!?':
            summary += '.'
        
        return summary
    
    def batch_summarize(self, texts: list, max_length: Optional[int] = None, min_length: Optional[int] = None) -> list:
        """
        Summarize multiple texts in batch for better performance.
        
        Args:
            texts: List of texts to summarize
            max_length: Maximum length of summaries
            min_length: Minimum length of summaries
            
        Returns:
            List of summarized texts
        """
        summaries = []
        for text in texts:
            summary = self.summarize_text(text, max_length, min_length)
            summaries.append(summary)
        
        return summaries
    
    def health_check(self) -> bool:
        """
        Check if the AI service is working properly.
        
        Returns:
            Boolean indicating service health
        """
        try:
            # Test with a simple text
            test_text = "This is a test bug report to check if the intelligent summarization service is working properly. The application crashes when users click the submit button."
            result = self.summarize_text(test_text)
            
            return len(result) > 0 and "unable to" not in result.lower()
            
        except Exception as e:
            logger.error(f"AI service health check failed: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the summarization service.
        
        Returns:
            Service information dictionary
        """
        return {
            "model_type": "rule_based_intelligent_summarization",
            "method": "keyword_extraction_and_sentence_scoring",
            "max_length": self.max_length,
            "min_length": self.min_length,
            "is_loaded": True,
            "features": ["technical_keyword_detection", "sentence_importance_scoring", "context_aware_summarization"]
        }
