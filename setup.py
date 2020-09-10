from setuptools import setup, find_packages
 
__version__ = '0.0.1'

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.readlines()
    
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
      install_requires=[requirements])