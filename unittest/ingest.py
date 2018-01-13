from pymapmanager.mmMap import mmMap

if __name__ == '__main__':
	path = '/Users/cudmore/Dropbox/MapManagerData/julia/Het2/THet2a/THet2a.txt'
	path = '/Users/cudmore/Dropbox/MapManagerData/amit/BD_NGDG450/BD_NGDG450.txt'
	path = '/Volumes/fourt/MapManagerData/ye_maps/F27A_1/F27A_1.txt'

	# Take some command line parameters
	# 1: path to map
	# 2: tp
	# 3: channel
	
	# check that path to map file exists
	
	# load the map
	m = mmMap(path)

	# check that tp exists
	
	# check that channel exists
	

	tp = 2

	# do ingest
	m.ingest(tp)