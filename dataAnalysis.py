import json
from pprint import pprint
from dateutil import parser
import matplotlib.pyplot as plt
import numpy as np
import math

acceptableError = 0.001

def getTime(dataTuple):
	return parser.parse(dataTuple[seriesColumns.index("time")])

def getUsageIdle(dataTuple):
	return float(dataTuple[seriesColumns.index("usage_idle")])

def getUsageIOWait(dataTuple):
	return float(dataTuple[seriesColumns.index("usage_iowait")])

def getUsageIRQ(dataTuple):
	return float(dataTuple[seriesColumns.index("usage_irq")])

def getUsageNice(dataTuple):
	return float(dataTuple[seriesColumns.index("usage_nice")])

def getUsageSoftIRQ(dataTuple):
	return float(dataTuple[seriesColumns.index("usage_softirq")])

def getUsageSteal(dataTuple):
	return float(dataTuple[seriesColumns.index("usage_steal")])

def getUsageSystem(dataTuple):
	return float(dataTuple[seriesColumns.index("usage_system")])

def getUsageUser(dataTuple):
	return float(dataTuple[seriesColumns.index("usage_user")])

def getTotalMemUsage(dataTuple):
	return  getUsageIdle(dataTuple) + \
			getUsageIOWait(dataTuple) + \
			getUsageIRQ(dataTuple) + \
			getUsageNice(dataTuple) + \
			getUsageSoftIRQ(dataTuple) + \
			getUsageSteal(dataTuple) + \
			getUsageSystem(dataTuple) + \
			getUsageUser(dataTuple)


# rangeMin is the slot in minutes to plot the data
def plotDataOverRange(rangeMin, getterFunc, ylabel, xlabel, legendLabel):
	data = {}
	for x in seriesValues:
		timeMins = str(int((getTime(x) - startTime).total_seconds() / rangeMin))
		if timeMins in data:
			data[timeMins].append(getterFunc(x))
		else:
			data[timeMins] = [getterFunc(x)]

	X = [int(x) * rangeMin / 60 for x in data]
	XSort = X.sort()
	dataMax = [max(data[x]) for x in data]
	dataMax.sort(key=dict(zip(X, dataMax)).get)
	dataMin = [min(data[x]) for x in data]
	dataMin.sort(key=dict(zip(X, dataMin)).get)
	dataMean = [np.mean(data[x]) for x in data]
	dataMean.sort(key=dict(zip(X, dataMean)).get)

	plt.plot(X, dataMax, color='blue', label=legendLabel + " MAX")
	plt.plot(X, dataMin, color='green', label=legendLabel + " MIN")
	plt.plot(X, dataMean, color='brown', label=legendLabel + " MEAN")
	plt.ylabel(ylabel)
	plt.xlabel(xlabel)
	plt.legend(loc='lower right')
	plt.xlim((0, max(X)))
	plt.show()



with open('cpu.json') as data_file:    
    data = json.load(data_file)

seriesName = data['results'][0]['series'][0]['name']
seriesColumns = data['results'][0]['series'][0]['columns']
seriesValues = data['results'][0]['series'][0]['values']

incorrectValues = filter(lambda x: not (abs(100.0 - getTotalMemUsage(x)) < acceptableError), seriesValues)
# there are none
print "There are " + str(len(incorrectValues)) + " incorrect values"

# collect all timestamps from the values
startTime = min([getTime(x) for x in seriesValues]) # this is time 0

#filter out values which correspond to the timeframe [0-8] hrs 0 being the startime
seriesValues = filter(lambda x:((getTime(x) - startTime).total_seconds() < (8*60*60)), seriesValues)


plotDataOverRange(20*60, getUsageUser, 'Percentage of CPU used for User Applications', 'Time in minutes from start of data collection', 'usage_user')
plotDataOverRange(20*60, getUsageSystem, 'Percentage of CPU used for System / Kernel', 'Time in minutes from start of data collection', 'usage_system')
plotDataOverRange(20*60, getUsageIdle, 'Percentage of CPU used for Idle Process', 'Time in minutes from start of data collection', 'usage_idle')
plotDataOverRange(20*60, getUsageIOWait, 'Percentage of CPU used for IO Wait', 'Time in minutes from start of data collection', 'usage_iowait')

