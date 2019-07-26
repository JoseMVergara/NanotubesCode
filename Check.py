#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Author: @JMVergara

import os
from itertools import dropwhile,takewhile   
 
def NotBlockStartRelaxedCoor(line):
    return not line.startswith('outcoor: Relaxed atomic coordinates (Ang):')

def NotBlockStartUnRelaxedCoor(line):
    return not line.startswith('outcoor: Final (unrelaxed) atomic coordinates (Ang):')

def NotBlockStartUnitCell(line):
	return not line.startswith('outcell: Unit cell vectors (Ang):')

def NotBlockEnd(line):
	return not line.startswith('\n')

def WriteLines(lines,outputFile):
	for line in lines:
		outputFile.write(line)

def GetInputInfo(inputFile,valueToObtain):
	with open(inputFile) as inputFile:
		inputLines = iter(inputFile)
		while True:
			inputLine = next(inputLines)
			if inputLine.startswith(valueToObtain,0,50):
				result = inputLine
				break
	return inputLine

def GetRelaxedCoor(finalFile,file):
    blockRelaxedCoor = dropwhile(NotBlockStartRelaxedCoor, file)
    next(blockRelaxedCoor)
    block=list(takewhile(NotBlockEnd, blockRelaxedCoor))
    block.insert(0,'outcoor: Relaxed atomic coordinates (Ang):\n')
    block.append('\n')
    WriteLines(block,finalFile)
    print('Getting Relaxed Coordinates.....  Done\n')

def GetUnRelaxedCoor(finalFile,file):
    blockUnRelaxedCoor = dropwhile(NotBlockStartUnRelaxedCoor, file)
    next(blockUnRelaxedCoor)
    block=list(takewhile(NotBlockEnd, blockUnRelaxedCoor))
    block.insert(0,'outcoor: Final (UNRELAXED) atomic coordinates (Ang): \n')
    block.append('\n')
    WriteLines(block,finalFile)
    print('Getting UNRELAXED Coordinates.....  Done\n')

def GetUnitCell(finalFile,file):
	blockUnitCell = dropwhile(NotBlockStartUnitCell, file)
	next(blockUnitCell)
	block=list(takewhile(NotBlockEnd, blockUnitCell))
	del(blockUnitCell)
	block.insert(0,'outcell: Unit cell vectors (Ang):\n')
	block.append('\n')
	WriteLines(block,finalFile)
	print('Getting UnitCell..... Done.\n')

def CheckScf(inputFile,finalFile,file):
	lines = iter(file)
	while True:
		try:
			line = next(lines)
		except:
			break
		if line.startswith( 'SCF cycle converged after', 0, 30 ):
			lastScf = line
	splitLastScf = lastScf.split(' ')	
	numIter = int(splitLastScf[7])
	maxSCF = GetInputInfo(inputFile,'MaxSCFIterations').split('\n')
	maxSCF = int(maxSCF[0].split(' ')[-1])

	if numIter <= maxSCF:
		scfResult = 'SCF cycle converged after %d and Max SCF iterations are %d          CORRECT\n'%(numIter,maxSCF) 
	else:
		scfResult = 'SCF cycle converged after %d and Max SCF iterations are %d          INCORRECT\n'%(numIter,maxSCF)

	WriteLines(list(scfResult),finalFile)
	print('Checking SCF iterations ........ Done.\n')

def CheckMaxForceTol(inputFile,finalFile,file):
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

	if numLastForceTol <= maxForceTol:
		forceTolResult = 'Max constrained converged after %f and Max force tol are %f          CORRECT\n'%(numLastForceTol,maxForceTol) 
	else:
		forceTolResult = 'Max constrained converged after %f and Max force tol are %f          INCORRECT\n'%(numLastForceTol,maxForceTol)

	WriteLines(list(forceTolResult),finalFile)
	print('Checking Force Tol ........ Done.\n')

def CheckCGsteps(inputFile,finalFile,file):
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

	if numCGsteps <= maxCGsteps:
		CGstepsResult = 'Input converged after %d CGsteps and Max CGsteps are %d          CORRECT\n'%(numCGsteps,maxCGsteps) 
	else:
		CGstepsResult = 'Input converged after %d CGsteps and Max CGsteps are %d          INCORRECT\n'%(numCGsteps,maxCGsteps)

	WriteLines(list(CGstepsResult),finalFile)
	print('Checking CGsteps ........ Done.\n')

def GetTotalEnergy(finalFile,file):
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
	result = list("Total Energy      %f\n"%totalEnergy)
	WriteLines(result,finalFile)
	print("Getting Total Energy....... Done.\n")

def FindFilenames(pathToDir, suffix=".out"): 
	"""Buscamos todos los archivos .out que se encuentran en un directorio
		input: Carpeta donde estan los archivos
		output: lista de todos los archivos.out encontrados"""
	filenames = os.listdir(pathToDir) 
	filenamesWithSuffix = [ filename for filename in filenames if filename.endswith(suffix) ] 	
	filenamesWithoutSuffix = []
	for filename in filenamesWithSuffix:
		filenamesWithoutSuffix += [filename.split('.')[0]]

	return filenamesWithoutSuffix

def CheckFile(filename):
	print('=======================================')
	print('Checking '+filename+'..................')
	finalname = filename +'.txt'
	outputFile = filename + '.out'
	inputFile = filename + '.out' 
	finalFile = open(finalname, "w")		
	with open(outputFile) as file:
		GetTotalEnergy(finalFile,file)
	with open(outputFile) as file:
		CheckCGsteps(inputFile,finalFile,file)
	with open(outputFile) as file:
		CheckMaxForceTol(inputFile,finalFile,file)
	with open(outputFile) as file:
		CheckScf(inputFile,finalFile,file)
	with open(outputFile) as file:
		GetUnitCell(finalFile,file)
	flag = False
	with open(outputFile) as file:
		try:
			GetRelaxedCoor(finalFile,file)
		except StopIteration:
			flag = True
	if flag == True:
		with open(outputFile) as file:
			GetUnRelaxedCoor(finalFile,file)

	finalFile.close()

filenames = FindFilenames('./')
for filename in filenames:
	CheckFile(filename)
