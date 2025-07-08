import unittest
from analyzer import KeywordAnalyzer

class TestKeywordAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = KeywordAnalyzer()
        
    def test_preprocess_text(self):
        text = "Hello! This is a <b>test</b> text with http://example.com and test@email.com"
        expected = "hello this is a test text with and"
        result = self.analyzer.preprocess_text(text, preserve_phrases=False)
        self.assertEqual(result, expected)
        
    def test_extract_keywords(self):
        text = "SEO optimization is important for digital marketing"
        keywords = self.analyzer.extract_keywords(text)
        self.assertIn("seo", keywords)
        self.assertIn("optimization", keywords)
        self.assertIn("digital", keywords)
        self.assertIn("marketing", keywords)
        
    def test_extract_phrases(self):
        text = "SEO optimization is important for digital marketing strategies"
        phrases = self.analyzer.extract_phrases(text)
        self.assertIn("seo optimization", phrases)
        self.assertIn("digital marketing", phrases)
        
    def test_analyze_text(self):
        text = """
        SEO optimization is crucial for digital marketing success.
        Digital marketing requires good SEO optimization practices.
        Marketing strategies should focus on SEO and digital presence.
        """
        results = self.analyzer.analyze_text(text, min_frequency=2)
        
        # Check that common phrases were found
        self.assertIn("seo optimization", results)
        self.assertIn("digital marketing", results)
        
        # Check frequency counts
        self.assertEqual(results["seo"]["frequency"], 3)
        self.assertEqual(results["digital"]["frequency"], 2)
        
    def test_calculate_importance_score(self):
        keyword = "test keyword"
        frequency = 5
        total_words = 100
        positions = [10, 30, 50, 70, 90]
        
        score = self.analyzer.calculate_importance_score(
            keyword, frequency, total_words, positions
        )
        
        # Score should be between 0 and 100
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        
if __name__ == '__main__':
    unittest.main()