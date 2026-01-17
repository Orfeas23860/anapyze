from setuptools import setup, find_packages

# Load requirements.txt
with open('requirements.txt', encoding='utf-8') as f:
    requirements = f.read().splitlines()

# Load README.md for long_description
try:
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ''

setup(
    name='anapyze',
    version='0.2.0',
    author='Jesus Silva',
    author_email='jesus.bubuchis@gmail.com',
    description='A bunch of functions to analyze Nifti data in Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Fundacion-CIEN/anapyze',
    package_dir={'': 'src'},
    packages=find_packages(
        where='src',
        exclude=['resources', 'examples', '__MACOSX']
    ),
    install_requires=requirements,
    include_package_data=False,  # set to True if you add data files via MANIFEST.in
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)