"""
Centralized dependency management for SEO Analyzer
Handles optional dependencies with graceful fallbacks
"""

import logging
import sys
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DependencyType(Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    DEVELOPMENT = "development"


@dataclass
class Dependency:
    name: str
    import_name: str
    version_min: Optional[str] = None
    dependency_type: DependencyType = DependencyType.REQUIRED
    fallback_available: bool = False
    description: str = ""
    install_command: str = ""


class DependencyManager:
    """
    Manages application dependencies with graceful fallbacks
    """
    
    def __init__(self):
        self.dependencies = self._define_dependencies()
        self.availability = {}
        self.missing_required = []
        self.missing_optional = []
        self._check_all_dependencies()
    
    def _define_dependencies(self) -> List[Dependency]:
        """Define all application dependencies"""
        return [
            # Core required dependencies
            Dependency(
                name="requests",
                import_name="requests",
                version_min="2.28.0",
                dependency_type=DependencyType.REQUIRED,
                description="HTTP library for web scraping",
                install_command="pip install requests"
            ),
            Dependency(
                name="beautifulsoup4",
                import_name="bs4",
                version_min="4.11.0",
                dependency_type=DependencyType.REQUIRED,
                description="HTML/XML parsing library",
                install_command="pip install beautifulsoup4"
            ),
            Dependency(
                name="lxml",
                import_name="lxml",
                version_min="4.9.0",
                dependency_type=DependencyType.REQUIRED,
                description="XML/HTML parser for BeautifulSoup",
                install_command="pip install lxml"
            ),
            Dependency(
                name="nltk",
                import_name="nltk",
                version_min="3.8",
                dependency_type=DependencyType.REQUIRED,
                description="Natural language processing toolkit",
                install_command="pip install nltk"
            ),
            
            # Optional dependencies with fallbacks
            Dependency(
                name="pandas",
                import_name="pandas",
                version_min="1.5.0",
                dependency_type=DependencyType.OPTIONAL,
                fallback_available=True,
                description="Data analysis library for enhanced exports",
                install_command="pip install pandas"
            ),
            Dependency(
                name="numpy",
                import_name="numpy",
                version_min="1.21.0",
                dependency_type=DependencyType.OPTIONAL,
                fallback_available=True,
                description="Numerical computing library",
                install_command="pip install numpy"
            ),
            Dependency(
                name="reportlab",
                import_name="reportlab",
                version_min="4.0.0",
                dependency_type=DependencyType.OPTIONAL,
                fallback_available=True,
                description="PDF generation library",
                install_command="pip install reportlab"
            ),
            Dependency(
                name="openpyxl",
                import_name="openpyxl",
                version_min="3.0.0",
                dependency_type=DependencyType.OPTIONAL,
                fallback_available=True,
                description="Excel file support",
                install_command="pip install openpyxl"
            ),
            Dependency(
                name="python-dotenv",
                import_name="dotenv",
                version_min="0.19.0",
                dependency_type=DependencyType.OPTIONAL,
                fallback_available=True,
                description="Environment variable management",
                install_command="pip install python-dotenv"
            ),
            
            # Premium API integrations (optional)
            Dependency(
                name="google-search-results",
                import_name="serpapi",
                version_min="2.4.0",
                dependency_type=DependencyType.OPTIONAL,
                fallback_available=True,
                description="SerpAPI integration for enhanced search",
                install_command="pip install google-search-results"
            ),
            
            # Development dependencies
            Dependency(
                name="pytest",
                import_name="pytest",
                version_min="7.0.0",
                dependency_type=DependencyType.DEVELOPMENT,
                fallback_available=False,
                description="Testing framework",
                install_command="pip install pytest"
            ),
            Dependency(
                name="pytest-cov",
                import_name="pytest_cov",
                dependency_type=DependencyType.DEVELOPMENT,
                fallback_available=False,
                description="Test coverage reporting",
                install_command="pip install pytest-cov"
            ),
        ]
    
    def _check_all_dependencies(self):
        """Check availability of all dependencies"""
        for dep in self.dependencies:
            is_available, version = self._check_dependency(dep)
            self.availability[dep.name] = {
                'available': is_available,
                'version': version,
                'dependency': dep
            }
            
            if not is_available:
                if dep.dependency_type == DependencyType.REQUIRED:
                    self.missing_required.append(dep)
                elif dep.dependency_type == DependencyType.OPTIONAL:
                    self.missing_optional.append(dep)
    
    def _check_dependency(self, dep: Dependency) -> Tuple[bool, Optional[str]]:
        """Check if a single dependency is available"""
        try:
            module = __import__(dep.import_name)
            version = getattr(module, '__version__', 'unknown')
            logger.debug(f"✓ {dep.name} {version} - Available")
            return True, version
        except ImportError as e:
            logger.debug(f"✗ {dep.name} - Missing: {str(e)}")
            return False, None
        except Exception as e:
            logger.warning(f"? {dep.name} - Error checking: {str(e)}")
            return False, None
    
    def is_available(self, package_name: str) -> bool:
        """Check if a specific package is available"""
        return self.availability.get(package_name, {}).get('available', False)
    
    def get_version(self, package_name: str) -> Optional[str]:
        """Get version of a specific package"""
        return self.availability.get(package_name, {}).get('version')
    
    def get_missing_required(self) -> List[Dependency]:
        """Get list of missing required dependencies"""
        return self.missing_required
    
    def get_missing_optional(self) -> List[Dependency]:
        """Get list of missing optional dependencies"""
        return self.missing_optional
    
    def validate_requirements(self) -> bool:
        """Validate that all required dependencies are available"""
        if self.missing_required:
            logger.error("Missing required dependencies:")
            for dep in self.missing_required:
                logger.error(f"  - {dep.name}: {dep.description}")
                logger.error(f"    Install with: {dep.install_command}")
            return False
        
        if self.missing_optional:
            logger.warning("Missing optional dependencies (some features may be disabled):")
            for dep in self.missing_optional:
                logger.warning(f"  - {dep.name}: {dep.description}")
                logger.warning(f"    Install with: {dep.install_command}")
        
        return True
    
    def get_dependency_report(self) -> str:
        """Generate a comprehensive dependency report"""
        report = ["SEO Analyzer Dependency Report", "=" * 40, ""]
        
        # Required dependencies
        report.append("REQUIRED DEPENDENCIES:")
        for dep in self.dependencies:
            if dep.dependency_type == DependencyType.REQUIRED:
                info = self.availability[dep.name]
                status = "✓ Available" if info['available'] else "✗ Missing"
                version = f" ({info['version']})" if info['version'] else ""
                report.append(f"  {dep.name}{version}: {status}")
        
        report.append("")
        
        # Optional dependencies
        report.append("OPTIONAL DEPENDENCIES:")
        for dep in self.dependencies:
            if dep.dependency_type == DependencyType.OPTIONAL:
                info = self.availability[dep.name]
                status = "✓ Available" if info['available'] else "✗ Missing"
                version = f" ({info['version']})" if info['version'] else ""
                fallback = " (fallback available)" if dep.fallback_available else ""
                report.append(f"  {dep.name}{version}: {status}{fallback}")
        
        report.append("")
        
        # Installation commands for missing packages
        missing = self.missing_required + self.missing_optional
        if missing:
            report.append("INSTALLATION COMMANDS:")
            for dep in missing:
                report.append(f"  {dep.install_command}")
        
        return "\n".join(report)
    
    def safe_import(self, package_name: str, fallback_value: Any = None):
        """Safely import a package with fallback"""
        if self.is_available(package_name):
            dep = next((d for d in self.dependencies if d.name == package_name), None)
            if dep:
                try:
                    return __import__(dep.import_name)
                except ImportError:
                    pass
        
        logger.debug(f"Using fallback for {package_name}")
        return fallback_value
    
    def require_dependency(self, package_name: str):
        """Require a dependency or raise informative error"""
        if not self.is_available(package_name):
            dep = next((d for d in self.dependencies if d.name == package_name), None)
            if dep:
                raise ImportError(
                    f"Required dependency '{package_name}' is not available.\n"
                    f"Description: {dep.description}\n"
                    f"Install with: {dep.install_command}"
                )
            else:
                raise ImportError(f"Unknown dependency: {package_name}")
        
        dep = next((d for d in self.dependencies if d.name == package_name), None)
        return __import__(dep.import_name)


# Global dependency manager instance
dependency_manager = DependencyManager()


# Convenience functions
def is_available(package_name: str) -> bool:
    """Check if package is available"""
    return dependency_manager.is_available(package_name)


def safe_import(package_name: str, fallback_value: Any = None):
    """Safely import package with fallback"""
    return dependency_manager.safe_import(package_name, fallback_value)


def require_dependency(package_name: str):
    """Require dependency or raise error"""
    return dependency_manager.require_dependency(package_name)


def validate_environment() -> bool:
    """Validate the current environment"""
    return dependency_manager.validate_requirements()


def get_dependency_report() -> str:
    """Get dependency report"""
    return dependency_manager.get_dependency_report()


if __name__ == "__main__":
    print(get_dependency_report())
    if not validate_environment():
        sys.exit(1)
    print("\n✓ Environment validation passed!")