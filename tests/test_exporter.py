import unittest
import os
import json
import csv
from exporter import ResultExporter

class TestResultExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = ResultExporter()
        
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
            }
        }
        
        self.missing_keywords = [
            {
                "keyword": "content strategy",
                "opportunity_score": 85,
                "priority": "high",
                "competitor_frequency": 6,
                "found_in_sites": 3,
                "keyword_type": "informational",
                "search_intent": "informational",
                "estimated_difficulty": "medium",
                "word_count": 2,
                "recommendations": ["Create comprehensive guide"]
            }
        ]
        
        self.metadata = {
            "keyword": "test keyword",
            "location": "test location",
            "analysis_date": "2025-01-01"
        }
        
        # Create test directory
        os.makedirs("test_output", exist_ok=True)
        
    def tearDown(self):
        # Clean up test files
        test_files = [
            "test_output/test.csv",
            "test_output/test.json",
            "test_output/test.pdf"
        ]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
        
        # Remove test directory
        if os.path.exists("test_output"):
            os.rmdir("test_output")
            
    def test_export_to_csv(self):
        filename = "test_output/test.csv"
        result = self.exporter.export_to_csv(
            filename,
            self.competitor_keywords,
            self.missing_keywords,
            self.metadata
        )
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(filename))
        
        # Verify CSV content
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            
            # Check header row exists
            self.assertGreater(len(rows), 0)
            
            # Check metadata is included
            self.assertIn(self.metadata['keyword'], rows[1][1])
            
    def test_export_to_json(self):
        filename = "test_output/test.json"
        result = self.exporter.export_to_json(
            filename,
            self.competitor_keywords,
            self.missing_keywords,
            self.metadata
        )
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(filename))
        
        # Verify JSON content
        with open(filename, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            
            self.assertIn('metadata', data)
            self.assertIn('competitor_keywords', data)
            self.assertIn('missing_keywords', data)
            self.assertIn('summary_statistics', data)
            
    def test_export_to_pdf(self):
        if not self.exporter.reportlab_available:
            self.skipTest("ReportLab not available")
            
        filename = "test_output/test.pdf"
        result = self.exporter.export_to_pdf(
            filename,
            self.competitor_keywords,
            self.missing_keywords,
            self.metadata
        )
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(filename))
        
    def test_create_batch_export(self):
        base_filename = "test_output/test"
        formats = ['csv', 'json']
        
        results = self.exporter.create_batch_export(
            base_filename,
            self.competitor_keywords,
            self.missing_keywords,
            self.metadata,
            formats
        )
        
        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), len(formats))
        
        for format_type in formats:
            self.assertTrue(results[format_type])
            self.assertTrue(os.path.exists(f"{base_filename}.{format_type}"))
            
    def test_generate_summary_stats(self):
        stats = self.exporter._generate_summary_stats(
            self.competitor_keywords,
            self.missing_keywords
        )
        
        self.assertIn('competitor_analysis', stats)
        self.assertIn('opportunity_analysis', stats)
        
        # Check competitor analysis stats
        comp_stats = stats['competitor_analysis']
        self.assertEqual(comp_stats['total_keywords'], len(self.competitor_keywords))
        self.assertGreater(comp_stats['avg_frequency'], 0)
        self.assertIsInstance(comp_stats['top_keywords'], list)
        
        # Check opportunity analysis stats
        opp_stats = stats['opportunity_analysis']
        self.assertEqual(opp_stats['total_opportunities'], len(self.missing_keywords))
        self.assertGreaterEqual(opp_stats['high_priority'], 0)
        
if __name__ == '__main__':
    unittest.main()