from setuptools import setup
from scrapetube import __version__




with open('README.md', encoding='utf-8') as f:
    readme = f.read()

with open('requirements.txt', encoding='utf-8') as f:
    requirements = [r.strip() for r in f]

setup(
    name = 'scrapetube',
    version = __version__,
    packages = ['scrapetube'],
    include_package_data = True,
    url = 'https://github.com/dermasmid/scrapetube',
    license = 'MIT',
    long_description = readme,
    long_description_content_type = 'text/markdown',
    author = 'Cheskel Twersky',
    author_email = 'twerskycheskel@gmail.com',
    description = 'Scrape youtube without the official youtube api and without selenium.',
    keywords = 'youtube python channel videos search playlist list get',
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        'Documentation': 'https://scrapetube.readthedocs.io/en/latest/'
    },
    install_requires = requirements,
    python_requires = '>=3.6',
)
