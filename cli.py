#!/usr/bin/env python3
"""
Command Line Interface for SEO Content Gap Analyzer
"""

import argparse
import sys
import os
import json
from datetime import datetime
from pathlib import Path

from scraper import GoogleScraper
from analyzer import KeywordAnalyzer
from gap_finder import ContentGapFinder
from exporter import ResultExporter


def validate_inputs(args):
    """Validate command line arguments"""
    if not args.keyword:
        print("Error: Target keyword is required")
        return False
    
    if args.content_method == 'file' and not os.path.exists(args.content):
        print(f"Error: Content file '{args.content}' not found")
        return False
    
    if args.content_method == 'url' and not args.content.startswith(('http://', 'https://')):
        print("Error: URL must start with http:// or https://")
        return False
    
    return True


def get_user_content(content_method, content_input):
    """Get user content based on method"""
    if content_method == 'url':
        scraper = GoogleScraper()
        return scraper.extract_content_from_url(content_input)
    elif content_method == 'text':
        return content_input
    elif content_method == 'file':
        try:
            with open(content_input, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    return None


def run_analysis(args):
    """Run SEO analysis with given arguments"""
    print(f"Starting SEO analysis for keyword: {args.keyword}")
    
    # Initialize components
    scraper = GoogleScraper()
    analyzer = KeywordAnalyzer()
    gap_finder = ContentGapFinder()
    exporter = ResultExporter()
    
    try:
        # Step 1: Scrape search results
        print("Scraping Google search results...")
        search_query = f"{args.keyword} {args.location}" if args.location else args.keyword
        search_results = scraper.scrape_google_results(search_query, args.results_count)
        
        if not search_results:
            print("No search results found")
            return False
        
        print(f"Found {len(search_results)} search results")
        
        # Step 2: Extract competitor content
        print("Extracting competitor content...")
        competitor_texts = []
        for i, result in enumerate(search_results):
            print(f"Processing competitor {i+1}/{len(search_results)}")
            content = scraper.extract_content_from_url(result['url'])
            if content:
                competitor_texts.append(content)
        
        # Step 3: Analyze competitor keywords
        print("Analyzing competitor keywords...")
        competitor_keywords = analyzer.analyze_multiple_texts(
            competitor_texts,
            min_frequency=args.min_frequency,
            exclude_common_words=True
        )
        
        # Step 4: Analyze user content
        print("Analyzing user content...")
        user_content = get_user_content(args.content_method, args.content)
        user_keywords = {}
        if user_content:
            user_keywords = analyzer.analyze_text(
                user_content,
                min_frequency=1,
                exclude_common_words=True
            )
        
        # Step 5: Find content gaps
        print("Identifying content gaps...")
        missing_keywords = gap_finder.find_missing_keywords(
            competitor_keywords,
            user_keywords
        )
        
        # Step 6: Export results
        print("Exporting results...")
        metadata = {
            'keyword': args.keyword,
            'location': args.location or '',
            'analysis_date': datetime.now().isoformat(),
            'results_count': args.results_count
        }
        
        # Determine output filename
        if args.output:
            base_filename = args.output
        else:
            safe_keyword = "".join(c for c in args.keyword if c.isalnum() or c in (' ', '-', '_')).rstrip()
            base_filename = f"seo_analysis_{safe_keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Export in requested formats
        success_count = 0
        for format_type in args.output_format:
            filename = f"{base_filename}.{format_type}"
            
            if format_type == 'csv':
                success = exporter.export_to_csv(filename, competitor_keywords, missing_keywords, metadata)
            elif format_type == 'json':
                success = exporter.export_to_json(filename, competitor_keywords, missing_keywords, metadata)
            elif format_type == 'pdf':
                success = exporter.export_to_pdf(filename, competitor_keywords, missing_keywords, metadata)
            else:
                print(f"Unsupported format: {format_type}")
                continue
            
            if success:
                print(f"Results exported to {filename}")
                success_count += 1
            else:
                print(f"Failed to export to {filename}")
        
        # Print summary
        print(f"\nAnalysis Summary:")
        print(f"- Competitor keywords found: {len(competitor_keywords)}")
        print(f"- Missing keywords identified: {len(missing_keywords)}")
        
        if missing_keywords:
            high_priority = len([k for k in missing_keywords if k['priority'] == 'high'])
            print(f"- High priority opportunities: {high_priority}")
        
        print(f"- Files exported: {success_count}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        return False


def batch_analysis(args):
    """Run batch analysis from CSV file"""
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        return False
    
    try:
        import csv
        with open(args.input, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                print(f"\nProcessing batch item {i+1}: {row.get('keyword', 'Unknown')}")
                
                # Create args object for this row
                batch_args = argparse.Namespace()
                batch_args.keyword = row.get('keyword', '')
                batch_args.location = row.get('location', '')
                batch_args.content = row.get('content', '')
                batch_args.content_method = row.get('content_method', 'url')
                batch_args.results_count = int(row.get('results_count', 10))
                batch_args.min_frequency = int(row.get('min_frequency', 2))
                batch_args.output_format = ['csv', 'json']
                batch_args.output = None
                
                if not batch_args.keyword:
                    print(f"Skipping row {i+1}: No keyword specified")
                    continue
                
                success = run_analysis(batch_args)
                if not success:
                    print(f"Failed to analyze: {batch_args.keyword}")
        
        return True
        
    except Exception as e:
        print(f"Batch analysis failed: {e}")
        return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="SEO Content Gap Analyzer - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze --keyword "digital marketing" --url "https://example.com"
  %(prog)s analyze --keyword "seo tools" --location "New York" --text "Your content here"
  %(prog)s batch --input keywords.csv --output results/
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run SEO analysis')
    analyze_parser.add_argument('--keyword', required=True, help='Target keyword to analyze')
    analyze_parser.add_argument('--location', help='Location for local SEO analysis')
    analyze_parser.add_argument('--content', required=True, help='Your content (URL, text, or file path)')
    analyze_parser.add_argument('--content-method', choices=['url', 'text', 'file'], 
                               default='url', help='Content input method')
    analyze_parser.add_argument('--results-count', type=int, default=10, 
                               help='Number of search results to analyze')
    analyze_parser.add_argument('--min-frequency', type=int, default=2,
                               help='Minimum keyword frequency threshold')
    analyze_parser.add_argument('--output-format', nargs='+', 
                               choices=['csv', 'json', 'pdf'], default=['csv'],
                               help='Output format(s)')
    analyze_parser.add_argument('--output', help='Output filename (without extension)')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Run batch analysis')
    batch_parser.add_argument('--input', required=True, help='Input CSV file with analysis parameters')
    batch_parser.add_argument('--output', help='Output directory for results')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'analyze':
        if not validate_inputs(args):
            return 1
        success = run_analysis(args)
        return 0 if success else 1
    
    elif args.command == 'batch':
        success = batch_analysis(args)
        return 0 if success else 1
    
    return 1


if __name__ == '__main__':
    sys.exit(main())