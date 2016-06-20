import json
import subprocess
from pprint import pprint
from dateutil import parser
import matplotlib.pyplot as plt
import numpy as np
from scipy.cluster.vq import *
import math

# #################################################################

# 						HELPERS

# #################################################################

def getValueFor(dataTuple, seriesColumns, valueHeader):
	return float(dataTuple[seriesColumns.index(valueHeader)])

def getTime(dataTuple, seriesColumns=["time"]):
	index = dataTuple[seriesColumns.index("time")]
	return parser.parse(index)

def getMaxEntries(measurementData):
	return max([ len(machine['values']) for machine in measurementData ])

def getValuesForMachine(data, machineID, maxLen, skipValuesFirst, skipValuesLast):
	for machine in data:
		if machine['tags']['host'] == machineID:
			#values should not contain the timestamp
			values = [ [float(x) for x in dataTuple[skipValuesFirst:len(dataTuple)-skipValuesLast]] for dataTuple in machine['values']]
			means = [np.mean(x) for x in np.asarray(values).T.tolist()]
			return sum(values, []) + (maxLen - len(values)) * means
	raise Exception('INCORRECT MACHINE ID')

def aggregateData(allData, machineIDs):
	maxLens = [getMaxEntries(data) for data in allData]
	print maxLens
	aggregatedData = []
	for machineID in machineIDs:
		aggregatedData.append(
			getValuesForMachine(allData[0], machineID, maxLens[0], 1, 0) +
			getValuesForMachine(allData[1], machineID, maxLens[1], 1, 0) +
			getValuesForMachine(allData[2], machineID, maxLens[2], 2, 1))
	return aggregatedData

def preProcess(dataForMachines, maxLen):
	return [sum(dataForMachines[machineID]['values'], []) + (maxLen - len(dataForMachines[machineID]['values'])) * dataForMachines[machineID]['means'] for machineID in dataForMachines]

def getDistinctMachineIDs(allData):
	return reduce(
		(lambda x,y: set.union(x, y)), 
		[set([machine['tags']['host'] for machine in measurementData])  for measurementData in allData])

def getMaxOverColumns(machineData, columnNames, column):
	lenData = len(columnNames)
	segmentedData = [machineData[x:x+lenData] for x in range(0,len(machineData),lenData)]
	data = np.asarray(segmentedData).T.tolist()
	maxVal = max(data[columnNames.index(column)])
	maxIndex = data[columnNames.index(column)].index(maxVal)
	return maxVal, segmentedData[maxIndex]


def plotterForIndividualMachines(valueHeader, values, columns, xlabel, ylabel, legendLabel, valueRanges=['MAX','MIN','MEAN'], show=True, lineStyle='solid'):

	machineStartTime = min([getTime(x, columns) for x in values])
	X = [int(float((getTime(x, columns) - machineStartTime).total_seconds()) / 20) for x in values]
	colorForPlots =  {
		'MAX': 'blue',
		'MIN': 'green',
		'MEAN': 'brown'
	}
	data = {}
	for rangeVal in valueRanges:
		data[rangeVal] = [getValueFor(x, columns, rangeVal.lower() + '_' + valueHeader) for x in values]

	for dataset in data:
		plt.plot(X, data[dataset], color=colorForPlots[dataset], linestyle=lineStyle, label=legendLabel + " " + dataset)

	plt.ylabel(ylabel)
	plt.xlabel(xlabel)
	plt.xlim((0, max(X)))
	plt.ylim((0, 120))
	if (show):
		plt.legend(loc='lower right')
		plt.show()


# #################################################################

def getDataForLastDayFromRestAPI(starTime, endTime):
	queryCommand = ['curl', 
		'-G', 
		'http://172.24.212.30:8086/query?pretty=true', 
		'--data-urlencode', "db=telegraf", 
		'--data-urlencode', 
		"q=SELECT * from downsampled_cpu WHERE time >= "+ starTime +" AND time <=  "+ endTime +" GROUP BY host"]
	print " ".join(queryCommand)
	op = subprocess.check_output(queryCommand)
	with open ('data/allDataCPU.json', 'w') as opFile:
		opFile.write(op)
	return (json.loads(op)['results'][0]['series'])

def getDataFromFile(fileName):
	with open(fileName) as data_file:
		return json.load(data_file)['results'][0]['series']

###################################################################

allData = [getDataFromFile('data/allDataCPU.json'),
           getDataFromFile('data/allDataMEM.json'),
           getDataFromFile('data/allDataDISK.json')]

machineIDs = getDistinctMachineIDs(allData)
dataSet = aggregateData(allData, machineIDs)
result, groups = kmeans2(np.array(dataSet), 3)
print groups

columnNames = allData[0][0]['columns'][1:] + allData[1][0]['columns'][1:] + allData[2][0]['columns'][2:len(allData[2][0]['columns'])-1]

for column in columnNames:
	plt.figure()
	for index in range(0,len(dataSet)):
		Y , otherValues = getMaxOverColumns(dataSet[index], columnNames, 'max_user')
		X = otherValues[columnNames.index(column)]
		plt.scatter(X,Y,color=['blue', 'green', 'brown'][groups[index]])

	plt.ylabel('Max CPU Usage by User Applications')
	plt.xlabel(column)
	plt.savefig('data/figs/' + column + '.png')
	plt.show()
	plt.close()
