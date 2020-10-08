from setuptools import setup, find_packages
 
__version__ = '0.0.1'

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.readlines()
    
PROJECT_URLS = {
    "Bug Tracker": "https://github.com/DougTrajano/anallyticabot/issues",
    "Documentation": "https://github.com/DougTrajano/anallyticabot/tree/master/documentation",
    "Source Code": "https://github.com/DougTrajano/anallyticabot",
}

CLASSIFIERS = [
    "Development Status :: 2 - Pre-Alpha",
    "Operating System :: OS Independent",
    "Intended Audience :: Customer Service",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Cython",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Scientific/Engineering :: Human Machine Interfaces",
    "Topic :: Scientific/Engineering :: Information Analysis"
]

setup(name='anallyticabot',
      version=__version__,
      url='https://github.com/DougTrajano/anallyticabot',
      license='GPL',
      author='Douglas Trajano',
      author_email='douglas.trajano@outlook.com',
      description='A package with analytical tools to improve chatbots.',
      packages=find_packages("anallyticabot"),
      long_description=open('README.md', encoding='utf-8').read(),
      long_description_content_type='text/markdown',
      tests_require=['pytest'],
      zip_safe=False,
      install_requires=[requirements],
      python_requires='>=3.6',
      classifiers=CLASSIFIERS,
      project_urls=PROJECT_URLS)