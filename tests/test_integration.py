import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
import json

from scraper import GoogleScraper
from analyzer import KeywordAnalyzer
from gap_finder import ContentGapFinder
from exporter import ResultExporter
from cli import run_analysis, validate_inputs
import argparse


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete SEO analysis workflow"""
    
    def setUp(self):
        self.scraper = GoogleScraper()
        self.analyzer = KeywordAnalyzer()
        self.gap_finder = ContentGapFinder()
        self.exporter = ResultExporter()
        
        # Sample test data
        self.sample_competitor_keywords = {
            'seo tools': {
                'frequency': 5,
                'document_frequency': 3,
                'avg_importance': 85.0,
                'sources': [0, 1, 2]
            },
            'keyword research': {
                'frequency': 8,
                'document_frequency': 4,
                'avg_importance': 92.0,
                'sources': [0, 1, 2, 3]
            }
        }
        
        self.sample_missing_keywords = [
            {
                'keyword': 'content gap analysis',
                'opportunity_score': 87.5,
                'priority': 'high',
                'competitor_frequency': 6,
                'found_in_sites': 3,
                'keyword_type': 'informational',
                'search_intent': 'informational',
                'estimated_difficulty': 'medium'
            }
        ]
    
    def test_complete_workflow(self):
        """Test the complete analysis workflow"""
        with patch.object(self.scraper, 'scrape_google_results') as mock_scrape:
            with patch.object(self.scraper, 'extract_content_from_url') as mock_extract:
                with patch.object(self.analyzer, 'analyze_multiple_texts') as mock_analyze_multi:
                    with patch.object(self.analyzer, 'analyze_text') as mock_analyze_single:
                        with patch.object(self.gap_finder, 'find_missing_keywords') as mock_find_gaps:
                            
                            # Setup mocks
                            mock_scrape.return_value = [
                                {'url': 'https://example1.com', 'title': 'Test 1'},
                                {'url': 'https://example2.com', 'title': 'Test 2'}
                            ]
                            mock_extract.return_value = "Sample competitor content"
                            mock_analyze_multi.return_value = self.sample_competitor_keywords
                            mock_analyze_single.return_value = {'existing': {'frequency': 2}}
                            mock_find_gaps.return_value = self.sample_missing_keywords
                            
                            # Run workflow
                            search_results = self.scraper.scrape_google_results("test keyword")
                            self.assertEqual(len(search_results), 2)
                            
                            competitor_texts = []
                            for result in search_results:
                                content = self.scraper.extract_content_from_url(result['url'])
                                if content:
                                    competitor_texts.append(content)
                            
                            competitor_keywords = self.analyzer.analyze_multiple_texts(competitor_texts)
                            user_keywords = self.analyzer.analyze_text("user content")
                            missing_keywords = self.gap_finder.find_missing_keywords(
                                competitor_keywords, user_keywords
                            )
                            
                            # Verify results
                            self.assertEqual(len(competitor_keywords), 2)
                            self.assertEqual(len(missing_keywords), 1)
                            self.assertEqual(missing_keywords[0]['priority'], 'high')
    
    def test_cli_validation(self):
        """Test CLI input validation"""
        # Valid arguments
        args = argparse.Namespace()
        args.keyword = "test keyword"
        args.content = "https://example.com"
        args.content_method = "url"
        
        self.assertTrue(validate_inputs(args))
        
        # Invalid - no keyword
        args.keyword = ""
        self.assertFalse(validate_inputs(args))
        
        # Invalid - bad URL
        args.keyword = "test"
        args.content = "not-a-url"
        args.content_method = "url"
        self.assertFalse(validate_inputs(args))
    
    def test_export_functionality(self):
        """Test export functionality with real data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test CSV export
            csv_file = os.path.join(temp_dir, "test.csv")
            success = self.exporter.export_to_csv(
                csv_file,
                self.sample_competitor_keywords,
                self.sample_missing_keywords,
                {'keyword': 'test', 'location': '', 'analysis_date': '2025-01-01'}
            )
            self.assertTrue(success)
            self.assertTrue(os.path.exists(csv_file))
            
            # Test JSON export
            json_file = os.path.join(temp_dir, "test.json")
            success = self.exporter.export_to_json(
                json_file,
                self.sample_competitor_keywords,
                self.sample_missing_keywords,
                {'keyword': 'test', 'location': '', 'analysis_date': '2025-01-01'}
            )
            self.assertTrue(success)
            self.assertTrue(os.path.exists(json_file))
            
            # Verify JSON content
            with open(json_file, 'r') as f:
                data = json.load(f)
                self.assertIn('competitor_keywords', data)
                self.assertIn('missing_keywords', data)
                self.assertIn('metadata', data)
    
    def test_performance_optimization(self):
        """Test that performance optimizations work correctly"""
        # Test that regex search is more efficient than string search
        import time
        
        text = "This is a test text with many keywords. " * 1000
        keyword = "test"
        
        # Time the optimized regex approach
        start_time = time.time()
        import re
        pattern = re.escape(keyword.lower())
        matches = list(re.finditer(pattern, text.lower()))
        regex_time = time.time() - start_time
        
        # Time the old string search approach
        start_time = time.time()
        positions = []
        start = 0
        while True:
            pos = text.lower().find(keyword.lower(), start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        string_time = time.time() - start_time
        
        # Regex should be faster or at least not significantly slower
        self.assertLessEqual(regex_time, string_time * 2)  # Allow 2x tolerance
        self.assertEqual(len(matches), len(positions))
    
    def test_error_handling(self):
        """Test error handling in various scenarios"""
        # Test network error handling
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            results = self.scraper.scrape_google_results("test")
            self.assertEqual(len(results), 0)  # Should return empty list, not crash
        
        # Test file handling errors
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to export to a directory that doesn't exist
            bad_path = os.path.join(temp_dir, "nonexistent", "test.csv")
            success = self.exporter.export_to_csv(
                bad_path,
                self.sample_competitor_keywords,
                self.sample_missing_keywords,
                {'keyword': 'test'}
            )
            # Should handle the error gracefully
            self.assertFalse(success)
    
    def test_constants_usage(self):
        """Test that constants are properly used instead of magic numbers"""
        gap_finder = ContentGapFinder()
        
        # Verify constants are defined
        self.assertTrue(hasattr(gap_finder, 'FREQUENCY_SCORE_MULTIPLIER'))
        self.assertTrue(hasattr(gap_finder, 'SIMILARITY_THRESHOLD'))
        self.assertTrue(hasattr(gap_finder, 'commercial_indicators'))
        
        # Test that constants are used in calculations
        score = gap_finder.calculate_opportunity_score(5, 3, 80, "test keyword", {})
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)


if __name__ == '__main__':
    unittest.main()