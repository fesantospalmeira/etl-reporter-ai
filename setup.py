from setuptools import setup, find_packages

setup(
    name='etl_reporter_ai',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'loguru',
        'python-dotenv',
        'google-generativeai'
    ],
)