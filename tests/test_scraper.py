import unittest
from unittest.mock import patch, MagicMock
from scraper import GoogleScraper
from bs4 import BeautifulSoup

class TestGoogleScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = GoogleScraper()
        
    def test_clean_google_url(self):
        test_url = "/url?q=https://example.com&sa=U&ved=123"
        expected = "https://example.com"
        result = self.scraper.clean_google_url(test_url)
        self.assertEqual(result, expected)
        
    def test_extract_domain_from_url(self):
        test_url = "https://example.com/path/page.html"
        expected = "example.com"
        result = self.scraper.extract_domain_from_url(test_url)
        self.assertEqual(result, expected)
        
    @patch('requests.Session.get')
    def test_extract_content_from_url(self, mock_get):
        # Mock response with test HTML
        mock_response = MagicMock()
        mock_response.content = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <script>alert('test');</script>
                <div>Test content</div>
                <nav>Navigation</nav>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        result = self.scraper.extract_content_from_url("https://example.com")
        self.assertIn("Test content", result)
        self.assertNotIn("alert('test')", result)
        self.assertNotIn("Navigation", result)
        
    def test_clean_extracted_text(self):
        text = "  Test   content  with  extra   spaces  and special @#$ characters  "
        expected = "Test content with extra spaces and special characters"
        result = self.scraper.clean_extracted_text(text)
        self.assertEqual(result, expected)
        
    @patch('requests.Session.get')
    def test_get_page_metadata(self, mock_get):
        # Mock response with test HTML containing metadata
        mock_response = MagicMock()
        mock_response.content = """
        <html>
            <head>
                <title>Test Title</title>
                <meta name="description" content="Test description">
                <meta name="keywords" content="test, keywords">
            </head>
            <body>
                <h1>Test H1</h1>
                <h2>Test H2</h2>
                <h3>Test H3</h3>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        metadata = self.scraper.get_page_metadata("https://example.com")
        
        self.assertEqual(metadata['title'], "Test Title")
        self.assertEqual(metadata['description'], "Test description")
        self.assertEqual(metadata['keywords'], "test, keywords")
        self.assertEqual(metadata['h1_tags'], ["Test H1"])
        self.assertEqual(metadata['h2_tags'], ["Test H2"])
        self.assertEqual(metadata['h3_tags'], ["Test H3"])
        
    @patch('requests.Session.get')
    def test_scrape_google_results(self, mock_get):
        # Mock response with test Google search results
        mock_response = MagicMock()
        mock_response.content = """
        <html>
            <div class="g">
                <h3><a href="/url?q=https://example1.com">Result 1</a></h3>
                <span data-ved="true">Description 1</span>
            </div>
            <div class="g">
                <h3><a href="/url?q=https://example2.com">Result 2</a></h3>
                <span data-ved="true">Description 2</span>
            </div>
        </html>
        """
        mock_get.return_value = mock_response
        
        results = self.scraper.scrape_google_results("test query", num_results=2)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['url'], "https://example1.com")
        self.assertEqual(results[1]['url'], "https://example2.com")
        
    def test_wait_for_rate_limit(self):
        # Test that rate limiting adds delay between requests
        import time
        
        start_time = time.time()
        
        # Make multiple requests that should trigger rate limiting
        for _ in range(5):
            self.scraper.wait_for_rate_limit()
            
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Should have some delay due to rate limiting
        self.assertGreater(elapsed_time, 0)
        
if __name__ == '__main__':
    unittest.main()