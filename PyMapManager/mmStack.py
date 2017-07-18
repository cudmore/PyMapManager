import os, time
import pandas as pd
import numpy as np
import uuid # to generate a unique id for each spine
import tifffile

import logging

from mmStackLine import mmStackLine

class mmStack():
    """
    A stack contains a 3D Tiff, a list of 3D annotations, and optionally a number of dendritic (segment) tracings.

    A stack can either be a single time-point or be embeded into a session of a :class:`PyMapManager.mmMap`.

    Attributes:
        name (str): Name of the stack. Used to fetch .tif file
        numChannels (int): Number of channels.
        map (object): Runtime object of :class:`PyMapManager.mmMap` that created the stack.
        mapSession (int): The map session number for the stack.

        stackdb (pandas dataframe): Pandas dataframe of annotations, one per row. Columns are statistic names.
            See `PyMapManager.mmUtil STACK_STATS` for valid statistic names
        images (numpy ndarray): 3D matrix of image pixels.
    """

    def __init__(self, name=None, numChannels=1, map=None, mapSession=None):

        logging.debug('mmStack.__init__() map:' + map.name + ' stack:' + name)

        self.folder = map.folder #re-route this to load a single time-point stack from its .tif !!!
        self.name = name # re-route this for single channel stack
        self.numChannels = numChannels #get this from stackdb???

        self.map = map
        self.mapSession = mapSession

        # stackdb file headers has (voxelx=0.12;voxely=0.12;voxelz=1;)
        self.voxelx = float(map.getValue('dx', mapSession))
        self.voxely = float(map.getValue('dy', mapSession))
        self.voxelz = int(map.getValue('dz', mapSession)) #we use z as index into numpy array, can't be int !!!
        self.numSlices = 0 # assigned in loadStack()
        self.numSegments = 0

        self.images = None #  3D numpy array of the stacks images, axis 0 is slices"""

        #stackdb
        self.stackdb = None
        stackdbFile = self.folder + 'stackdb' + '/' + self.name + '_db2.txt'
        if os.path.isfile(stackdbFile):
            #self.stackdb = pd.read_csv(stackdbFile, header=1, index_col=0)
            self.stackdb = pd.read_csv(stackdbFile, header=1, index_col=False)

            # CRITICAL: Idx in stackdb is corrupt (it is not used in Igor MapManager)
            #self.stackdb.reset_index(drop=True, inplace=True)

            self.stackdb['Idx'] = self.stackdb.index

            #self.images = None # assigned in self.loadStack()

            # append columns (map, hashID, next, nexttp, prev, prevtp, runIdx)
            self.stackdb['mapName'] = map.name
            self.stackdb['mapSession'] = mapSession

            hashID = [uuid.uuid4().hex for i in range(self.stackdb.shape[0])]
            self.stackdb['hashID'] = hashID #32 character hexadecimal string

            if map and mapSession>=0:
                #should have numObj()-1 here ???
                self.stackdb['next'] = map.objMap[1,0:self.numObj(),mapSession].tolist() # 1: next
                self.stackdb['nexttp'] = map.objMap[2,0:self.numObj(),mapSession].tolist() # 2: nextTP
                self.stackdb['prev'] = map.objMap[3,0:self.numObj(),mapSession].tolist() # 3: prev
                self.stackdb['prevtp'] = map.objMap[4,0:self.numObj(),mapSession].tolist() # 4: prevTP
                self.stackdb['runIdx'] = map.objMap[6,0:self.numObj(),mapSession].tolist() # 4: runIdx

            unique = self.stackdb['parentID'].unique()
            self.numSegments = np.count_nonzero(~np.isnan(unique))

        else:
            print 'mmStack() error, did not find file:', filePath

        # int1 and in2 will have some column names in common with stackdb
        #assuming we want values from stackdb, just drop them
        #droplist = ['x','y','z','isDirty','intBad']

        # int1
        int1File = self.folder + 'stackdb' + '/' + self.name + '_Int1.txt'
        if os.path.isfile(int1File):
            int1 = pd.read_csv(int1File, header=1, index_col=False)
            #int1 = int1.drop(droplist, axis=1)
            #print name, 'int1:', int1.columns.values.tolist()
            int1 = int1.add_suffix('_int1')
            self.stackdb = self.stackdb.join(int1)
        else:
            print 'mmStack error, did not find file', int1File

        # int2
        if self.numChannels==2:
            int2File = self.folder + 'stackdb' + '/' + self.name + '_Int2.txt'
            if os.path.isfile(int2File):
                int2 = pd.read_csv(int2File, header=1, index_col=False)
                #int2 = int2.drop(droplist, axis=1)
                #print int2.columns.values.tolist()
                int2 = int2.add_suffix('_int2')
                self.stackdb = self.stackdb.join(int2)
            else:
                print 'mmStack error, did not find file', int2File

        # line
        self.line = None
        self._loadLine()

    def add_to_map(self, map, session):
        """Add the stack into a map at the given session index"""

    def getStackValues(self, token, roiType='spineROI', segmentID=[]):
        """
        Get the values for a given token. Valid tokens are columns of stackdb.
        Specify roiType to get values for a given type.
        Specify a list of segments with segmentID to get just those segments.

        Args:
            token (str): Statistic name (Must be a column name in pandas dataframe stackdb)
            roiType (str): xxx
            segmentID (list): xxx

        Return:
            1D numpy array of 'token' values matching criteria.
            This is NOT the same size as stackdb it only contains values of interest.
            Use reverseLookup to find index into theValues that corresponds to an actual stackdb index
        """
        ret = self.stackdb
        if segmentID:
            ret = ret[ret['parentID'].isin(segmentID)]
        #ret = ret[ret['roiType'].isin([roiType])][token].values
        ret = ret[ret['roiType'].isin([roiType])]
        theValues = ret[token].values
        theStackdbIdx = ret.index.values # values makes a ndarray

        reverseLookup = np.zeros(self.numObj())
        reverseLookup[:] = np.NaN
        for i, val in enumerate(theStackdbIdx):
            if val >= 0:
                reverseLookup[val] = i

        return theValues, theStackdbIdx, reverseLookup

    def numObj(self):
        """Get the number of objects (annotations) in the stack. This is the number of rows in stackdb"""
        return self.stackdb.shape[0]

    def _loadLine(self):
        """
        Load a line (mmStackLine) associated with the stack. Sets 'line' instance variable.

        Return: None.
        """
        self.line = mmStackLine(self)

    def loadStack(self,channel=2):
        """
        Load the images for a stack. Sets 'images' instance variable

        Args:
            channel (int): Specifies the channel number to load. MapManager uses single channel .tif files. Each channel has its own file: _ch1.tif, _ch2.tif, _ch3.tif.

        Return:
            3D numpy array of images.
        """
        startTime = time.time()

        if channel == 1 or channel is None:
            chStr = '_ch1'
        else:
            chStr = '_ch2'

        tiffFileName = self.folder + 'raw' + '/' + self.name + chStr + '.tif'
        #with tifffile.TiffFile(tiffFileName, key=0) as tif:
        with tifffile.TiffFile(tiffFileName) as tif:
                self.images = tif.asarray()

        self.numSlices = self.images.shape[0]

        '''
        # load both channels and make an rgb image
        self.rgb = np.zeros(4)
        tiffFileName = self.folder + 'raw' + '/' + self.name + '_ch1.tif'
        with tifffile.TiffFile(tiffFileName) as tif:
            self.rgb[...,1] = tif.asarray()
        tiffFileName = self.folder + 'raw' + '/' + self.name + '_ch2.tif'
        with tifffile.TiffFile(tiffFileName) as tif:
            self.rgb[...,2] = tif.asarray()
        imshow(self.rgb)
        plt.show()
        '''

        stopTime = time.time()
        print 'mmStack.loadStack() loaded map session', self.mapSession, 'channel', channel, 'in', round(stopTime-startTime,2), 'seconds.'

        # debug
        # print self.images
        #import matplotlib.pyplot as plt
        #self.imgplot = plt.imshow(self.images[0,:,:])

        return self.images