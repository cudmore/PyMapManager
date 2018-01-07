from pymapmanager.mmMap import mmMap

if __name__ == '__main__':
	path = '../examples/exampleMaps/THet2a/THet2a.txt'
	path = '/Users/cudmore/Dropbox/MapManagerData/julia/Het2/THet2a/THet2a.txt'

	m = mmMap(path)

	tp = 2

	m.ingest(tp)