from pymapmanager.mmMap import mmMap

if __name__ == '__main__':
	path = '../examples/exampleMaps/THet2a/THet2a.txt'
	path = '/Users/cudmore/Dropbox/MapManagerData/julia/Het2/THet2a/THet2a.txt'
	path = '/Users/cudmore/Dropbox/MapManagerData/amit/BD_NGDG450/BD_NGDG450.txt'

	m = mmMap(path)

	tp = 5

	m.ingest(tp)