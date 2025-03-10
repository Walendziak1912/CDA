from setuptools import setup, find_packages # type: ignore

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="cda-premium-downloader",
    version="1.0.0",
    author="Twoje Imię",
    author_email="twoj.email@przyklad.com",
    description="Program do pobierania filmów z CDA Premium",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/twoja-nazwa-uzytkownika/cda-premium-downloader",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "cda-downloader=src.main:main",
        ],
    },
)