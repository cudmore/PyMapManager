import os
import tkFileDialog
from Tkinter import *

import matplotlib as mpl

mpl.use('TkAgg')

import matplotlib.pyplot as plt

from mmMap import mmMap
from mmMapPool import mmMapPool
from mmStackPlot import mmStackPlot
from mmMapPlot import mmMapPlot

if 0:
    filePath = '/Users/cudmore/Desktop/data/rr30a/rr30a.txt'
    #filePath = 'c:\\users\cudmore\Desktop\PyMapManager\data\rr30a\rr30a.txt'
    print 'filePath:', filePath
    m = mmMap(filePath=filePath)

#print m.table.loc['hsStack'].count()
#print m.getTable().index
#print m.getTable().loc['px'].iloc[1]
#print m.getValue('hsStack',0)
#print m.getStack(1)
#print m.numChannels

#print m.stacks[2].stackdb.columns.values.tolist()

#print m.stacks[2].stackdb['hashID'].values

#print m.stacks[1].getValues('x')
if 0:
    session = 1
    segmentID = None #4

    #p = mmStackPlot(m.stacks[session])
    #p.plot('ubssSum','int1','pDist','stackdb',roiType='spineROI')
    #p.plot('ubssSum','int1','pDist','stackdb',roiType='spineROI', segmentID=segmentID)

    mp = mmMapPlot(m)
    mp.plot()

if 0:
    path = '/Users/cudmore/MapManagerData/richard/Nancy'
    mmMapPool(path)

class MyFirstGUI:
    def __init__(self, master):
        self.master = master
        master.title("pyMapManager")

        #this is ugly as shit
        # master.configure(bg='gray')

        self.defaultPath = ''

        self.m = []
        #self.m.append(m)
        self.numMaps = 0

        #
        loadframe = LabelFrame(root, text="Load")
        loadframe.grid(row=0, columnspan=4, sticky='W')

        self.load_map_button = Button(loadframe, text="Load Map", command=self.load_map)
        self.load_map_button.grid(row=0, column=0)

        self.load_dir_button = Button(loadframe, text="Load Dir", command=self.load_dir)
        self.load_dir_button.grid(row=0, column=1)

        v = StringVar()
        self.path_entry = Entry(loadframe, textvariable=v)
        #v.set(self.m[0].folder)
        self.path_entry.grid(row=0, column=2)

        self.load_stack_button = Button(loadframe, text="Load Stack", command=self.load_stack)
        self.load_stack_button.grid(row=0, column=3)

        #
        plotframe = LabelFrame(root, text="Plot")
        plotframe.grid(row=1, column=0)

        self.map_plot_button = Button(plotframe, text="Map Plot", command=self.map_plot)
        self.map_plot_button.grid(row=0, column=0)

        self.stack_plot_button = Button(plotframe, text="Stack Plot", command=self.stack_plot)
        self.stack_plot_button.grid(row=0, column=1)

        #self.quit_button = Button(plotframe, text="Quit", command=master.quit)
        #self.quit_button.grid(row=0, column=2)

        #if self.m:
        #    self.statList = self.m.stacks[0].stackdb.columns.values

        # list of maps
        listheight = 10
        self.mapListTitle = Label(master, text="Maps")
        self.mapListTitle.grid(row=2, column=0)
        self.maplist = Listbox(master,height=listheight,exportselection=0)
        self.maplist.grid(row=3, column=0)
        #self.maplist.insert(END, m.name)
        self.maplist.bind('<Double-1>', self.map_plot0)

        # list of session (fill in on map selection)
        self.sessListTitle = Label(master, text="Sessions")
        self.sessListTitle.grid(row=2, column=1)
        self.sessList = Listbox(master,height=listheight,exportselection=0)
        self.sessList.grid(row=3, column=1)

        # list of segments
        self.segListTitle = Label(master, text="Segments")
        self.segListTitle.grid(row=2, column=2)
        self.segList = Listbox(master,height=listheight,exportselection=0)
        self.segList.grid(row=3, column=2)
        self.segList.insert(END, 'All')
        #for item in range(self.m[0].stacks[0].numSegments):
        #    self.segList.insert(END, item)

        listheight = 20

        self.yListTitle = Label(master, text="Y Stat")
        self.yListTitle.grid(row=4, column=0)
        self.ylistbox = Listbox(master,height=listheight,exportselection=0)
        self.ylistbox.grid(row=5, column=0)

        self.xListTitle = Label(master, text="X Stat")
        self.xListTitle.grid(row=4, column=1)
        self.xlistbox = Listbox(master,height=listheight,exportselection=0)
        self.xlistbox.grid(row=5, column=1)

        #for i,item in enumerate(self.statList):
        #    itemStr = str(i) + '\t' + item
        #    self.ylistbox.insert(END, itemStr)
        #    self.xlistbox.insert(END, itemStr)

        
    def load_dir(self):
        print 'load_dir()'
        path = tkFileDialog.askdirectory(initialdir=self.defaultPath,
                                            title = "Select file")
        # path does not have trailing '/'
        print '\tpath:', path

        maps = mmMapPool(path)
        for map in maps.maps:
            self.m.append(map)

    def load_map(self,path):
        print 'load_map()'

        if path:
            pass
        else:
            path = tkFileDialog.askopenfilename(initialdir=self.defaultPath,
                                            title = "Select file",
                                            filetypes = (("txt files","*.txt"),("all files","*.*")))
        print '\tpath:', path
        m = mmMap(filePath=path)
        self.m.append(m)

        self.refreshinterface(0)

        '''
        self.maplist.insert(END, m.name)

        for item in range(self.m[0].numSessions):
            self.sessList.insert(END, item)

        for item in range(self.m[0].stacks[0].numSegments):
            self.segList.insert(END, item)
        '''

    def load_stack(self):
        mapIdx = 0
        theChannel = 2

        sess = self.sessList.curselection()[0]

        self.m[mapIdx].stacks[sess].loadStackImages(theChannel)

        segmentID = self.getUserSelection('segmentID')

        #plot
        sp = mmStackPlot(self.m[mapIdx].stacks[sess])
        sp.plotStack(self.master, segmentID=segmentID)

    def refreshinterface(self,mapIdx):
        #map
        for map in self.m:
            self.maplist.insert(END, map.name)
        self.maplist.select_set(0)

        #session
        for item in range(self.m[mapIdx].numSessions):
            self.sessList.insert(END, item)
        self.sessList.select_set(0)

        #segments
        for item in range(self.m[mapIdx].stacks[0].numSegments):
            self.segList.insert(END, item)
        self.segList.select_set(0)

        #stats
        if self.m:
            self.statList = self.m[0].stacks[0].stackdb.columns.values

        for i,item in enumerate(self.statList):
            itemStr = str(i) + '\t' + item
            self.ylistbox.insert(END, itemStr)
            self.xlistbox.insert(END, itemStr)
        self.ylistbox.select_set(3)
        self.xlistbox.select_set(2)

    def getUserSelection(self,type):
        segmentID = []
        if type == 'segmentID':
            segmentItem = self.segList.curselection()[0]
            segmentID_str = self.segList.get(segmentItem)
            if segmentID_str == 'All':
                segmentID = []
            else:
                segmentID = [segmentID_str]
        return segmentID

    def map_plot0(self, event):
        print 'map_plot0'
        p = mmMapPlot(self.master, self.m[0])
        segmentID = self.getUserSelection('segmentID')
        p.plot('mapSession', 'pDist', segmentID=segmentID)

    def map_plot(self):
        ySelection = ''
        xSelection = ''
        print 'MyFirstGUI.map_plot()'
        for yitem in self.ylistbox.curselection():
            print 'yStat:', self.statList[yitem]
            ySelection = self.statList[yitem]
        for xitem in self.xlistbox.curselection():
            print 'xStat:', self.statList[xitem]
            xSelection = self.statList[xitem]

        segmentID = self.getUserSelection('segmentID')

        yitem = self.ylistbox.curselection()
        xitem = self.xlistbox.curselection()
        if xSelection and ySelection:
            p = mmMapPlot(self.master, self.m[0])
            p.plot(xSelection,ySelection,segmentID=segmentID)
        else:
            print 'please select and x and y stat'

    def stack_plot(self):
        print 'MyFirstGUI.stack_plot()'
        yitem = self.ylistbox.curselection()
        ystat = self.statList[yitem]
        xitem = self.xlistbox.curselection()
        xstat = self.statList[xitem]
        sess = self.sessList.curselection()[0]
        segmentID = self.getUserSelection('segmentID')
        sp = mmStackPlot(self.m[0].stacks[sess])
        sp.plot(ystat, xstat, roiType='spineROI', segmentID=segmentID)

if __name__ == '__main__':
    root = Tk()
    my_gui = MyFirstGUI(root)

    defaultMap = '/Users/cudmore/Desktop/data/rr30a/rr30a.txt'
    if os.path.isfile(defaultMap):
        my_gui.load_map(path=defaultMap)
    else:
        print 'error: main() did not load default map:', defaultMap

    plt.ion()

    root.mainloop()
