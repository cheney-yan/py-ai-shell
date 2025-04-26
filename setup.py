from setuptools import setup, find_packages

setup(
    name="ai-shell",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "click>=8.0.0",
        "rich>=10.0.0",
        "pydantic>=2.0.0",
        "pyperclip>=1.8.0",
    ],
    entry_points={
        "console_scripts": [
            "ai=ai_shell.cli:main",
            "ai-shell=ai_shell.cli:main",
        ],
    },
    author="AI Shell Team",
    author_email="example@example.com",
    description="AI-powered shell assistant",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai-shell",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
