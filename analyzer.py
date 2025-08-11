import re
import nltk
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Optional
import string
import logging
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
import config

class KeywordAnalyzer:
    """
    Advanced keyword analysis engine for SEO content analysis
    Handles text processing, keyword extraction, and frequency analysis
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Download required NLTK data
        self.setup_nltk()
        
        # Initialize text processing tools
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        
        # Load stopwords
        self.stop_words = set(stopwords.words('english'))
        self.stop_words.update(config.CUSTOM_STOPWORDS)
        
        # Common SEO-irrelevant words to filter
        self.seo_irrelevant_words = {
            'said', 'says', 'tell', 'told', 'ask', 'asked', 'think', 'thought',
            'know', 'knew', 'see', 'saw', 'look', 'looked', 'come', 'came',
            'go', 'went', 'get', 'got', 'make', 'made', 'take', 'took',
            'give', 'gave', 'find', 'found', 'work', 'worked', 'call', 'called',
            'try', 'tried', 'use', 'used', 'want', 'wanted', 'need', 'needed',
            'help', 'helped', 'start', 'started', 'stop', 'stopped',
            'today', 'yesterday', 'tomorrow', 'monday', 'tuesday', 'wednesday',
            'thursday', 'friday', 'saturday', 'sunday', 'january', 'february',
            'march', 'april', 'may', 'june', 'july', 'august', 'september',
            'october', 'november', 'december'
        }
        
    def setup_nltk(self):
        """Download required NLTK data packages with SSL handling"""
        import ssl

        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context

        nltk_packages = [
            'punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger',
            'maxent_ne_chunker', 'words', 'omw-1.4'
        ]
        
        for package in nltk_packages:
            try:
                nltk.download(package, quiet=True)
            except (OSError, IOError) as e:
                self.logger.warning("Could not download NLTK package %s: %s", package, str(e).replace('\n', '\\n').replace('\r', '\\r'))
            except Exception as e:
                self.logger.error("Unexpected error downloading NLTK package %s: %s", package, str(e).replace('\n', '\\n').replace('\r', '\\r'))
                # Attempt to create data directory manually if it doesn't exist
                try:
                    import os
                    nltk_data_dir = os.path.expanduser('~/nltk_data')
                    os.makedirs(nltk_data_dir, exist_ok=True)
                except Exception as dir_e:
                    self.logger.error(f"Could not create NLTK data directory: {str(dir_e)}")
                
    def preprocess_text(self, text: str, preserve_phrases: bool = True) -> str:
        """
        Preprocess text for keyword analysis
        
        Args:
            text: Raw text content
            preserve_phrases: Whether to preserve multi-word phrases
            
        Returns:
            Cleaned and preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove HTML tags if any
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', ' ', text)
        
        # Remove excessive punctuation but preserve sentence structure
        if preserve_phrases:
            # Keep basic punctuation for phrase detection
            text = re.sub(r'[^\w\s\.\,\!\?\-\:\;]', ' ', text)
        else:
            # Remove all punctuation except apostrophes
            text = re.sub(r'[^\w\s\']', ' ', text)
        
        # Remove numbers unless they're part of important terms
        text = re.sub(r'\b\d+\b', ' ', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
        
    def extract_keywords(self, text: str, min_length: int = 2, max_length: int = 50) -> List[str]:
        """
        Extract individual keywords from text
        
        Args:
            text: Preprocessed text
            min_length: Minimum keyword length
            max_length: Maximum keyword length
            
        Returns:
            List of keywords
        """
        # Tokenize text
        tokens = word_tokenize(text)
        
        # Filter tokens
        keywords = []
        for token in tokens:
            # Skip if too short or too long
            if len(token) < min_length or len(token) > max_length:
                continue
                
            # Skip if all punctuation
            if all(c in string.punctuation for c in token):
                continue
                
            # Skip stopwords
            if token.lower() in self.stop_words:
                continue
                
            # Skip SEO-irrelevant words
            if token.lower() in self.seo_irrelevant_words:
                continue
                
            # Skip single characters
            if len(token) == 1:
                continue
                
            keywords.append(token.lower())
            
        return keywords
        
    def extract_phrases(self, text: str, min_words: int = 2, max_words: int = 5) -> List[str]:
        """
        Extract meaningful phrases from text
        
        Args:
            text: Preprocessed text
            min_words: Minimum words in phrase
            max_words: Maximum words in phrase
            
        Returns:
            List of phrases
        """
        phrases = []
        
        # Split into sentences
        sentences = sent_tokenize(text)
        
        for sentence in sentences:
            # Tokenize sentence
            words = word_tokenize(sentence.lower())
            
            # Generate n-grams
            for phrase_length in range(min_words, max_words + 1):
                for i in range(len(words) - phrase_length + 1):
                    phrase_words = words[i:i + phrase_length]
                    
                    # Filter phrase
                    if self.is_valid_phrase(phrase_words):
                        phrase = ' '.join(phrase_words)
                        phrases.append(phrase)
                        
        return phrases
        
    def is_valid_phrase(self, words: List[str]) -> bool:
        """
        Check if a phrase is valid for SEO analysis
        
        Args:
            words: List of words in phrase
            
        Returns:
            True if phrase is valid
        """
        # Must have at least one content word (not all stopwords)
        content_words = [w for w in words if w not in self.stop_words]
        if not content_words:
            return False
            
        # Must not start or end with common connector words
        connector_words = {'and', 'or', 'but', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        if words[0] in connector_words or words[-1] in connector_words:
            return False
            
        # Must not be all numbers or punctuation
        if all(w.isdigit() or w in string.punctuation for w in words):
            return False
            
        # Must have reasonable length
        phrase_text = ' '.join(words)
        if len(phrase_text) < 4 or len(phrase_text) > 100:
            return False
            
        return True
        
    def analyze_text(self, text: str, min_frequency: int = 2, 
                    exclude_common_words: bool = True,
                    custom_stopwords: List[str] = None) -> Dict[str, Dict]:
        """
        Perform comprehensive keyword analysis on text
        
        Args:
            text: Text content to analyze
            min_frequency: Minimum frequency for keyword inclusion
            exclude_common_words: Whether to exclude common words
            custom_stopwords: Additional stopwords to exclude
            
        Returns:
            Dictionary of keywords with analysis data
        """
        if custom_stopwords:
            self.stop_words.update(set(custom_stopwords))
            
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # Extract keywords and phrases
        keywords = self.extract_keywords(processed_text)
        phrases = self.extract_phrases(processed_text)
        
        # Combine keywords and phrases
        all_terms = keywords + phrases
        
        # Count frequencies
        term_counts = Counter(all_terms)
        
        # Filter by minimum frequency
        filtered_terms = {term: count for term, count in term_counts.items() 
                         if count >= min_frequency}
        
        # Analyze each term
        keyword_analysis = {}
        for term, frequency in filtered_terms.items():
            analysis_data = self.analyze_keyword(term, processed_text, frequency)
            keyword_analysis[term] = analysis_data
            
        return keyword_analysis
        
    def analyze_keyword(self, keyword: str, text: str, frequency: int) -> Dict:
        """
        Analyze individual keyword for SEO relevance
        
        Args:
            keyword: Keyword to analyze
            text: Full text content
            frequency: Keyword frequency
            
        Returns:
            Dictionary with keyword analysis data
        """
        analysis = {
            'frequency': frequency,
            'positions': [],
            'contexts': [],
            'sentiment_score': 0,
            'importance_score': 0,
            'word_count': len(keyword.split()),
            'character_length': len(keyword)
        }
        
        # Find keyword positions and contexts
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        # Find keyword positions using regex for better performance
        import re
        pattern = re.escape(keyword_lower)
        for match in re.finditer(pattern, text_lower):
            pos = match.start()
            analysis['positions'].append(pos)
            
            # Extract context (surrounding words)
            context_start = max(0, pos - 50)
            context_end = min(len(text), pos + len(keyword) + 50)
            context = text[context_start:context_end].strip()
            analysis['contexts'].append(context)
            
        # Calculate importance score
        analysis['importance_score'] = self.calculate_importance_score(
            keyword, frequency, len(text.split()), analysis['positions']
        )
        
        return analysis
        
    def calculate_importance_score(self, keyword: str, frequency: int, 
                                 total_words: int, positions: List[int]) -> float:
        """
        Calculate importance score for keyword
        
        Args:
            keyword: Keyword text
            frequency: Keyword frequency
            total_words: Total words in text
            positions: List of keyword positions
            
        Returns:
            Importance score (0-100)
        """
        # Base score from frequency
        frequency_score = min(frequency * 10, 50)
        
        # Length bonus (longer keywords often more specific)
        length_bonus = min(len(keyword.split()) * 5, 20)
        
        # Position bonus (keywords near beginning are often more important)
        position_bonus = 0
        if positions:
            # Average position as percentage of text
            avg_position = sum(positions) / len(positions)
            position_percentage = avg_position / total_words if total_words > 0 else 0
            
            # Bonus for appearing early in text
            if position_percentage < 0.1:
                position_bonus = 15
            elif position_percentage < 0.25:
                position_bonus = 10
            elif position_percentage < 0.5:
                position_bonus = 5
                
        # Density score
        density = (frequency / total_words * 100) if total_words > 0 else 0
        density_score = min(density * 2, 15)
        
        total_score = frequency_score + length_bonus + position_bonus + density_score
        return min(total_score, 100)
        
    def analyze_multiple_texts(self, texts: List[str], min_frequency: int = 2,
                             exclude_common_words: bool = True,
                             custom_stopwords: List[str] = None,
                             batch_size: int = 5) -> Dict[str, Dict]:
        """
        Analyze keywords across multiple texts (competitor analysis) with batch processing
        
        Args:
            texts: List of text content to analyze
            min_frequency: Minimum frequency across all texts
            exclude_common_words: Whether to exclude common words
            custom_stopwords: Additional stopwords to exclude
            batch_size: Number of texts to process in each batch
            
        Returns:
            Dictionary of keywords with aggregate analysis data
        """
        if not texts:
            return {}
            
        # Initialize aggregated results
        aggregated_keywords = defaultdict(lambda: {
            'frequency': 0,
            'sources': [],
            'total_importance': 0,
            'avg_importance': 0,
            'document_frequency': 0,
            'avg_position': 0
        })
        
        # Process texts in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            self.logger.info("Processing batch %d/%d", i//batch_size + 1, (len(texts) + batch_size - 1)//batch_size)
            
            # Analyze each text in the batch
            batch_analyses = []
            for j, text in enumerate(batch):
                try:
                    analysis = self.analyze_text(text, min_frequency=1, 
                                             exclude_common_words=exclude_common_words,
                                             custom_stopwords=custom_stopwords)
                    batch_analyses.append(analysis)
                except Exception as e:
                    self.logger.error("Error analyzing text %d: %s", i+j, str(e).replace('\n', '\\n').replace('\r', '\\r'))
                    continue
            
            # Aggregate batch results
            for j, analysis in enumerate(batch_analyses):
                for keyword, data in analysis.items():
                    agg_data = aggregated_keywords[keyword]
                    agg_data['frequency'] += data['frequency']
                    agg_data['sources'].append(i + j)
                    agg_data['total_importance'] += data['importance_score']
                    agg_data['document_frequency'] += 1
            
            # Clear batch data to free memory
            batch_analyses.clear()
        
        # Calculate final averages and filter by minimum frequency
        final_keywords = {}
        for keyword, data in aggregated_keywords.items():
            if data['frequency'] >= min_frequency:
                data['avg_importance'] = data['total_importance'] / data['document_frequency']
                data['avg_position'] = data['frequency'] / len(texts)
                final_keywords[keyword] = data
        
        return final_keywords
        
    def extract_named_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text (organizations, locations, people)
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of entity types and entities
        """
        entities = defaultdict(list)
        
        try:
            # Tokenize and tag parts of speech
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            
            # Extract named entities
            chunks = ne_chunk(pos_tags)
            
            for chunk in chunks:
                if hasattr(chunk, 'label'):
                    entity_text = ' '.join([token for token, pos in chunk.leaves()])
                    entity_type = chunk.label()
                    entities[entity_type].append(entity_text)
                    
        except Exception as e:
            self.logger.warning(f"Error extracting named entities: {str(e)}")
            
        return dict(entities)
        
    def calculate_keyword_density(self, text: str, keyword: str) -> float:
        """
        Calculate keyword density percentage
        
        Args:
            text: Text content
            keyword: Keyword to calculate density for
            
        Returns:
            Keyword density as percentage
        """
        text_words = text.lower().split()
        keyword_words = keyword.lower().split()
        
        if len(keyword_words) == 1:
            # Single word keyword
            keyword_count = text_words.count(keyword_words[0])
        else:
            # Multi-word keyword
            keyword_count = 0
            for i in range(len(text_words) - len(keyword_words) + 1):
                if text_words[i:i + len(keyword_words)] == keyword_words:
                    keyword_count += 1
                    
        total_words = len(text_words)
        density = (keyword_count / total_words * 100) if total_words > 0 else 0
        
        return round(density, 2)
        
    def find_semantic_keywords(self, primary_keyword: str, text: str, 
                             top_n: int = 20) -> List[Tuple[str, float]]:
        """
        Find semantically related keywords in text
        
        Args:
            primary_keyword: Main keyword to find related terms for
            text: Text to search in
            top_n: Number of related keywords to return
            
        Returns:
            List of tuples (keyword, relevance_score)
        """
        # This is a simplified implementation
        # In production, you might use word embeddings or semantic analysis
        
        keywords = self.analyze_text(text, min_frequency=1)
        primary_words = set(primary_keyword.lower().split())
        
        semantic_keywords = []
        for keyword, data in keywords.items():
            keyword_words = set(keyword.lower().split())
            
            # Calculate semantic similarity (simplified)
            overlap = len(primary_words.intersection(keyword_words))
            similarity_score = overlap / len(primary_words.union(keyword_words))
            
            # Boost score for keywords that appear near primary keyword
            context_boost = 0
            for context in data.get('contexts', []):
                if primary_keyword.lower() in context.lower():
                    context_boost += 0.1
                    
            total_score = similarity_score + context_boost + (data['importance_score'] / 100)
            semantic_keywords.append((keyword, total_score))
            
        # Sort by relevance and return top N
        semantic_keywords.sort(key=lambda x: x[1], reverse=True)
        return semantic_keywords[:top_n]
        
    def generate_keyword_report(self, keyword_analysis: Dict[str, Dict]) -> str:
        """
        Generate formatted keyword analysis report
        
        Args:
            keyword_analysis: Keyword analysis results
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("KEYWORD ANALYSIS REPORT")
        report.append("=" * 50)
        
        # Sort keywords by importance score
        sorted_keywords = sorted(keyword_analysis.items(), 
                               key=lambda x: x[1].get('importance_score', 0), 
                               reverse=True)
        
        report.append(f"\nTotal Keywords Found: {len(sorted_keywords)}")
        report.append(f"Top Keywords by Importance:\n")
        
        for i, (keyword, data) in enumerate(sorted_keywords[:20], 1):
            frequency = data.get('frequency', 0)
            importance = data.get('importance_score', 0)
            word_count = data.get('word_count', 1)
            
            report.append(f"{i:2d}. {keyword:<30} | Freq: {frequency:3d} | "
                         f"Importance: {importance:5.1f} | Words: {word_count}")
                         
        return '\n'.join(report)