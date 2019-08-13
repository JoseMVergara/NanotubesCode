#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Author: @JMVergara

'''
Program that extract necessary information and automatize processes from SIESTA software outputs.

The program do the process for all files with ".out" extension that are in the same folder of the script

How to use:
	$python Check.py

outputs:
Note: here 'File' is the name of the ".out" file. example: if BPNT1414.out File = BPNT1414

	Status.csv file: Show iformation about the correct termination of job in SIESTA: OK, FAILED
	File-R.fdf file: replace relaxed coordinates in fdf input file for future calculations  
'''

import os
import pandas as pd
from itertools import dropwhile,takewhile   
 
def NotBlockStartRelaxedCoor(line):
    return not line.startswith('outcoor: Relaxed atomic coordinates (Ang):')

def NotBlockStartUnRelaxedCoor(line):
    return not line.startswith('outcoor: Final (unrelaxed) atomic coordinates (Ang):')

def NotBlockStartUnitCell(line):
	return not line.startswith('outcell: Unit cell vectors (Ang):')

def NotBlockEnd(line):
	return not line.startswith('\n')

def NotBlockStartInputCoordinates(line):
	return not line.startswith('%block AtomicCoordinatesAndAtomicSpecies')

def NotBlockInputEnd(line):
	return not line.startswith('%endblock AtomicCoordinatesAndAtomicSpecies')

def NotBlockStartInputUnit(line):
	return not line.startswith('%block LatticeVectors')

def NotBlockUnitCellEnd(line):
	return not line.startswith('%endblock LatticeVectors')

def WriteLines(lines,outputFile):
	'''Write lines in outputfile
	input: 
		lines = lines of text or numbers that you want to write
		outputFile = file where the lines will be written'''

	for line in lines:
		outputFile.write(line)

def WriteFindCoorFile(data):
	blockInputCoor = dropwhile(NotBlockStartInputCoordinates, data)
	next(blockInputCoor)
	block=list(takewhile(NotBlockInputEnd, blockInputCoor))
	findFile = open('findCoor.txt',"w")
	WriteLines(block,findFile)

def WriteFindUnitFile(data):   
	blockUnitCell = dropwhile(NotBlockStartInputUnit, data)
	next(blockUnitCell)
	block=list(takewhile(NotBlockUnitCellEnd, blockUnitCell))
	findFile = open('findUnit.txt',"w")
	WriteLines(block,findFile)
	

def GetInputInfo(inputFile,valueToObtain):
	with open(inputFile) as inputFile:
		inputLines = iter(inputFile)
		while True:
			inputLine = next(inputLines)
			if inputLine.startswith(valueToObtain,0,50):
				result = inputLine
				break
	return inputLine

def GetRelaxedCoor(file):
    blockRelaxedCoor = dropwhile(NotBlockStartRelaxedCoor, file)
    next(blockRelaxedCoor)
    block=list(takewhile(NotBlockEnd, blockRelaxedCoor))
    replaceFile = open('replaceCoor.txt',"w")
    WriteLines(block,replaceFile)

def GetUnRelaxedCoor(file):
	blockUnRelaxedCoor = dropwhile(NotBlockStartUnRelaxedCoor, file)
	next(blockUnRelaxedCoor)
	block=list(takewhile(NotBlockEnd, blockUnRelaxedCoor))
	replaceFile = open('replaceCoor.txt',"w")
	WriteLines(block,replaceFile)

def GetUnitCell(file):
	blockUnitCell = dropwhile(NotBlockStartUnitCell, file)
	next(blockUnitCell)
	block=list(takewhile(NotBlockEnd, blockUnitCell))
	replaceFile = open('replaceUnit.txt',"w")
	WriteLines(block,replaceFile)

def CheckScf(inputFile,file):
	lines = iter(file)
	while True:
		try:
			line = next(lines)
		except:
			break
		if line.startswith( 'SCF cycle converged after', 0, 30 ):
			lastScf = line
	splitLastScf = lastScf.split(' ')
	try:
		numIter = int(splitLastScf[7])
	except:
		numIter = int(splitLastScf[6])
	maxSCF = GetInputInfo(inputFile,'MaxSCFIterations').split('\n')
	maxSCF = int(maxSCF[0].split(' ')[-1])

	if numIter < maxSCF:
		status = True
	else:
		status = False

	return status

def CheckMaxForceTol(inputFile,file):
	lines = iter(file)
	while True:
		try:
			line = next(lines)
		except:
			break
		if line.startswith( 'Max', 3, 30 ):
			lastForceTol = line
	splitLastForceTol = lastForceTol.split(' ')
	numLastForceTol = float(splitLastForceTol[7])

	maxForceTol = GetInputInfo(inputFile,'MD.MaxForceTol').split('\n')
	maxForceTol = float(maxForceTol[0].split(' ')[4])

	if numLastForceTol < maxForceTol:
		status =  True 
	else:
		status = False

	return status

def CheckCGsteps(inputFile,file):
	lines = iter(file)
	while True:
		try:
			line = next(lines)
		except:
			break
		if line.startswith( 'Begin FIRE opt. move', 24, 50 ):
			lastCGsteps = line
	splitCGsteps = lastCGsteps.split('\n')
	splitCGsteps = splitCGsteps[0].split(' ')
	numCGsteps = int(splitCGsteps[-1])

	maxCGsteps = GetInputInfo(inputFile,'MD.NumCGsteps').split('\n')
	maxCGsteps = int(maxCGsteps[0].split(' ')[-1])

	if numCGsteps < maxCGsteps:
		status = True
	else:
		status = True

	return status

def GetTotalEnergy(file):
	lines = iter(file)
	while True:
		try:
			line = next(lines)
		except:
			break
		if line.startswith( 'Total', 16, 50 ):
			totalEnergy = line
	split = totalEnergy.split('\n')
	totalEnergy = float(split[0].split(' ')[-1])
	return totalEnergy

def FindFilenames(pathToDir, suffix=".out"): 
	"""Search all the .out files found in a directory.

		input: Folder where the files are
		output: list of all files found out"""
	filenames = os.listdir(pathToDir) 
	filenamesWithSuffix = [ filename for filename in filenames if filename.endswith(suffix) ] 	
	filenamesWithoutSuffix = []
	for filename in filenamesWithSuffix:
		filenamesWithoutSuffix += [filename.split('.')[0]]

	return filenamesWithoutSuffix

def ReplaceCoordinatesInputFile(inputFile,RelaxFile):
	RelaxFiletemp = RelaxFile+"tmp.fdf"
	RelaxFile = RelaxFile+"-R.fdf"
	with open(inputFile) as data:
		WriteFindCoorFile(data)
	with open(inputFile) as data:
		WriteFindUnitFile(data)

	findLines = open('findCoor.txt').read().split('\n')
	replaceLines = open('replaceCoor.txt').read().split('\n')
	findReplace = dict(zip(findLines, replaceLines))
	with open(inputFile) as data:
		with open(RelaxFiletemp,"w") as newData:
			for line in data:
				for key in findReplace:
					if key in line:
						line = line.replace(key, findReplace[key])
				newData.write(line)

	findLines = open('findUnit.txt').read().split('\n')
	replaceLines = open('replaceUnit.txt').read().split('\n')
	findReplace = dict(zip(findLines, replaceLines))
	with open(RelaxFiletemp) as data:
		with open(RelaxFile,"w") as newData:
			for line in data:
				for key in findReplace:
					if key in line:
						line = line.replace(key, findReplace[key])
				newData.write(line)
	
def GetTypeFile(outputfile):
	maxCGsteps = GetInputInfo(outputfile,'MD.NumCGsteps').split('\n')
	maxCGsteps = int(maxCGsteps[0].split(' ')[-1])
	if maxCGsteps > 0:
		typeFile = 'Relaxed'
	else:
		typeFile = 'Result'
	return typeFile

def CheckIfFileIsEmpty(path):
	try:
		return os.stat(path).st_size==0
	except:
		return True

def GetFerminEnergy(file):
	lines = iter(file)
	while True:
		try:
			line = next(lines)
		except:
			break
		if line.startswith( '   scf:', 0, 7 ):
			lastScf = line
	splitLastScf = lastScf.split(' ')[-1]
	ferminEnergy = splitLastScf.split('\n')[0]
	return ferminEnergy
	
def CheckFile(filename):

	print('=======================================')
	print('Checking '+filename+'..................')
	outputFile = filename + '.out'
	inputFile = filename + '.fdf' 
	typeFile = GetTypeFile(outputFile)
	if typeFile == 'Relaxed':		
		with open(outputFile) as file:
			totalEnergy = GetTotalEnergy(file)
		with open(outputFile) as file:
			statusCG = CheckCGsteps(inputFile,file)
		with open(outputFile) as file:
			statusForceTol = CheckMaxForceTol(inputFile,file)
		with open(outputFile) as file:
			statusScf = CheckScf(inputFile,file)
		with open(outputFile) as file:
			GetUnitCell(file)
		flag = False
		with open(outputFile) as file:
			try:
				GetRelaxedCoor(file)
			except StopIteration:
				flag = True
		if flag == True:
			with open(outputFile) as file:
				GetUnRelaxedCoor(file)
		statusList = [statusCG,statusForceTol,statusScf]
		if False in statusList:
			fileStatus = 'FAILED'
		else:
			fileStatus = 'OK'
	
		info = [filename,totalEnergy,fileStatus,'NA']
		ReplaceCoordinatesInputFile(inputFile,filename)

		os.remove('findCoor.txt')
		os.remove('replaceCoor.txt')	
		os.remove('findUnit.txt')
		os.remove('replaceUnit.txt')
		os.remove(filename+"tmp.fdf")
	else:
		filenameAux = filename.split('-R')[0]
		bandsFile = filenameAux + '.dat'
		DOSFile = filenameAux + '.DOS'
		with open(outputFile) as file:
			totalEnergy = GetTotalEnergy(file)

		with open(outputFile) as file:
			ferminEnergy = GetFerminEnergy(file)
		if CheckIfFileIsEmpty(bandsFile) == False and CheckIfFileIsEmpty(DOSFile) == False:
			fileStatus='OK'
		else:
			fileStatus='False'
			
		info = [filename,totalEnergy,fileStatus,ferminEnergy]

	return info	




filenames = FindFilenames('./')
Data = []
for filename in filenames:
	info = CheckFile(filename)
	Data += [info]

infoFile = pd.DataFrame(Data,columns=['System','TotalEnergy','Status','FerminEnergy'])
infoFile.to_csv("Status.csv")
