from setuptools import setup, find_packages

setup(
    name="seo-analyzer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#") and not line.startswith("git+")
    ],
    entry_points={
        'console_scripts': [
            'seo-analyzer=main:main',
        ],
    },
    python_requires='>=3.8',
    author="Your Company Name",
    author_email="contact@example.com",
    description="SEO Rank & Content Gap Analyzer Pro",
    long_description=open("readme.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/seo-analyzer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)