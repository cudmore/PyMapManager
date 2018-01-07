from setuptools import setup, find_packages

setup(name='PyMapManager',
      version='0.1.1',
      description='Load, analyze, and visualize Map Manager files',
      url='http://github.com/cudmore/PyMapManager',
      author='Robert H Cudmore',
      author_email='robert.cudmore@gmail.com',
      license='MIT',
      packages=['pymapmanager','pymapmanager/mmio'],
      #zip_safe=False
)

#  This one work, it excludes interface
"""
setup(
      name='pymapmanager',
      version='0.1',
      packages=find_packages(exclude=("*.interface", "*.interface.*", "interface.*", "interface")),
      description='Python library to load and analyze MapManager files',
      url='http://github.com/cudmore/PyMapManager',
      author='Robert H Cudmore',
      author_email='robert.cudmore@gmail.com',
      license='MIT',
      zip_safe=False)

#  this is the original
"""

"""
setup(name='PyMapManager',
      version='0.1',
      description='Python library to load and analyze MapManager files',
      url='http://github.com/cudmore/PyMapManager',
      author='Robert H Cudmore',
      author_email='robert.cudmore@gmail.com',
      license='MIT',
      packages=['PyMapManager'],
      zip_safe=False)
"""      