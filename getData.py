import json
import subprocess

op = subprocess.check_output(['curl', '-G', 'http://172.24.212.30:8086/query?pretty=true', '--data-urlencode', "db=telegraf", '--data-urlencode', "q=SHOW MEASUREMENTS"])
measurementLoL = json.loads(op)['results'][0]['series'][0]['values']
measurement = []
[measurement.extend(x) for x in measurementLoL]
allMeasurements = ','.join(measurement)

op = subprocess.check_output(['curl', '-G', 'http://172.24.212.30:8086/query?pretty=true', '--data-urlencode', "db=telegraf", '--data-urlencode', "q=select * from " + allMeasurements])
file = open('dataAll_Measurements.json','w')
file.write(op)
file.close()

# for measure in measurement:
# 	op = subprocess.check_output(['curl', '-G', 'http://172.24.212.30:8086/query?pretty=true', '--data-urlencode', "db=telegraf", '--data-urlencode', "q=select * from " + measure])
# 	file = open('data/' + measure + '.json','w')
# 	file.write(op)
# 	file.close()