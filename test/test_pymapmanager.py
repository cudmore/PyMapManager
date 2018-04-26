# content of test_sample.py

import os

import numpy as np

from pymapmanager import mmMap
from pymapmanager.mmUtil import newplotdict

def test_load():
	path = 'examples/exampleMaps/rr30a'
	
	'''
	if not os.path.isdir(path):
		print('my error: did not find path:', path)
	'''
	
	m = mmMap(path)
	
	assert m.numMapSegments == 5
	
	plotDict = newplotdict()
	plotDict['plotbad'] = True
	plotDict['xstat'] = 'days'
	plotDict['ystat'] = 'pDist'
	plotDict['zstat'] = 'ubssSum_int2' #'sLen3d_int1' #swap in any stat you like, e.g. 'ubssSum_int2'
	plotDict['segmentid'] = 0
	plotDict = m.getMapValues3(plotDict)

	assert plotDict['x'].shape == (112, 9)
	assert np.nanmean(plotDict['x']) == 9.53251974522293

'''
def func(x):
    return x + 1

def test_answer():
    assert func(3) == 5
'''