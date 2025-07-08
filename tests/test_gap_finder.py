import unittest
from gap_finder import ContentGapFinder

class TestContentGapFinder(unittest.TestCase):
    def setUp(self):
        self.gap_finder = ContentGapFinder()
        
        # Sample test data
        self.competitor_keywords = {
            "seo optimization": {
                "frequency": 10,
                "document_frequency": 5,
                "avg_importance": 80,
                "sources": [1, 2, 3, 4, 5]
            },
            "digital marketing": {
                "frequency": 8,
                "document_frequency": 4,
                "avg_importance": 75,
                "sources": [1, 2, 3, 4]
            },
            "content strategy": {
                "frequency": 6,
                "document_frequency": 3,
                "avg_importance": 70,
                "sources": [1, 2, 3]
            }
        }
        
        self.user_keywords = {
            "seo optimization": {
                "frequency": 5,
                "importance_score": 60
            },
            "digital marketing": {
                "frequency": 3,
                "importance_score": 55
            }
        }
        
    def test_find_missing_keywords(self):
        missing_keywords = self.gap_finder.find_missing_keywords(
            self.competitor_keywords,
            self.user_keywords
        )
        
        # Should find "content strategy" as missing
        self.assertEqual(len(missing_keywords), 1)
        self.assertEqual(missing_keywords[0]['keyword'], "content strategy")
        
    def test_analyze_keyword_opportunity(self):
        keyword = "content strategy"
        competitor_data = self.competitor_keywords[keyword]
        
        opportunity = self.gap_finder.analyze_keyword_opportunity(
            keyword,
            competitor_data,
            self.user_keywords
        )
        
        # Check opportunity data structure
        self.assertIn('keyword', opportunity)
        self.assertIn('opportunity_score', opportunity)
        self.assertIn('priority', opportunity)
        self.assertIn('competitor_frequency', opportunity)
        self.assertIn('found_in_sites', opportunity)
        
        # Check values
        self.assertEqual(opportunity['keyword'], keyword)
        self.assertEqual(opportunity['competitor_frequency'], 6)
        self.assertEqual(opportunity['found_in_sites'], 3)
        
    def test_calculate_opportunity_score(self):
        score = self.gap_finder.calculate_opportunity_score(
            frequency=10,
            document_frequency=5,
            avg_importance=80,
            keyword="test keyword",
            user_keywords=self.user_keywords
        )
        
        # Score should be between 0 and 100
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        
    def test_determine_priority(self):
        # Test high priority
        high_score = 80
        self.assertEqual(
            self.gap_finder.determine_priority(high_score),
            'high'
        )
        
        # Test medium priority
        medium_score = 60
        self.assertEqual(
            self.gap_finder.determine_priority(medium_score),
            'medium'
        )
        
        # Test low priority
        low_score = 30
        self.assertEqual(
            self.gap_finder.determine_priority(low_score),
            'low'
        )
        
    def test_classify_keyword_type(self):
        # Test commercial keyword
        commercial = "buy best products"
        self.assertEqual(
            self.gap_finder.classify_keyword_type(commercial),
            'commercial'
        )
        
        # Test informational keyword
        informational = "how to optimize seo"
        self.assertEqual(
            self.gap_finder.classify_keyword_type(informational),
            'informational'
        )
        
        # Test local keyword
        local = "services near me"
        self.assertEqual(
            self.gap_finder.classify_keyword_type(local),
            'local'
        )
        
    def test_classify_search_intent(self):
        # Test transactional intent
        transactional = "buy seo services"
        self.assertEqual(
            self.gap_finder.classify_search_intent(transactional),
            'transactional'
        )
        
        # Test informational intent
        informational = "what is seo"
        self.assertEqual(
            self.gap_finder.classify_search_intent(informational),
            'informational'
        )
        
        # Test navigational intent
        navigational = "login dashboard"
        self.assertEqual(
            self.gap_finder.classify_search_intent(navigational),
            'navigational'
        )
        
    def test_generate_keyword_recommendations(self):
        keyword = "content strategy"
        competitor_data = self.competitor_keywords[keyword]
        
        recommendations = self.gap_finder.generate_keyword_recommendations(
            keyword,
            competitor_data
        )
        
        # Should return a list of recommendations
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
    def test_find_related_user_keywords(self):
        keyword = "content optimization"
        related = self.gap_finder.find_related_user_keywords(
            keyword,
            self.user_keywords
        )
        
        # Should find "seo optimization" as related
        self.assertIsInstance(related, list)
        self.assertIn("seo optimization", related)
        
    def test_calculate_semantic_similarity(self):
        # Test exact match
        similarity = self.gap_finder.calculate_semantic_similarity(
            "seo optimization",
            "seo optimization"
        )
        self.assertEqual(similarity, 1.0)
        
        # Test partial match
        similarity = self.gap_finder.calculate_semantic_similarity(
            "seo optimization",
            "seo strategy"
        )
        self.assertGreater(similarity, 0)
        self.assertLess(similarity, 1)
        
        # Test no match
        similarity = self.gap_finder.calculate_semantic_similarity(
            "seo optimization",
            "social media"
        )
        self.assertEqual(similarity, 0)
        
if __name__ == '__main__':
    unittest.main()