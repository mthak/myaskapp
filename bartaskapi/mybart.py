#!/usr/bin/env python
import json
import xmltodict
import json
import requests

def validate_dest(stn,stnlist):
   stnname = [lambda x: x['name'] for x in stnlist]
   if stn not in stname:
      return None
   else:
      return stn
def validate_stn(stnname,stnlist):
    stnabbr = [lambda x: x['abbr'] for x in stnlist]
    stndict ={}
    for items in stnlist:
        name = items['name'].lower()
        stndict[name] = items['abbr']
    if stnname not in stnabbr:
       stnname = stnname.lower()
       try: 
          retstn = stndict[stnname]
       except KeyError,e:
         retstn = None
    else:
       retstn = stnname
    return retstn
 
def getSchedule(source,dest):
    stns = requests.get("http://bart.crudworks.org/api/stations")     
    stnlist = json.loads(stns.content)
    print "source and destination is " , source,dest
    source = validate_stn(source,stnlist)
    if not source:
       return [" Invalid Source Station , Please pick a valid station"]
    dest = validate_stn(dest,stnlist)
    if not dest:
       return ["Invalid destination"]
    print "station validate" , source
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
        result = ["Sorry Bart API is not reachable"]
        return result
    try:
       stationinfo = mydict['root']['station']
    except KeyError,e:
       return ["Root for Station not Found"]
    try:
       destinationinfo = mydict['root']['station']['etd']
    except KeyError:
       return ["No train available for the given stations now"]
    if type(destinationinfo) != list:
       destinationinfo = [ destinationinfo ] 
    found = False
    for alldestinations in destinationinfo:
        query = False
	for key,value in alldestinations.items():
            if value == dest:
                print "Found it"
                print key,value
                query = True
                found = True
            if key == "estimate" and query:
	       for data in value:
                   time = data['minutes']
                   if "Leaving" not in time:
                       sttime = "next train in " + time + "minutes"
                   else: 
                       sttime = "next train Leaving now"
                   result.append(sttime)
                   print data['minutes']
               newdata['time'] = str(result)
        
    if not found:
       result = ["No train available from Source to Destination"]
    return  result

# my test playground 
#ret = getSchedule("Colim","Walnut Creek")
#print ret
