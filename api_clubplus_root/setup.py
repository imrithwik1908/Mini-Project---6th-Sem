from setuptools import setup, find_packages

setup(
    name='api_clubplus',
    version='0.1.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'Flask',
        'requests',
        'python-dotenv'
    ],
    entry_points='''
        [console_scripts]
        strava_api=strava_api_clubplus.api:main
    ''',
    author='Club+',
    author_email='reddyrithwik23@gmail.com',
    description='A Python package for interacting with the Strava API',
    url='https://github.com/imrithwik1908/Mini-Project---6th-Sem/tree/main',
)
