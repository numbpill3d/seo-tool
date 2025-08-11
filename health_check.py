#!/usr/bin/env python3
"""
Health check script for SEO Analyzer
Validates system requirements and configuration
"""

import sys
import os
import importlib
import subprocess
from pathlib import Path


def check_python_version():
    """Check Python version compatibility"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False


def check_dependencies():
    """Check required dependencies"""
    print("\nChecking dependencies...")
    
    required_packages = [
        'requests', 'beautifulsoup4', 'nltk', 'pandas', 'numpy',
        'reportlab', 'openpyxl', 'pyyaml', 'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            # Handle package name differences
            import_name = package
            if package == 'beautifulsoup4':
                import_name = 'bs4'
            elif package == 'python-dotenv':
                import_name = 'dotenv'
            elif package == 'pyyaml':
                import_name = 'yaml'
                
            importlib.import_module(import_name)
            print(f"✓ {package} - OK")
        except ImportError:
            print(f"✗ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True


def check_nltk_data():
    """Check NLTK data availability"""
    print("\nChecking NLTK data...")
    
    try:
        import nltk
        
        required_data = [
            'punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger',
            'maxent_ne_chunker', 'words'
        ]
        
        missing_data = []
        
        for data_name in required_data:
            try:
                nltk.data.find(f'tokenizers/{data_name}')
                print(f"✓ {data_name} - OK")
            except LookupError:
                try:
                    nltk.data.find(f'corpora/{data_name}')
                    print(f"✓ {data_name} - OK")
                except LookupError:
                    try:
                        nltk.data.find(f'taggers/{data_name}')
                        print(f"✓ {data_name} - OK")
                    except LookupError:
                        try:
                            nltk.data.find(f'chunkers/{data_name}')
                            print(f"✓ {data_name} - OK")
                        except LookupError:
                            print(f"✗ {data_name} - Missing")
                            missing_data.append(data_name)
        
        if missing_data:
            print(f"\nMissing NLTK data: {', '.join(missing_data)}")
            print("Download with: python -c \"import nltk; nltk.download('all')\"")
            return False
        
        return True
        
    except ImportError:
        print("✗ NLTK not available")
        return False


def check_configuration():
    """Check configuration validity"""
    print("\nChecking configuration...")
    
    try:
        import config
        
        if config.validate_config():
            print("✓ Configuration - OK")
            return True
        else:
            print("✗ Configuration - Invalid")
            return False
            
    except ImportError:
        print("✗ Configuration module not found")
        return False
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def check_directories():
    """Check required directories"""
    print("\nChecking directories...")
    
    required_dirs = ['seo_reports', 'sessions', 'history', 'temp', 'cache', 'logs']
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✓ {dir_name}/ - OK")
        else:
            try:
                os.makedirs(dir_name, exist_ok=True)
                print(f"✓ {dir_name}/ - Created")
            except Exception as e:
                print(f"✗ {dir_name}/ - Cannot create: {e}")
                return False
    
    return True


def check_permissions():
    """Check file system permissions"""
    print("\nChecking permissions...")
    
    test_dirs = ['seo_reports', 'sessions', 'logs']
    
    for dir_name in test_dirs:
        test_file = os.path.join(dir_name, '.test_write')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"✓ {dir_name}/ - Writable")
        except Exception as e:
            print(f"✗ {dir_name}/ - Not writable: {e}")
            return False
    
    return True


def check_network():
    """Check network connectivity"""
    print("\nChecking network connectivity...")
    
    try:
        import requests
        
        # Test basic connectivity
        response = requests.get('https://httpbin.org/status/200', timeout=10)
        if response.status_code == 200:
            print("✓ Network connectivity - OK")
            return True
        else:
            print(f"✗ Network connectivity - HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Network connectivity - {e}")
        return False


def run_basic_tests():
    """Run basic functionality tests"""
    print("\nRunning basic tests...")
    
    try:
        # Test scraper initialization
        from scraper import GoogleScraper
        scraper = GoogleScraper()
        print("✓ Scraper initialization - OK")
        
        # Test analyzer initialization
        from analyzer import KeywordAnalyzer
        analyzer = KeywordAnalyzer()
        print("✓ Analyzer initialization - OK")
        
        # Test gap finder initialization
        from gap_finder import ContentGapFinder
        gap_finder = ContentGapFinder()
        print("✓ Gap finder initialization - OK")
        
        # Test exporter initialization
        from exporter import ResultExporter
        exporter = ResultExporter()
        print("✓ Exporter initialization - OK")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic tests failed: {e}")
        return False


def main():
    """Main health check function"""
    print("SEO Analyzer Health Check")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("NLTK Data", check_nltk_data),
        ("Configuration", check_configuration),
        ("Directories", check_directories),
        ("Permissions", check_permissions),
        ("Network", check_network),
        ("Basic Tests", run_basic_tests),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"✗ {check_name} - Error: {e}")
    
    print("\n" + "=" * 50)
    print(f"Health Check Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("✓ System is ready for production use!")
        return 0
    else:
        print("✗ System has issues that need to be resolved")
        return 1


if __name__ == '__main__':
    sys.exit(main())