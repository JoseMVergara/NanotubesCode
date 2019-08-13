#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Author: @JoseMVergara

'''
Program that Convert files that are in the same folder that the script with ".bands" extension to ".dat"  
How to use:
	$python ConvertBands.py
outputs:
Note: here 'File' is the name of the ".bands" file. example: if BPNT1414.bands File = BPNT1414

	File.dat 

'''

import os

def FindFilenames(pathToDir, suffix): 
	"""Search all the .out files found in a directory.

		input: Folder where the files are
		output: list of all files found out"""
	filenames = os.listdir(pathToDir) 
	filenamesWithSuffix = [ filename for filename in filenames if filename.endswith(suffix) ] 	
	filenamesWithoutSuffix = []
	for filename in filenamesWithSuffix:
		filenamesWithoutSuffix += [filename.split('.')[0]]

	return filenamesWithoutSuffix

def ConvertBandsToDat(gnubandsPath,bandsFile):
	"""
	Convert ".bands" file to ".dat" file.
	
	input: ".bands" file.
	output: ".dat" file.
	"""

	os.system(gnubandsPath+'gnubands-new -F < '+bandsFile+'.bands > '+bandsFile+'.dat')

files = FindFilenames('./',".bands")
for bandsFile in files:
	ConvertBandsToDat('/export/apps/',bandsFile)




