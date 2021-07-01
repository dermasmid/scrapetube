from setuptools import setup
from list_youtube_channel import __version__




with open('README.md', encoding='utf-8') as f:
    readme = f.read()

with open('requirements.txt', encoding='utf-8') as f:
    requirements = [r.strip() for r in f]

setup(
    name = 'list_youtube_channel',
    version = __version__,
    packages = ['list_youtube_channel'],
    include_package_data = True,
    url = 'https://github.com/dermasmid/list_youtube_channel',
    license = 'MIT',
    long_description = readme,
    long_description_content_type = 'text/markdown',
    author = 'Cheskel Twersky',
    author_email = 'twerskycheskel@gmail.com',
    description = 'Get all videos for a Youtube channel',
    keywords = 'youtube python channel videos list get',
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = requirements,
    python_requires = '>=3.6',
)
