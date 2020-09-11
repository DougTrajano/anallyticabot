from setuptools import setup, find_packages
 
__version__ = '0.0.3'

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.readlines()
    
PROJECT_URLS = {
    "Bug Tracker": "https://github.com/DougTrajano/mirage-chatbot-analytics/issues",
    "Documentation": "https://github.com/DougTrajano/mirage-chatbot-analytics/tree/master/documentation",
    "Source Code": "https://github.com/DougTrajano/mirage-chatbot-analytics",
}

CLASSIFIERS = [
    "Development Status :: 2 - Pre-Alpha",
    "Environment :: Console",
    "Operating System :: OS Independent",
    "Intended Audience :: Science/Research",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Cython",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]

setup(name='mirage-chatbot-analytics',
      version=__version__,
      url='https://github.com/DougTrajano/mirage-chatbot-analytics',
      license='GPL',
      author='Douglas Trajano',
      author_email='douglas.trajano@outlook.com',
      description='A package with analytical tools to improve chatbots.',
      packages=find_packages(exclude=['tests']),
      long_description=open('README.md').read(),
      tests_require=['pytest'],
      zip_safe=False,
      install_requires=[requirements],
      python_requires='>=3.6',
      classifiers=CLASSIFIERS,
      project_urls=PROJECT_URLS)