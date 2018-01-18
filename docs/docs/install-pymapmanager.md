
## Install from [PyPi][PyPi] using pip

	pip install PyMapManager
	
This will install the most recent version from [PyPi](https://pypi.python.org/pypi/pymapmanager).

## Install from a manual download

### 1) Download the repo

This will make a `PyMapManager` folder.

	git clone https://github.com/cudmore/PyMapManager.git

### 2) Install required Python libraries

	pip install -r PyMapManager/requirements.txt
	
### 3) Install PyMapManager (from the downloaded folder)

	pip install PyMapManager/
	
## Testing the install from a `python` prompt

Check the version

```python
>>> import pymapmanager
>>> pymapmanager.__version__
'0.0.3'
```

Load an example map

```python
from pymapmanager import mmMap
path = 'PyMapManager/examples/exampleMaps/rr30a'
myMap = mmMap(path)
```
You should see (exact seconds will vary)

```
map rr30a loaded in 0.45 seconds.
```

Then type

```
print myMap
```

And you should see

```
map:rr30a map segments:5 stacks:9 total object:2467
```
	
[Pypi]: https://pypi.python.org/pypi/pymapmanager