

## To do

 - Set/get cookies in client browser. To do this, place ALL plotly options and then leaflet options into a dict. Save all values in each dict as cookies.
    - marker size
    - leaflet marker size
    - set name for session in session list from (None, original file, session condition)
    - default channel
 - Move /data outside of /mmserver/data
 - Implement a map pool to represent a figure in a paper
    - start by doing this in pure python
 - Intercept keyboard in leaflet, use this to switch (channel 1, channel 2, channel 3)
 - Write IGor code to export a vascular map
    - stack db will have 2x type (nodeROI, slabROI)
    - object map will hold just nodeROI (they are linked through time)
    - on click in in plotly/leaflet, don't plotRun() is slabROI (there is no map for slabs
    
 - 20170106. We now open 'otherROI' files
 
 1. [done] Generate API documentation from doc strings
 2. [done] Load individual slices dynamically (how to query number of slices in .tif file?)
 3. [done] Use the mmserver REST API to make a standalone web-app using Flask, Angular, and Plotly
 4. [done] Implement visualization of a spine run in mmserver.
 5. Make mmserver link all plot, clicking in one will highlight in other.
 6. mmserver needs to use `map pool` so publication data can easily be presented.

## Running development servers

	cd mmserver
	python mmserver.py
	
	cd mmclient
	reload -b
	
## MkDocs

Serve locally

```
cd ~/Dropbox/PyMapManager/docs
mkdocs serve
```

Push to github. This needs to be pushed from local github repo, not Dropbox repo.

```
cd ~/Sites/PyMapManager/docs
mkdocs gh-deploy --clean
```

## Synchronize with Unison

```
# Unison preferences file
root = /Users/cudmore/Dropbox/PyMapManager/
root = /Users/cudmore/Sites/PyMapManager

ignore = Name .DS_Store
ignore = Name *.DS_Store
ignore = Name *.pyc
ignore = Name *.tif
ignore = Name *.egg-info
ignore = Path .git
ignore = Path .idea

#when synchronizing between platforms or hdd formats
#rsrc = false
#perms = 0

# Be fast even on Windows
#fastcheck = yes

#servercmd=/home1/robertcu/unison
```

## Export iPython notebooks to html

```
jupyter nbconvert --ExecutePreprocessor.kernel_name=python3 --to html --execute --ExecutePreprocessor.timeout=120

jupyter nbconvert --ExecutePreprocessor.kernel_name=python2 --to html --execute --ExecutePreprocessor.timeout=120
```

## Search and replace across a number of files

search for `windows` and replace with `linux`

	grep -rl 'windows' ./ | xargs sed -i 's/windows/linux/g'

	grep -rl 'windows' ./ | xargs sed -i "" 's/windows/linux/g'
	
	find ./ -type f -exec sed -i "" "s/oldstring/new string/g" {} \;

search all files in current directory `./` for `    ` and replace with ``

	grep -rl '    ' ./ | xargs sed -i "" 's/    //g'	

from /PyMapMAnager/docs, search for '    ' and replace it with ''

	grep -rl '    ' ./docs/examples | xargs sed -i "" 's/    //g'
	
## Pushing changes to home Debian server

 1. Use Unison to update entire PyMapManager folder (pymapmanager, mmclient, mmserver)
 
 This lives in `/home/cudmore/PyMapManager`
 
 2. If I changed core soure code, make sure `pymapmanager` is updated
 
```
cd
pip uninstall PyMapManager
pip install -e PyMapManager
```

 3. Copy mmclient into /var/www/html
 
```
cd
cd PyMapManager
sudo cp -fr mmclient /var/www/html/
```

 4. Run mmserver/ in screen using gunicorn
 
Make sure it is not already running with `screen -r`. Or with `ps -aux | grep gunicorn`
 
```
cd
cd PyMapManager/mmserver
screen
gunicorn -b 0.0.0.0:5010 mmserver:app
```


## Pushing changes in mmclient/ to robertcudmore.org

## Pushing to [PyPi][pypi]

This will be available at [https://pypi.python.org/pypi/pymapmanager](https://pypi.python.org/pypi/pymapmanager) and can be installed with `pip install PyMapManager`.

There is also a test server at [https://testpypi.python.org/pypi](https://testpypi.python.org/pypi)

1. Make sure there is a `~/.pypirc` file

```
[distutils]
index-servers =
  pypi
  pypitest

[pypi]
username=your_username
password=your_password

[pypitest]
username=your_username
password=your_password
```

2. Update version in `PyMapManager/setup.py`

      version='0.1.1',

3. Makes .tar.gz in `dist/`

	cd PyMapManager
	python setup.py sdist
	
4.1 push to test server

	python setup.py sdist upload -r pypitest
	
4.2. Push to PyPi website

	python setup.py sdist upload
	

## images

I need to decide between

mmServer.py is using

	from skimage.io import imsave, imread

mmMap is using

	import scipy.misc

## cookies

see: https://stackoverflow.com/questions/14573223/set-cookie-and-get-cookie-with-javascript

[pypi]: https://pypi.python.org/pypi/pymapmanager