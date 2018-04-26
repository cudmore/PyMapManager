# 20180115

from __future__ import print_function
import io
import pandas as pd
import numpy as np

from pymapmanager import mmMap
from pymapmanager import mmio

if __name__ == '__main__':
	print('=== init')
	my_mmio = mmio()
	
	print('=== map list')
	print(my_mmio.maplist())
	
	mymap = 'rr30a'
	mytp = 0
	
	"""
	print('=== load')
	# maps DO NOT need to be 'loaded' to get files from map
	# mimics mmMap.__init__()
	file1 = my_mmio.getfile('header', mymap)
	table1 = pd.read_table(io.StringIO(file1.decode('utf-8')), index_col=0)
	print(table1)
	
	tmp = my_mmio.getfile('objmap', mymap)
	header = tmp.split('\n')[0]
	objMap = np.loadtxt(tmp.split('\n'), skiprows=1)
	print(objMap)
	
	print('=== mimic mmStack.__init()')
	tmp = my_mmio.getfile('stackdb', mymap, timepoint=mytp)
	header = tmp.split('\r')[0]
	stackdb_header = pd.read_csv(io.StringIO(tmp.decode('utf-8')), header=1, index_col=False)
	stackdb_header = stackdb_header.index
	"""
	
	print('=== Load a url map')
	m = mmMap(urlmap=mymap)
	print(m)

	print('=== Upload a url map')
	mapPath = '../examples/exampleMaps/rr30a'
	my_mmio.postmap(mapPath)