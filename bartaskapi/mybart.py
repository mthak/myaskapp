#!/usr/bin/env python
import json
import xmltodict
import json
import requests

def getSchedule(source,dest):
    '''params = requests.get_json()
    source = params['source'].strip()
    dest = params['dest'].strip()'''
    print "source and destination is " , source,dest
    result = []
    newdata = {}
    key="MW9S-E7SL-26DU-VV8V"
    apiurl = "http://api.bart.gov/api/etd.aspx?cmd=etd&orig="+source+"&key="+key
    xmldata = requests.get(apiurl)
    if xmldata.status_code == 200:
       data  = xmldata.content
       mydict = xmltodict.parse(data)
       print json.dumps(mydict,indent=4)
    else:
        raise Exception("Sorry Bart API is not reachable")

    stationinfo = mydict['root']['station']
    destinationinfo = mydict['root']['station']['etd']
    if type(destinationinfo) != list:
       destinationinfo = [ destinationinfo ] 
    for alldestinations in destinationinfo:
        query = False
	for key,value in alldestinations.items():
            if value == dest:
                print "Found it"
                print key,value
                query = True
            if key == "estimate" and query:
	       for data in value:
                   time = data['minutes']
                   sttime = "next train in " + time + "minutes"
                   result.append(sttime)
                   print data['minutes']
               newdata['time'] = str(result)
               print newdata
    return  json.dumps(newdata)
