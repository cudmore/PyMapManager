import os, io, time
from glob import glob # for mmStackPool
from errno import ENOENT
import pandas as pd
import numpy as np
#import uuid # to generate a unique id for each spine
import tifffile

from pymapmanager.mmStackLine import mmStackLine
from pymapmanager.mmio import mmio
from pymapmanager.mmUtil import newplotdict

class mmStack():
    """
    A stack contains a 3D Tiff, a list of 3D annotations, and optionally a number of segment tracings.

    A stack can either be a single time-point or be embeded into a session of a :class:`pymapmanager.mmMap`.

    Args:
        filePath (str): Full path to tiff file, this is used to open single timepoint stacks (not stacks in a map)
        name (str): Name of the stack. Used to fetch .tif file
        numChannels (int): Number of channels.
        map (object): Runtime object of :class:`pymapmanager.mmMap` that created the stack.
        mapSession (int): The map session number for the stack.

    Example::

        xxx
        yyy
        zzz
    """

    def __init__(self, filePath=None, name=None, numChannels=1, map=None, mapSession=None, urlmap=None):
        self.fileName = filePath
        self._folder = '' #map.folder #re-route this to load a single time-point stack from its .tif !!!
        self.name = name #re-route this for single channel stack
        self.numChannels = numChannels #get this from stackdb???

        self._stackdb = None

        self.map_ = map
        self.mapSession = mapSession

        self.doFile = True
        self.server = None
        self.urlmap = None

        if urlmap is not None:
            #from server
            self.doFile = False
            self.urlmap = urlmap
            self.server = mmio.mmio()
        elif map is not None:
            # from mm map
            self._folder = map._folder
        elif filePath is not None:
            # single timepoint
            self._folder = os.path.dirname(filePath) + '/' #  Path to enclosing folder, ends in '/'.
            self.name = os.path.basename(filePath).strip('.tiff')  #  Name of the stack
            if self.name.endswith('_ch1'): self.name = self.name[:-4]
            if self.name.endswith('_ch2'): self.name = self.name[:-4]
            # todo: we don't have numChannel in header, infer this from other _ch1.tif and _ch2.tif files in same directory
        else:
            # undefined
            print 'error: mmStack() constructor got bad parameters.'
            return

        #todo: to open generic tif (no stackdb), we need to use tifffile load of first image, query tif header values (gonna be a pain)
        #f = tifffile.TiffFile('/Users/cudmore/Desktop/data/rr30a/raw/rr30a_s0_ch2.tif', pages=[0])
        self.voxelx = 1.0 #float(map.getValue('dx', mapSession))
        self.voxely = 1.0 #float(map.getValue('dy', mapSession))
        self.voxelz = 1.0 #int(map.getValue('dz', mapSession)) #we use z as index into numpy array, can't be int !!!

        self._images = None #  3D numpy array of the stacks images, axis 0 is slices"""

        ###############################################################################
        #stackdb
        if self.doFile:
            stackdbFile = self._folder + 'stackdb' + '/' + self.name + '_db2.txt'
            if not os.path.isfile(stackdbFile):
                raise IOError(ENOENT, 'mmStack did not find stackdbFile:', stackdbFile)
            with open(stackdbFile, 'rU') as f:
                header = f.readline().rstrip()
            self._stackdb = pd.read_csv(stackdbFile, header=1, index_col=False)
            self._stackdb['Idx'] = self.stackdb.index
        else:
            tmp = self.server.getfile('stackdb', self.urlmap, timepoint=self.mapSession)
            header = tmp.split('\r')[0]
            self._stackdb = pd.read_csv(io.StringIO(tmp.decode('utf-8')), header=1, index_col=False)
            self._stackdb['Idx'] = self.stackdb.index

        # stackdb file headers has (voxelx=0.12;voxely=0.12;voxelz=1;)
        if header.endswith(';'):
            header = header[:-1]
        header = header.split(';')
        d = dict(s.split('=') for s in header)
        self.voxelx = float(d['voxelx']) # um
        self.voxely = float(d['voxely'])
        self.voxelz = float(d['voxelz'])

        # julias single time-point stack have pixels=NaN ???
        #self.pixelsx = int(d['pixelx']) # pixels
        #self.pixelsy = int(d['pixely'])
        #self.numSlices = int(d['pixelz'])

        #not currently using, good idea for EVERY spine to have unique ID?
        # hashID = [uuid.uuid4().hex for i in range(self.stackdb.shape[0])]
        # self.stackdb['hashID'] = hashID #32 character hexadecimal string

        m = self.stackdb.shape[0]

        # append columns (map, hashID, next, nexttp, prev, prevtp, runIdx)
        if map and mapSession>=0:
            self.stackdb['mapName'] = map.name
            self.stackdb['mapSession'] = mapSession
            mapCond = map.getValue('mapCond', 0)  # one map condition, in column zero
            #should have numObj()-1 here ???
            self.stackdb['next'] = map.objMap[1,0:self.numObj,mapSession].tolist() # 1: next
            self.stackdb['nexttp'] = map.objMap[2,0:self.numObj,mapSession].tolist() # 2: nextTP
            self.stackdb['prev'] = map.objMap[3,0:self.numObj,mapSession].tolist() # 3: prev
            self.stackdb['prevtp'] = map.objMap[4,0:self.numObj,mapSession].tolist() # 4: prevTP
            self.stackdb['runIdx'] = map.objMap[6,0:self.numObj,mapSession].tolist() # 4: runIdx
            self.stackdb['days'] = map.getValue('days', mapSession)
            self.stackdb['sessCond'] = map.getValue('condStr', mapSession)
            self.stackdb['mapCond'] = mapCond

            self.stackdb['isAdd'] = np.nan
            self.stackdb['isSub'] = np.nan
            if mapSession > 0:
                self.stackdb['isAdd'] = [np.nan if a >= 0 else 1 for a in map.objMap[3,0:m,mapSession]] # 3 is prev
            if mapSession < map.numSessions-1:
                self.stackdb['isSub'] = [np.nan if a >= 0 else 1 for a in map.objMap[1,0:m,mapSession]] # 1 is next
            self.stackdb['isTransient'] = self.stackdb['isAdd'].isin([1]) & self.stackdb['isSub'].isin([1])


        # int1 and in2 will have some column names in common with stackdb
        #assuming we want values from stackdb, just drop them
        #droplist = ['x','y','z','isDirty','intBad']

        ###############################################################################
        # int1
        if self.doFile:
            int1File = self._folder + 'stackdb' + '/' + self.name + '_Int1.txt'
            if not os.path.isfile(int1File):
                raise IOError(ENOENT, 'mmStack did not find int1File:', int1File)
            int1 = pd.read_csv(int1File, header=1, index_col=False)
            int1 = int1.add_suffix('_int1')
            self._stackdb = self.stackdb.join(int1)
        else:
            tmp = self.server.getfile('int', self.urlmap, timepoint=self.mapSession, channel=1)
            int1 = pd.read_csv(io.StringIO(tmp.decode('utf-8')), header=1, index_col=False)
            int1 = int1.add_suffix('_int1')
            self._stackdb = self.stackdb.join(int1)

        ###############################################################################
        # int2
        if self.numChannels==2:
            if self.doFile:
                int2File = self._folder + 'stackdb' + '/' + self.name + '_Int2.txt'
                if not os.path.isfile(int2File):
                    raise IOError(ENOENT, 'mmStack did not find int2File:', int2File)
                int2 = pd.read_csv(int2File, header=1, index_col=False)
                int2 = int2.add_suffix('_int2')
                self._stackdb = self.stackdb.join(int2)
            else:
                tmp = self.server.getfile('int', self.urlmap, timepoint=self.mapSession, channel=2)
                int2 = pd.read_csv(io.StringIO(tmp.decode('utf-8')), header=1, index_col=False)
                int2 = int2.add_suffix('_int2')
                self._stackdb = self.stackdb.join(int2)

        ###############################################################################
        # line
        self._line = None
        self._loadLine()

    @property
    def stackdb(self):
        """
        stackdb (pandas dataframe): Pandas dataframe of annotations, one per row. Columns are statistic names.
            See `pymapmanager.mmUtil STACK_STATS` for valid statistic names.
        """
        return self._stackdb

    @property
    def numObj(self):
        """The number of objects (annotations) in the stack. This is the number of rows in stackdb"""
        if self.stackdb is not None:
            return self.stackdb.shape[0]
        else:
            return 0

    @property
    def images(self):
        """
        images (numpy ndarray): 3D numpy ndarray of image data.
            This is not valid until :func:`loadStackImages` is called.
            Slices are in the 1st dimension, use images[0,:,:] to get the first image.
        """
        return self._images

    @property
    def numSlices(self):
        """
        Number of image slices in the stack.
        """
        if self.images is not None:
            return self.images.shape[0]
        else:
            return None

    @property
    def line(self):
        """
        line (:class:`pymapmanager.mmStackLine`): A 3D tracing of segments.
        """
        return self._line

    @property
    def numSegments(self):
        """
        Number of line segments in the stack.
        """
        if self.stackdb is not None:
            unique = self.stackdb['parentID'].unique()
            return np.count_nonzero(~np.isnan(unique))
        else:
            return None

    def __str__(self):
        mapname = self.map_.name if self.map_ else 'None'
        return ('stack:' + self.name
                + ' map:' + mapname
                + ' session:' + str(self.mapSession)
                + ' objects:' + str(self.numObj)
                + ' segments:' + str(self.numSegments)
                + ' channels:' + str(self.numChannels))

    def getStatNames(self):
        """Get column names from stack. These are valid values for plot functions."""
        return list(self.stackdb.columns.values)

    def getStackValues3(self, pd):
        """Get x/y/z stats using a plot dict pd

        Args:
            pd (dict): A :py:const:`mmUtil.PLOT_DICT`

        Returns:
            pd with pd['x'], pd['y'] and pd['z'] filled in with values

        Note::

            Returns pd filled in as follows:
            pd['x']: x stat values if pd['xstat'], length is number of annotations matching criteria in original pd argument
            pd['y']: y stat values if pd['ystat']
            pd['z']: z stat values if pd['zstat']
            pd['stackidx']: stack index of returned values
            pd['reverse']: same length as stackdb.numObj,
                reverse[i]>=0 gives index into pd['x'] for annotation i, reverse[i]=='nan' means annotation i was not included
        """

        ret = self.stackdb
        if pd['segmentid']:
            ret = ret[ret['parentID'].isin(pd['segmentid'])]
        if pd['roitype']:
            ret = ret[ret['roiType'].isin(pd['roitype'])]

        if pd['xstat']:
            pd['x'] = ret[pd['xstat']].values
        if pd['ystat']:
            pd['y'] = ret[pd['ystat']].values
        if pd['zstat']:
            pd['z'] = ret[pd['zstat']].values

        pd['stackidx'] = ret.index.values

        reverse = np.zeros(self.numObj)
        reverse[:] = np.NaN
        for i, val in enumerate(pd['stackidx']):
            if val >= 0:
                reverse[val] = i
        pd['reverse'] = reverse

        return pd

    def getStackValues2(self, stat, roiType=['spineROI'], segmentID=[], plotBad=False, plotIntBad=False):
        """

        Args:
            token: stack statistic
            roiType: yyy
            segmentID: zzz

        Returns: 1D numpy ndarray of values

        """
        plotDict = newplotdict()
        plotDict['roitype'] = roiType
        plotDict['xstat'] = stat
        plotDict['segmentid'] = segmentID
        plotDict['plotbad'] = plotBad
        plotDict['plotIntBad'] = plotIntBad

        plotDict = self.getStackValues3(plotDict)
        return plotDict['x']

    def _loadLine(self):
        """
        Load a line (mmStackLine) associated with the stack. Sets 'line' instance variable.

        Returns:
            None.
        """
        self._line = mmStackLine(self)

    def loadStackImages(self, channel=2):
        """
        Load the images for a stack. Sets 'images' instance variable

        Args:
            channel (int): Specifies the channel number to load. MapManager uses single channel .tif files. Each channel has its own file: _ch1.tif, _ch2.tif, _ch3.tif.

        Return:
            images (3D ndarray): 3D numpy array of images.
        """
        startTime = time.time()

        if self.urlmap is not None:
            sliceNotUsed = 1
            content = self.server.getimage(self.urlmap, self.mapSession, sliceNotUsed, channel=channel)
            with tifffile.TiffFile(io.BytesIO(content)) as tif:
                self._images = tif.asarray()
        else:
            if channel == 1 or channel is None:
                chStr = '_ch1'
            else:
                chStr = '_ch2'

            if self.map_:
                tiffFileName = self._folder + 'raw' + '/' + self.name + chStr + '.tif'
            else:
                tiffFileName = self._folder + self.name + chStr + '.tif'

            if not os.path.isfile(tiffFileName):
                raise IOError(ENOENT, 'mmStack did not find tiffFileName:', tiffFileName)

            try:
                """
                tmp = tifffile.TiffFile(tiffFileName)
                print tmp.is_imagej
                print tmp.pages #.imagej_tags()
                """

                with tifffile.TiffFile(tiffFileName) as tif:
                        self._images = tif.asarray()

            except:
                print 'ERROR: mmStack.loadStackImages() did not load tiff file:', tiffFileName
                raise

        if len(self.images.shape) > 3:
            print 'WARNING: mmStack.loadStackImages() just loaded a stack with a bizarre shape:', self.images.shape
            self.images = self.images[:,:,:,1]

        # this is read from stackdb header
        #if self.numSlices is None:
        #    self.numSlices = self.images.shape[0]

        '''
        # load both channels and make an rgb image
        self.rgb = np.zeros(4)
        tiffFileName = self._folder + 'raw' + '/' + self.name + '_ch1.tif'
        with tifffile.TiffFile(tiffFileName) as tif:
            self.rgb[...,1] = tif.asarray()
        tiffFileName = self._folder + 'raw' + '/' + self.name + '_ch2.tif'
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


