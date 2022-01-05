## Front end to MaManager using PyQt5

This is a basic prototype. It leaves a lot to be desired.

## Install

1) Make a virtual environment

```
cd PyQtMapManager
python -m venv mmqt_env

# activate it
source mmqt_env/bin/activate

# on linux, always upgrade pip
pip install --upgrade pip

```

2) Install backend MapManager

```
# in the `PyQtMapManager` folder
pip install -e ../.
```

3) Install PyQtMapManager

```
# in the `PyQtMapManager` folder
pip install -r requirements.txt
```

## Run

```
python main.py
```