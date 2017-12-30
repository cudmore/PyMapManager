

## To do

 1. [done] Generate API documentation from doc strings
 2. [done] Load individual slices dynamically (how to query number of slices in .tif file?)
 3. [done] Use the mmserver REST API to make a standalone web-app using Flask, Angular, and Plotly
 4. [done] Implement visualization of a spine run in mmserver.
 5. Make mmserver link all plot, clicking in one will highlight in other.
 6. mmserver needs to use `map pool` so publication data can easily be presented.

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

