from setuptools import setup

'''
## Pushing to PyPi

https://pypi.python.org/pypi/pymapmanager

1. Make sure there is a `~/.pypirc` file

	[distutils]
	index-servers=pypi

	[pypi]
	username=your_username
	password=your_password

2. [old] Update version in `PyMapManager/setup.py`

<<<<<<< HEAD
'''
## Pushing to PyPi

https://pypi.python.org/pypi/pymapmanager

1. Make sure there is a `~/.pypirc` file

	[distutils]
	index-servers=pypi

	[pypi]
	username=your_username
	password=your_password

2. [old] Update version in `PyMapManager/setup.py`

=======
>>>>>>> 1fafab487d3f9fa7524c831a1474814132f4a645
      version='0.1.1',

3. Makes .tar.gz in `dist/`

	python setup.py sdist
	
4. Push to PyPi website

	python setup.py sdist upload

## Notes:
    `requests` is required by pymapmanager.mmio
'''

exec (open('pymapmanager/version.py').read())

setup(
<<<<<<< HEAD
    name='pymapmanager',
=======
    name='PyMapManager',
>>>>>>> 1fafab487d3f9fa7524c831a1474814132f4a645
    version=__version__,
    description='Load, analyze, and visualize Map Manager files',
    url='http://github.com/cudmore/PyMapManager',
    author='Robert H Cudmore',
    author_email='robert.cudmore@gmail.com',
    license='MIT',
<<<<<<< HEAD
    packages = find_packages(),
    #packages = find_packages(exclude=['version']),
    #packages=[
    #    'pymapmanager',
    #    'pymapmanager.mmio'
    #],
=======
    packages=[
        'pymapmanager',
        'pymapmanager.mmio'
    ],
>>>>>>> 1fafab487d3f9fa7524c831a1474814132f4a645
    install_requires=[
        "numpy>=1.14.0",
        "pandas>=0.22.0",
        "requests>=2.18.4",
        "scipy>=1.0.0",
        "tifffile"
    ]
)

