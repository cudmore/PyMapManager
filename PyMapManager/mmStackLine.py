import os, math
import pandas as pd
import numpy as np

class mmStackLine():
    """
    A stack line represents a 3D tracing of a number of dendritic segments.

    Get a particular segment with `getLine(segmentID=[])`.

    Each spineROI and axonROI annotation in a mmStack is associated with one segmentID.
    """
    def __init__(self,stack):
        """
        Load a line tracing for a stack. In addition to (x,y,z), the line has 'parentID' to specify multiple dendritic tracings

        Args:
            stack (:class:`PyMapManager.mmStack`): The stack that will own the line.

        """
        self.stack = stack
        self.linedb = None

        if stack.map:
            lineFile = stack.folder + 'line' + '/' + stack.name + '_l.txt'
        else:
            lineFile = stack.folder + 'stackdb' + '/' + stack.name + '_l.txt'
        if os.path.isfile(lineFile):
            with open(lineFile, 'rU') as f:
                header = f.readline().rstrip()
            if header.endswith(';'):
                header = header[:-1]
            header = header.split(';')
            d = dict(s.split('=') for s in header)

            # line file has a header of segments
            # 1 file header + 1 segment header + numHeaderRow
            numHeaderRow = int(d['numHeaderRow'])
            startReadingRow = 1 + 1 + numHeaderRow
            self.linedb = pd.read_csv(lineFile, header=startReadingRow, index_col=0) #  Pandas dataframe with (x,y,z,segmentID) columns

    def getLineValues3(self,pd):
        """
        Args:
            pd (dict): See mmUtil.newplotdict()

        Returns: pd with ['x'], ['y'], and ['z'] values filled in as numpy ndarray
        """
        if self.linedb is None:
            return

        df = self.linedb
        if pd['segmentid']:
            df = df[df['ID'].isin(pd['segmentid'])]
        pd['x'] = df['x'].values
        pd['y'] = df['y'].values
        pd['z'] = df['z'].values

        return pd

    def getLine(self,segmentID=[]):
        """
        Get the x/y/z values of a line tracing. Pass segmentID to get just one tracing. Note, x/y are in um, z is in slices!

        Args:
            segmentID (list): List of int specifying which segmentID, pass [] to get all.

        Return:
            numpy ndarray of (x,y,z)
        """
        if self.linedb is None:
            return

        df = self.linedb
        if segmentID:
            df = df[df['ID'].isin(segmentID)]
        ret = df[['x','y','z']].values
        return ret

    def _EuclideanDist(self, from_xyz, to_xyz):
        """
        Get the euclidean distance between two points, pass tuple[2]=np.nan to get 2d distance

        Args:
            from_xyz (3 tuple):
            to_xyz (3 tuple):

        Returns: float

        """
        if from_xyz[2] and to_xyz[2]:
            ret = math.sqrt(math.pow(abs(from_xyz[0]-to_xyz[0]),2) \
                + math.pow(abs(from_xyz[1]-to_xyz[1]),2) \
                + math.pow(abs(from_xyz[2]-to_xyz[2]),2))
        else:
            ret = math.sqrt(math.pow(abs(from_xyz[0]-to_xyz[0]),2) \
                + math.pow(abs(from_xyz[1]-to_xyz[1]),2))
        return ret

    def getLineLength(self, segmentID, smoothz=None):
        """Get the 3D line length for one segment (um)

        Args:
            segmentID (int): Stack centric segmentID, different from other functions, requires an int (not a list)
            smoothz (int): Smooth Z

        Returns:
            3D length (float) of segmentID
        """
        # strip down df
        df = self.linedb
        df = df[df['ID'].isin(segmentID)]
        # grab x/y/z values (z is in slices!!!)
        values = df[['x', 'y', 'z']].values
        # convert z to microns
        values[:,2] *= self.stack.voxelz # slices * um/slice -->> um
        # filter z
        if smoothz:
            pass
        # step through rows and get euclidean distance between each row i and row i-1
        dist = 0.0
        prev_xyz = (np.nan, np.nan, np.nan)
        for i, row in enumerate(values):
            this_xyz = (row[0], row[1], row[2])
            if i>0:
                dist += self._EuclideanDist(prev_xyz, this_xyz)
            prev_xyz = tuple(this_xyz)
        return dist