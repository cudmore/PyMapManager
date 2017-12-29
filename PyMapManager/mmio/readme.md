Python code to act as a liaison between PyMapManager annotations in `PyMapManager:mmMap` and an online repository served by [mmserver/mmserver.py][1].

Please see the main [PyMapManager][PyMapManager] documentation website.

## The cool part

### Load maps from a Map Manager server in Python

```
from pymapmanager.mmMap import mmMap
myMap = mmMap(urlmap='rr30a')

print myMap

#map:rr30a map segments:5 stacks:9 total object:2467
```

## Using mmio to manually interact with an [mmserver][1]

### Establish connection to server

    from mmio import mmio
    s = mmio(server_url='http://cudmore.duckdns.org:5010/', username='public')

### Request a map header

    mapName = 'rr30a'
    s.getfile('header', mapName)
    
### Request intensity analysis for timepoint 1, channel 2

    objectType = 'int'
    timepoint = 1
    channel = 2
    s.getfile(objectType, mapName, timepoint=timepoint, channel=channel)
        

[1]: https://github.com/cudmore/PyMapManager/tree/master/mmserver
[PyMapManager]: http://blog.cudmore.io/PyMapManager/