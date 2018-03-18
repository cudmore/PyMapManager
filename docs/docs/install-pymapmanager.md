
## Install from [PyPi][PyPi]

	pip install PyMapManager
	
This will install the most recent version from [PyPi](https://pypi.python.org/pypi/pymapmanager).

## Install from a manual download

### 1) Download the repo

This will make a `PyMapManager` folder.

	git clone https://github.com/cudmore/PyMapManager.git

### 2) Install PyMapManager (from the downloaded folder)

	pip install PyMapManager/
	
## Testing the install from a `python` prompt

Check the version

```python
import pymapmanager
pymapmanager.__version__
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

## We have tons more examples

Head over to the [examples/][examples/] folder in the main Github repository.

Experimental: You should be able to view these notebooks at [binder][binder]. Beware, binder is experimental and link may be broken.


[examples/]: https://github.com/cudmore/PyMapManager/tree/master/examples
[binder]: https://hub.mybinder.org/user/cudmore-pymapmanager-8r5uk9g6/tree/examples