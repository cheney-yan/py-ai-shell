from setuptools import setup, find_packages

# Read version from __init__.py
with open('ai_shell/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"\'')
            break

setup(
    name="py-ai-shell",
    version=version,
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "click>=8.0.0",
        "rich>=10.0.0",
        "pydantic>=2.0.0",
        "pyperclip>=1.8.0",
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'flake8>=6.0.0',
            'tox>=4.0.0',
            'twine>=4.0.0',
            'wheel>=0.40.0',
            'build>=0.10.0',
            'watchdog'
        ],
    },
    entry_points={
        "console_scripts": [
            "ai=ai_shell.cli:main",
            "ai-shell=ai_shell.cli:main",
        ],
    },
    author="Cheney Yan",
    author_email="cheney.yan@example.com",
    description="AI-powered shell assistant",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cheney-yan/py-ai-shell",
    project_urls={
        "Bug Tracker": "https://github.com/cheney-yan/py-ai-shell/issues",
        "Documentation": "https://github.com/cheney-yan/py-ai-shell",
        "Source Code": "https://github.com/cheney-yan/py-ai-shell",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
