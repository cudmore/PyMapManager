import os
from glob import glob

from mmMap import mmMap

class mmMapPool():
    """
    Load all maps in a folder.

    Args:
        path (str): Full path to a folder.
    """

    def __init__(self, path):
        self.maps = []

        if os.path.isdir(path):
            folders = glob(path+'/*/')
            for folder in folders:
                mapName = os.path.basename(folder[:-1])
                mapFile = folder + mapName + '.txt'
                if os.path.isfile(mapFile):
                    print 'mmMapPool() loading map:', mapName
                    map = mmMap(mapFile)
                    self.maps.append(map)
        else:
            print 'error: mmMapPool() did not find path:', path