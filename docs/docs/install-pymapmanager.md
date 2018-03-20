
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

```python
print myMap
```

And you should see

```
map:rr30a map segments:5 stacks:9 total object:2467
```
	
## We have tons more examples

Head over to the [examples/][examples/] folder in the main Github repository.

## Running Jupyter notebooks

At this point, it is super simple to run all the example Jupyter notebooks interactively. Back at a command prompt, not in Python, enter the following commands and you should get a web page with interactive examples.

	pip install jupyter
	cd PyMapManager/examples
	jupyter notebook


[Pypi]: https://pypi.python.org/pypi/pymapmanager
[examples/]: https://github.com/cudmore/PyMapManager/tree/master/examples
[binder]: https://hub.mybinder.org/user/cudmore-pymapmanager-8r5uk9g6/tree/examples