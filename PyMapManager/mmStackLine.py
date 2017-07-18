import os
import pandas as pd
import numpy as np

class mmStackLine():
    """
    A stack line represents a 3D tracing of a number of dendritic segments. Get a particular segment with getLine(segmentID=[]). Each spineROI and axonROI annotation in a mmStack is associated with one segmentID.
    """
    def __init__(self,stack):
        """
        Load a line tracing for a stack. In addition to (x,y,z), the line has 'parentID' to specify multiple dendritic tracings
        """
        self.linedb = None

        lineFile = stack.folder + 'line' + '/' + stack.name + '_l.txt'
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
            self.linedb = pd.read_csv(lineFile, header=startReadingRow, index_col=0)
            """Pandas dataframe with (x,y,z,segmentID) columns"""
            #parse linedb into segments
            #print "todo: copy 'ID' into 'segmentID'"

    def getLine(self,segmentID=[]):
        """
        Get the x/y/z values of a line tracing. Pass segmentID to get just one tracing. Note, x/y are in um, z is in slices!

        segmentID (list): List of int specifying which segmentID, pass [] to get all.

        Return: np array of (x,y,z)
        """
        if not self.linedb:
            return

        df = self.linedb
        if segmentID:
            df = df[df['ID'].isin(segmentID)]
        ret = df[['x','y','z']].values
        return ret

    def getLineLength(self, segmentID=[]):
        """Get the 3D line segment length in um"""
        pass