# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages

setup(
    name         = 'ironman',
    version      = '1.3',
    packages     = find_packages(),
    package_data ={
        'ironman': ['resources/GoogleAPISecret.json']
    },
    include_package_data=True,
    entry_points = {'scrapy': ['settings = ironman.settings']},
)
