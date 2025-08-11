from typing import Dict, List, Set, Tuple, Optional
import logging
from collections import defaultdict
import math

class ContentGapFinder:
    """
    Advanced content gap analysis engine for SEO optimization
    Identifies missing keywords and content opportunities
    """
    
    # Constants for scoring and classification
    FREQUENCY_SCORE_MULTIPLIER = 2
    DOC_FREQ_SCORE_MULTIPLIER = 5
    IMPORTANCE_SCORE_DIVISOR = 5
    LENGTH_BONUS_MULTIPLIER = 2
    RELEVANCE_BONUS_MULTIPLIER = 3
    SIMILARITY_THRESHOLD = 0.3
    PARTIAL_MATCH_BONUS = 0.1
    MAX_PARTIAL_BONUS = 0.3
    
    # Word count thresholds
    SINGLE_WORD_COUNT = 1
    TWO_WORD_COUNT = 2
    LONG_TAIL_MIN_WORDS = 4
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Priority thresholds for opportunity scoring
        self.priority_thresholds = {
            'high': 75,
            'medium': 50,
            'low': 25
        }
        
        # Keyword classification indicators
        self.commercial_indicators = {
            'buy', 'purchase', 'order', 'shop', 'sale', 'deal', 'discount',
            'cheap', 'best', 'top', 'review', 'compare', 'vs', 'versus'
        }
        
        self.informational_indicators = {
            'how', 'what', 'why', 'when', 'where', 'guide', 'tutorial',
            'tips', 'learn', 'understand', 'explain', 'definition'
        }
        
        self.local_indicators = {
            'near', 'local', 'nearby', 'around', 'close', 'in', 'at'
        }
        
        self.transactional_indicators = {
            'buy', 'purchase', 'order', 'book', 'hire', 'contact',
            'quote', 'price', 'cost', 'signup', 'register'
        }
        
        self.navigational_indicators = {
            'login', 'website', 'homepage', 'official', 'store',
            'shop', 'account', 'dashboard'
        }
        
        self.competitive_terms = {
            'best', 'top', 'cheap', 'free', 'review', 'buy', 'online',
            'service', 'company', 'business', 'professional'
        }
        
    def find_missing_keywords(self, competitor_keywords: Dict[str, Dict], 
                            user_keywords: Dict[str, Dict],
                            similarity_threshold: float = 0.8) -> List[Dict]:
        """
        Identify keywords present in competitor content but missing from user content
        
        Args:
            competitor_keywords: Analyzed competitor keyword data
            user_keywords: Analyzed user content keyword data
            similarity_threshold: Threshold for considering keywords similar
            
        Returns:
            List of missing keyword opportunities with analysis data
        """
        missing_opportunities = []
        
        # Get sets of keywords for comparison
        competitor_terms = set(competitor_keywords.keys())
        user_terms = set(user_keywords.keys()) if user_keywords else set()
        
        self.logger.info("Analyzing %d competitor keywords against %d user keywords", len(competitor_terms), len(user_terms))
        
        # Find directly missing keywords
        directly_missing = competitor_terms - user_terms
        
        # Analyze each missing keyword
        for keyword in directly_missing:
            competitor_data = competitor_keywords[keyword]
            opportunity = self.analyze_keyword_opportunity(keyword, competitor_data, user_keywords)
            missing_opportunities.append(opportunity)
            
        # Find semantically similar but potentially missing variations
        semantic_gaps = self.find_semantic_gaps(competitor_keywords, user_keywords, similarity_threshold)
        missing_opportunities.extend(semantic_gaps)
        
        # Sort opportunities by score
        missing_opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        self.logger.info("Found %d keyword opportunities", len(missing_opportunities))
        
        return missing_opportunities
        
    def analyze_keyword_opportunity(self, keyword: str, competitor_data: Dict, 
                                  user_keywords: Dict[str, Dict]) -> Dict:
        """
        Analyze the opportunity value of a missing keyword
        
        Args:
            keyword: The missing keyword
            competitor_data: Data about keyword from competitor analysis
            user_keywords: User's existing keyword data
            
        Returns:
            Dictionary with opportunity analysis
        """
        # Base opportunity score from competitor usage
        frequency = competitor_data.get('frequency', 0)
        document_frequency = competitor_data.get('document_frequency', 0)
        avg_importance = competitor_data.get('avg_importance', 0)
        
        # Calculate opportunity score
        opportunity_score = self.calculate_opportunity_score(
            frequency, document_frequency, avg_importance, keyword, user_keywords
        )
        
        # Determine priority level
        priority = self.determine_priority(opportunity_score)
        
        # Analyze keyword characteristics
        characteristics = self.analyze_keyword_characteristics(keyword)
        
        # Generate recommendations
        recommendations = self.generate_keyword_recommendations(keyword, competitor_data)
        
        opportunity = {
            'keyword': keyword,
            'opportunity_score': opportunity_score,
            'priority': priority,
            'competitor_frequency': frequency,
            'found_in_sites': document_frequency,
            'avg_competitor_importance': avg_importance,
            'keyword_type': characteristics['type'],
            'word_count': len(keyword.split()),
            'estimated_difficulty': characteristics['difficulty'],
            'search_intent': characteristics['intent'],
            'recommendations': recommendations,
            'related_user_keywords': self.find_related_user_keywords(keyword, user_keywords)
        }
        
        return opportunity
        
    def calculate_opportunity_score(self, frequency: int, document_frequency: int, 
                                  avg_importance: float, keyword: str,
                                  user_keywords: Dict[str, Dict]) -> float:
        """
        Calculate comprehensive opportunity score for missing keyword
        
        Args:
            frequency: Total frequency across competitor sites
            document_frequency: Number of competitor sites using keyword
            avg_importance: Average importance score from competitors
            keyword: The keyword being analyzed
            user_keywords: User's existing keywords for context
            
        Returns:
            Opportunity score (0-100)
        """
        # Frequency component (0-30 points)
        frequency_score = min(frequency * self.FREQUENCY_SCORE_MULTIPLIER, 30)
        
        # Document frequency component (0-25 points)
        # Higher score if keyword appears on multiple competitor sites
        doc_freq_score = min(document_frequency * self.DOC_FREQ_SCORE_MULTIPLIER, 25)
        
        # Importance component (0-20 points)
        importance_score = min(avg_importance / self.IMPORTANCE_SCORE_DIVISOR, 20)
        
        # Keyword length bonus (0-10 points)
        # Longer keywords often more specific and valuable
        length_bonus = min(len(keyword.split()) * self.LENGTH_BONUS_MULTIPLIER, 10)
        
        # Content relevance bonus (0-15 points)
        relevance_bonus = self.calculate_content_relevance(keyword, user_keywords)
        
        total_score = frequency_score + doc_freq_score + importance_score + length_bonus + relevance_bonus
        
        return min(total_score, 100)
        
    def calculate_content_relevance(self, keyword: str, user_keywords: Dict[str, Dict]) -> float:
        """
        Calculate how relevant keyword is to existing user content
        
        Args:
            keyword: Keyword to analyze
            user_keywords: User's existing keywords
            
        Returns:
            Relevance score (0-15)
        """
        if not user_keywords:
            return 0
            
        relevance_score = 0
        keyword_words = set(keyword.lower().split())
        
        for user_keyword in user_keywords.keys():
            user_words = set(user_keyword.lower().split())
            
            # Calculate word overlap
            overlap = len(keyword_words.intersection(user_words))
            union = len(keyword_words.union(user_words))
            
            if union > 0:
                similarity = overlap / union
                relevance_score += similarity * self.RELEVANCE_BONUS_MULTIPLIER
                
        return min(relevance_score, 15)
        
    def determine_priority(self, opportunity_score: float) -> str:
        """
        Determine priority level based on opportunity score
        
        Args:
            opportunity_score: Calculated opportunity score
            
        Returns:
            Priority level string
        """
        if opportunity_score >= self.priority_thresholds['high']:
            return 'high'
        elif opportunity_score >= self.priority_thresholds['medium']:
            return 'medium'
        else:
            return 'low'
            
    def analyze_keyword_characteristics(self, keyword: str) -> Dict:
        """
        Analyze characteristics of keyword for strategic insights
        
        Args:
            keyword: Keyword to analyze
            
        Returns:
            Dictionary with keyword characteristics
        """
        characteristics = {
            'type': self.classify_keyword_type(keyword),
            'difficulty': self.estimate_keyword_difficulty(keyword),
            'intent': self.classify_search_intent(keyword)
        }
        
        return characteristics
        
    def classify_keyword_type(self, keyword: str) -> str:
        """
        Classify keyword type for strategic planning
        
        Args:
            keyword: Keyword to classify
            
        Returns:
            Keyword type classification
        """
        word_count = len(keyword.split())
        
        # Use class attribute indicators
        
        keyword_lower = keyword.lower()
        
        # Check for commercial keywords
        if any(indicator in keyword_lower for indicator in self.commercial_indicators):
            return 'commercial'
        
        # Check for local keywords
        if any(indicator in keyword_lower for indicator in self.local_indicators):
            return 'local'
        
        # Check for informational keywords
        if any(indicator in keyword_lower for indicator in self.informational_indicators):
            return 'informational'
        
        # Classify by length
        if word_count == self.SINGLE_WORD_COUNT:
            return 'head'
        elif word_count == self.TWO_WORD_COUNT:
            return 'body'
        else:
            return 'long_tail'
            
    def estimate_keyword_difficulty(self, keyword: str) -> str:
        """
        Estimate SEO difficulty for keyword
        
        Args:
            keyword: Keyword to analyze
            
        Returns:
            Difficulty level estimate
        """
        word_count = len(keyword.split())
        
        # Use class attribute competitive terms
        
        keyword_lower = keyword.lower()
        
        # Single word keywords are typically harder
        if word_count == self.SINGLE_WORD_COUNT:
            return 'high'
        
        # Keywords with competitive terms
        if any(term in keyword_lower for term in self.competitive_terms):
            return 'high' if word_count <= self.TWO_WORD_COUNT else 'medium'
        
        # Long tail keywords are typically easier
        if word_count >= self.LONG_TAIL_MIN_WORDS:
            return 'low'
        
        # Default to medium
        return 'medium'
        
    def classify_search_intent(self, keyword: str) -> str:
        """
        Classify search intent for keyword
        
        Args:
            keyword: Keyword to analyze
            
        Returns:
            Search intent classification
        """
        keyword_lower = keyword.lower()
        
        # Use class attribute indicators
        
        if any(word in keyword_lower for word in self.transactional_indicators):
            return 'transactional'
        elif any(word in keyword_lower for word in self.navigational_indicators):
            return 'navigational'
        elif any(word in keyword_lower for word in self.informational_indicators):
            return 'informational'
        else:
            return 'commercial'
            
    def generate_keyword_recommendations(self, keyword: str, competitor_data: Dict) -> List[str]:
        """
        Generate actionable recommendations for keyword optimization
        
        Args:
            keyword: Missing keyword
            competitor_data: Competitor usage data
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        frequency = competitor_data.get('frequency', 0)
        document_frequency = competitor_data.get('document_frequency', 0)
        
        # High frequency recommendations
        if frequency > 10:
            recommendations.append(f"High-priority target: appears {frequency} times across competitor sites")
            
        # Multiple site usage
        if document_frequency > 3:
            recommendations.append(f"Strong opportunity: used by {document_frequency} different competitors")
            
        # Content type recommendations
        keyword_type = self.classify_keyword_type(keyword)
        if keyword_type == 'informational':
            recommendations.append("Create comprehensive guide or tutorial content")
        elif keyword_type == 'commercial':
            recommendations.append("Optimize product/service pages and create comparison content")
        elif keyword_type == 'local':
            recommendations.append("Optimize for local SEO and create location-specific content")
        elif keyword_type == 'long_tail':
            recommendations.append("Target with specific, detailed content pages")
            
        # Intent-based recommendations
        intent = self.classify_search_intent(keyword)
        if intent == 'transactional':
            recommendations.append("Focus on conversion-optimized landing pages")
        elif intent == 'informational':
            recommendations.append("Create educational blog posts or resource pages")
            
        return recommendations
        
    def find_related_user_keywords(self, keyword: str, user_keywords: Dict[str, Dict]) -> List[str]:
        """
        Find user's existing keywords related to the missing keyword
        
        Args:
            keyword: Missing keyword
            user_keywords: User's existing keywords
            
        Returns:
            List of related user keywords
        """
        if not user_keywords:
            return []
            
        related_keywords = []
        keyword_words = set(keyword.lower().split())
        
        for user_keyword in user_keywords.keys():
            user_words = set(user_keyword.lower().split())
            
            # Check for word overlap
            overlap = len(keyword_words.intersection(user_words))
            if overlap > 0:
                similarity_score = overlap / len(keyword_words.union(user_words))
                if similarity_score >= self.SIMILARITY_THRESHOLD:
                    related_keywords.append(user_keyword)
                    
        return related_keywords[:5]  # Return top 5 related keywords
        
    def find_semantic_gaps(self, competitor_keywords: Dict[str, Dict], 
                          user_keywords: Dict[str, Dict],
                          similarity_threshold: float = 0.8) -> List[Dict]:
        """
        Find semantic keyword gaps using word similarity
        
        Args:
            competitor_keywords: Competitor keyword data
            user_keywords: User keyword data
            similarity_threshold: Threshold for semantic similarity
            
        Returns:
            List of semantic gap opportunities
        """
        semantic_gaps = []
        
        if not user_keywords:
            return semantic_gaps
            
        for comp_keyword, comp_data in competitor_keywords.items():
            # Check if semantically similar keyword exists in user content
            has_similar = False
            
            for user_keyword in user_keywords.keys():
                similarity = self.calculate_semantic_similarity(comp_keyword, user_keyword)
                if similarity >= similarity_threshold:
                    has_similar = True
                    break
                    
            # If no similar keyword found, it's a potential gap
            if not has_similar:
                gap_opportunity = self.analyze_keyword_opportunity(comp_keyword, comp_data, user_keywords)
                gap_opportunity['gap_type'] = 'semantic'
                semantic_gaps.append(gap_opportunity)
                
        return semantic_gaps
        
    def calculate_semantic_similarity(self, keyword1: str, keyword2: str) -> float:
        """
        Calculate semantic similarity between two keywords
        
        Args:
            keyword1: First keyword
            keyword2: Second keyword
            
        Returns:
            Similarity score (0-1)
        """
        # Simple word overlap similarity
        words1 = set(keyword1.lower().split())
        words2 = set(keyword2.lower().split())
        
        if not words1 or not words2:
            return 0
            
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        jaccard_similarity = intersection / union if union > 0 else 0
        
        # Boost similarity for partial matches
        partial_matches = 0
        for word1 in words1:
            for word2 in words2:
                if word1 in word2 or word2 in word1:
                    partial_matches += 1
                    
        partial_bonus = min(partial_matches * self.PARTIAL_MATCH_BONUS, self.MAX_PARTIAL_BONUS)
        
        return min(jaccard_similarity + partial_bonus, 1.0)
        
    def generate_content_strategy(self, missing_keywords: List[Dict], 
                                top_n: int = 20) -> Dict:
        """
        Generate comprehensive content strategy based on missing keywords
        
        Args:
            missing_keywords: List of missing keyword opportunities
            top_n: Number of top opportunities to focus on
            
        Returns:
            Dictionary with content strategy recommendations
        """
        if not missing_keywords:
            return {'message': 'No keyword opportunities found'}
            
        top_opportunities = missing_keywords[:top_n]
        
        # Group by priority
        priority_groups = defaultdict(list)
        for opportunity in top_opportunities:
            priority = opportunity['priority']
            priority_groups[priority].append(opportunity)
            
        # Group by keyword type
        type_groups = defaultdict(list)
        for opportunity in top_opportunities:
            keyword_type = opportunity['keyword_type']
            type_groups[keyword_type].append(opportunity)
            
        # Group by search intent
        intent_groups = defaultdict(list)
        for opportunity in top_opportunities:
            intent = opportunity['search_intent']
            intent_groups[intent].append(opportunity)
            
        strategy = {
            'total_opportunities': len(missing_keywords),
            'priority_breakdown': {
                'high_priority': len(priority_groups['high']),
                'medium_priority': len(priority_groups['medium']),
                'low_priority': len(priority_groups['low'])
            },
            'keyword_type_breakdown': dict(type_groups.keys()),
            'intent_breakdown': dict(intent_groups.keys()),
            'recommended_actions': self.generate_action_plan(priority_groups, type_groups, intent_groups),
            'quick_wins': [kw for kw in top_opportunities if kw['estimated_difficulty'] == 'low'][:5],
            'high_impact_targets': [kw for kw in top_opportunities if kw['priority'] == 'high'][:5]
        }
        
        return strategy
        
    def generate_action_plan(self, priority_groups: Dict, type_groups: Dict, 
                           intent_groups: Dict) -> List[str]:
        """
        Generate specific action plan based on keyword analysis
        
        Args:
            priority_groups: Keywords grouped by priority
            type_groups: Keywords grouped by type
            intent_groups: Keywords grouped by intent
            
        Returns:
            List of recommended actions
        """
        actions = []
        
        # Priority-based actions
        if 'high' in priority_groups and priority_groups['high']:
            actions.append(f"Immediately target {len(priority_groups['high'])} high-priority keywords")
            
        # Type-based actions
        if 'informational' in type_groups:
            actions.append(f"Create {len(type_groups['informational'])} educational blog posts or guides")
            
        if 'commercial' in type_groups:
            actions.append(f"Optimize {len(type_groups['commercial'])} product/service pages")
            
        if 'local' in type_groups:
            actions.append(f"Develop {len(type_groups['local'])} location-specific content pieces")
            
        # Intent-based actions
        if 'transactional' in intent_groups:
            actions.append(f"Create {len(intent_groups['transactional'])} conversion-focused landing pages")
            
        if 'informational' in intent_groups:
            actions.append(f"Develop {len(intent_groups['informational'])} educational resources")
            
        return actions