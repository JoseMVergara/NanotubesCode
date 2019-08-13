#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Author: @JoseMVergara

'''
Program that plots files with ".dat" and ".DOS" extension that are in the same folder of the script
How to use:
	$python Graph.py
outputs:
Note: here 'File' is the name of the ".dat" or ".DOS" file. example: if BPNT1414.bands File = BPNT1414

	'plots' directory that containts all ".dat"  and ".DOS" plots 

'''
import os
import numpy as np
import matplotlib.pyplot as plt
from itertools import dropwhile,takewhile 
import seaborn as sns; sns.set() 

def NotBlockStart(line):
	return not line.startswith('\n')

def NotBlockEnd(line):
	return not line.startswith('\n')

def GetBands(file):
	try:	
		blockBand = dropwhile(NotBlockStart,file)
		next(blockBand)
		block=list(takewhile(NotBlockEnd,blockBand))
		return block
	except StopIteration:
		return False

def FindFilenames(pathToDir, suffix): 
	"""Search all the ."suffix" files found in a directory.

		input: Folder where the files are
		output: list of all files found """
	filenames = os.listdir(pathToDir) 
	filenamesWithSuffix = [ filename for filename in filenames if filename.endswith(suffix) ] 	
	filenamesWithoutSuffix = []
	for filename in filenamesWithSuffix:
		filenamesWithoutSuffix += [filename.split('.')[0]]

	return filenamesWithoutSuffix

def GraphBands(datFile):
	with open(datFile) as file:
		bands = []
		while True:
			block = GetBands(file)
			if block is not False:
				bands += [block]
			else:
				break
	bandsToPlot = np.array([])
	for band in bands:
		x = []
		y = []
		for line in band:
			splitBand = np.array(line.split(),dtype=float)
			x += [splitBand[0]]
			y += [splitBand[1]]
		plt.plot(x,y)

	plt.title('Band Structure of '+filename)
	plt.ylim(-2.5,2.5)
	plt.savefig('Plots/'+filename+'.dat.png',dpi=300)
	plt.close()

def GraphDOS(DOSFile):
	with open(DOSFile) as file:
		x = []
		y = []
		for line in file:
			DOSLine = np.array(line.split()[0:-1],dtype=float)
			x+=[DOSLine[0]]
			y+=[DOSLine[1]]
	plt.plot(x,y, '-r')
	plt.title('DOS '+filename)
	plt.savefig('Plots/'+filename+'.DOS.png',dpi=300)
	plt.close()


def GraphFile(filename):

	print('=======================================')
	print('Graphing '+filename+'..................')
	datFile = filename + '.dat'
	DOSFile = filename + '.DOS' 
			
	GraphBands(datFile)	
	GraphDOS(DOSFile)
	return 


files=FindFilenames('./','.dat')
os.system('mkdir Plots')
for filename in files:
	bands = GraphFile(filename)
	











