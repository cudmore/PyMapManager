'''
Author: Robert H Cudmore
Date: 20211023

Load bil .tif images and .txt files. Provide function to slice 3D stacks once loaded.

ToDo: Add a flask (or fast api) wrapper

'''

import os
import requests
import io
import json
#import numpy as np
import pandas as pd  # to load .txt files into dataframe
import tifffile  # to load tif files from requests response 'content'
from bs4 import BeautifulSoup  # used to parse html response from bil

class bilLoader():
    def __init__(self, bilID : str, loadFrom = 'remote'):
        # check we have a 16-digit ID
        if len(bilID) != 16:
            #logger.error()
            print('error: bil id must be 16-digits.')

        self._bilUrl = 'https://download.brainimagelibrary.org'
        self._bilID = bilID
        self._loadFrom = loadFrom
    
    
    @property
    def bilUrl(self):
        """
        Return base bil url.
        Usually is https://download.brainimagelibrary.org
        """
        return self._bilUrl

    @property
    def bilID(self):
        """
        Return 16-digit bil id.
        """
        return self._bilID

    @property
    def bilPath(self):
        return self._getPathFromID(self.bilID)
        
    def getRootFolders(self):
        """
        Return a list of folder names associated with a bil ID
        """
        folder = self.bilPath  # /ab/cd/
        folder = self._urljoin(folder, self.bilID)
        return self._getLinks(folder)
    
    def getFilesAndFolders(self, folder: str):
        """
        Return a list of file and folder names.
        Folders will end in '/'
        """
        fullFolder = self.bilPath  # /ab/cd/
        fullFolder = self._urljoin(fullFolder, self.bilID)
        fullFolder = self._urljoin(fullFolder, folder)
        return self._getLinks(fullFolder)
    
    def getAllObjects(self):
        """
        Get the names of all objects from a bil id
        
        Returns:
            A list of (dict, str), if str then it is usally the filename
                If an entry is a dist then it is a recursive list of filename
        """
        folderDict = {}
        rootFolderList = self.getRootFolders()
        for rootFolder in rootFolderList:
            folderDict[rootFolder] = []
            objList = self.getFilesAndFolders(rootFolder)
            for obj in objList:
                if obj.endswith('/'):
                    innerFolder = self._urljoin(rootFolder, obj)
                    recursiveObj = self.getFilesAndFolders(innerFolder)
                    recursiveDict = {}
                    recursiveDict[innerFolder] = recursiveObj
                    folderDict[rootFolder].append(recursiveDict)
                else:
                    folderDict[rootFolder].append(obj)

        #
        return folderDict

    def _getPathFromID(self, id: str):
        """
        Get /ab/cd/ path from first 4-digits of 16-digit bilID abcdxxxxxxxxxxxx
        """
        firstDir = id[0:2]
        secondDir = id[2:4]
        thepath = self._urljoin(firstDir, secondDir)
        return thepath

    def _urlFromFolder(self, folder: str):
        return self._urljoin(self.bilUrl, folder)

    def _getLinks(self, folder, verbose=False):
        """
        Get a list of <A HREF> links from bil (e.g. a list of files in url).
        
        Args:
            folder (str): url folder postfix like /ab/cd/
        
        Returns:
            List of objects, each object i either a folder or a file.
                Folders end in '/'
        """

        url = self._urlFromFolder(folder)
        
        if verbose:
            print('_getLinks() url:', url)

        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')

        # always ignore some links
        ignoreList = ['./', '../']

        # specific to cudmore data
        ignoreTuple = ('.finished', '.master')
 
        fileList = []

        linkList = soup.find_all('a')
        for link in linkList:
            # link is type <class 'bs4.element.Tag'>
            href = link.get('href')
            if href in ignoreList:
                continue

            # specific to cudmore data
            if href.endswith(ignoreTuple):
                continue

            fileList.append(href)
        #
        return fileList

    def _urljoin(self, *args):
        """
        Joins given arguments into an url. Trailing but not leading slashes are
        stripped for each argument.
        """

        return "/".join(map(lambda x: str(x).rstrip('/'), args))

    def _old_printResp(self, r):
        """
        Print out a requests response
        """
        print(f'  status_code: {r.status_code}')
        
        # text will often be raw html, parse with BeautifulSoup
        #print(f'  text: {r.text}')
        
        print(f'  encoding: {r.encoding}')
        print(f"  headers['content-type']: {r.headers['content-type']}")
        
        print('    fetching content ...')
        content = r.content
        print('    ... got content')
        
        print(f'  len(content): {len(content)}')
        print(f'  type(content): {type(content)}')

if __name__ == '__main__':
    bilID = 'd901fb2108458eca'
    bl = bilLoader(bilID)
    print('bilID:', bl.bilID)
    print('bilPath:', bl.bilPath)

    #rootFolders = bl.getRootFolders()
    #print('getRootFolders():', rootFolders)
    
    objDict = bl.getAllObjects()
    print('objDict:')
    print(json.dumps(objDict, indent=4))
    
    # parse the results and plot a line
