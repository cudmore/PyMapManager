from __future__ import print_function

import os, time
from glob import glob # for pool

from pymapmanager.mmStack import mmStack

class mmStackPool():
    """
    Load all .tif stacks in a folder.

    Args:
        path (str): Full path to a folder containing .tif files.

    Example::

		path = myMapFile = 'PyMapManager/examples/exampleMaps/'
        stacks = mmStackPool(path)
        for stack in stacks:
            print(stack)
    """

    def __init__(self, path):
        self._stacks = []

        startTime = time.time()

        if os.path.isdir(path):
            files = glob(path+'/*')
            for file in files:
                isTiff = file.endswith('.tif')
                if (isTiff):
                    print('=== mmStackPool() loading stack:', file)
                    stack = mmStack(filePath=file)
                    self.stacks.append(stack)
        else:
            print('error: mmMapPool() did not find path:', path)

        stopTime = time.time()
        print('mmStackPool() loaded', len(self.stacks), 'stacks in', stopTime-startTime, 'seconds.')

    @property
    def stacks(self):
        """
        List of :class:`pymapmanager.mmStack` in the mmStackPool.
        """
        return self._stacks

    def __iter__(self):
        i = 0
        while i < len(self.stacks):
            yield self.stacks[i]
            i+=1

    def __str__(self):
        count = 0
        for stack in self:
            count += stack.numObj
        return ('pool:'
                + ' num stacks:' + str(len(self.stacks))
                + ' num obj:' + str(count))
