from __future__ import print_function

import time, copy
import pandas as pd
import numpy as np

#from pandas.plotting import autocorrelation_plot
from pandas.tools.plotting import autocorrelation_plot

def segmentAnalysis(map, ps):
    """

    Args:
        map: mmMap
        ps (dictionary): From mmUtil.newplotdict().
            Fill in plotStruct['xstat'] with stat of interest

    """
    startTime = time.time()

    ps['ystat'] = 'pDist'

    for i in range(map.numMapSegments):
        for j in range(map.numSessions):
            stackSegment = map._getStackSegmentID(i, j)
            if stackSegment is not None:
                ps['segmentid'] = [stackSegment]
                ps = map.stacks[j].getStackValues3(ps)
                # sort by pDist and make ['x'] values follow
                sortedIdx = np.argsort(ps['y'])
                xSorted = ps['x'][sortedIdx]
                ySorted = ps['y'][sortedIdx]
                if i==0 and j==0:
                    autocorrelation_plot(xSorted)

    stopTime = time.time()
    print('segmentAnalysis() took', stopTime - startTime, 'seconds')

def getMapDynamics(map, plotDict):
    """
    Calculate dynamics of annotations across a map including added, subtracted,
    density added, density subtracted, etc. etc.

    For spines, this generates a set of analysis for each dendretic segment across
    sessions in a the map

    Args:
        map (obj): mmMap
        plotDict (dict): See mmUtil.getdynamicsdict()

    Returns:
        list of dict. Use pandas.DataFrame.from_dict to easily view output

    Example::

        import pandas as pd
        from IPython.display import display # displays pretty table in ipython

        from pymapmanager.mmUtil import newplotdict
        from pymapmanager.mmMap import mmMap
        from pymapmanager.mmMapAnalysis import getMapDynamics

        # load a map
        filePath = '/Users/cudmore/Desktop/data/rr30a/rr30a.txt'
        m = mmMap(filePath=filePath)

        plotDict = newplotdict()
        plotDict = getMapDynamics(m, pd)

        for segmentReport in plotDict:
            display(pd.DataFrame.from_dict(segmentReport, orient='index'))

    """
    startTime = time.time()

    # each list holds values across sessions
    retStruct = {
        'totalnum': [],
        'numbad': [],
        'numgood': [],

        'numadd': [],
        'numsub': [],
        'numsub2': [],

        'totallen': [],
        'goodlen': [],

        'totallensmoothed': [],
        'goodlensmoothed': [],

        # pAdd, pSub, pSub2
        'padd': [],
        'psub': [],
        'psub2': [],

        # dAdd, dSub, dSub2
        'dadd': [],
        'dsub': [],
        'dsub2': [],

        # tor
        'tor': [],

        # survival
        # death
    }

    retList = []
    for i in range(map.numMapSegments):

        retList.append(copy.deepcopy(retStruct))

        totalnum = np.nan
        numsub = np.nan
        prevtotalnum = np.nan
        prevsub = np.nan  # to fill in numSub2
        for j in range(map.numSessions):
            segmentID = map._getStackSegmentID(i, j)  # segmentID is stack centric
            if segmentID >= 0:
                segmentID = int(segmentID)  # this is annoying
                df = map.stacks[j].stackdb
                if plotDict['roitype']:
                    df = df[df['roiType'].isin(plotDict['roitype'])]
                df = df[df['parentID'].isin([segmentID])]

                totalnum = df.shape[0]
                
                # 20171231, moved down
                #numbad = df['isBad'].isin([1]).sum(index=1)
                numbad = df['isBad'].isin([1]).sum()

                # todo: strip out bad
                df = df[~df['isBad'].isin([1])]

                numgood = df.shape[0]  # numgood = totalnum - 'isBad'
                
                #print(j, segmentID, 'numgood:', numgood, df['isAdd'])
                #tmp999 = df['isSub'].sum()
                #print ('tmp999:', tmp999)
                
                # should be same as above
                #numbad = totalnum - numgood
                
                #numadd = df['isAdd'].sum(index=1)
                #numsub = df['isSub'].sum(index=1)  # w.r.t. this session
                numadd = df['isAdd'].sum()
                numsub = df['isSub'].sum()  # w.r.t. this session
                numsub2 = prevsub  # w.r.t. previous session

                padd = numadd / prevtotalnum * 100
                psub = numsub / prevtotalnum * 100
                psub2 = numsub2 / prevtotalnum * 100

                totallen = map.stacks[j].line.getLineLength([segmentID])  # um
                goodlen = 0  # um

                totallensmoothed = 0  # um
                goodlensmoothed = 0  # um

                dadd = numadd / totallen
                dsub = numsub / totallen
                dsub2 = numsub2 / totallen

                # assign to return
                retList[i]['totalnum'].append(totalnum)
                retList[i]['numbad'].append(numbad)
                retList[i]['numgood'].append(numgood)

                retList[i]['numadd'].append(numadd)
                retList[i]['numsub'].append(numsub)
                retList[i]['numsub2'].append(numsub2)

                retList[i]['padd'].append(padd)
                retList[i]['psub'].append(psub)
                retList[i]['psub2'].append(psub2)

                retList[i]['totallen'].append(totallen)
                retList[i]['goodlen'].append(goodlen)

                retList[i]['totallensmoothed'].append(totallensmoothed)
                retList[i]['goodlensmoothed'].append(goodlensmoothed)

                retList[i]['dadd'].append(dadd)
                retList[i]['dsub'].append(dsub)
                retList[i]['dsub2'].append(dsub2)

            prevtotalnum = totalnum
            prevsub = numsub
    stopTime = time.time()
    print('getMapDynamics() took', stopTime - startTime, 'seconds')

    if 0:
        print(retList)
        print(len(retList))

        seg = 0  # map centrix
        print('answer for map segment', seg)
        for key, val in retList[seg].iteritems():
            print(key, val)

        # convert to a pandas dataframe
        out_df = pd.DataFrame.from_dict(retList[seg], orient='index')

    return retList

if __name__ == '__main__':
    from pymapmanager.mmMap import mmMap
    from pymapmanager import mmUtil

    mapPath = '/Users/cudmore/MapManagerData/Richard/Nancy/rr30a/rr30a.txt'
    m = mmMap(mapPath)

    plotStruct = mmUtil.newplotdict()
    plotStruct['xstat'] = 'ubssSum_int1'
    plotStruct = segmentAnalysis(m, plotStruct)
