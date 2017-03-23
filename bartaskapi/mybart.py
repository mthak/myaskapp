#!/usr/bin/env python
import json
import xmltodict
import json
import requests
import logging

stations = ['12th St. Oakland City Center', '16th St. Mission', '19th St. Oakland', '24th St. Mission', 'Ashby', 'Balboa Park', 'Bay Fair', 'Castro Valley', 'Civic Center', 'Coliseum', 'Colma', 'Concord', 'Daly City', 'Downtown Berkeley', 'Dublin', 'El Cerrito del Norte', 'El Cerrito Plaza', 'Embarcadero', 'Fremont', 'Fruitvale', 'Glen Park', 'Hayward', 'Lafayette', 'Lake Merritt', 'MacArthur', 'Millbrae', 'Montgomery St.', 'North Berkeley', 'North Concord', "Oakland Int'l Airport", 'Orinda', 'Pittsburg Bay Point', 'Pleasant Hill', 'Powell St.', 'Richmond', 'Rockridge', 'San Bruno', "San Francisco Int'l Airport", 'San Leandro', 'South Hayward', 'South San Francisco', 'Union City', 'Walnut Creek', 'West Dublin', 'West Oakland']

def validate_name(stn,stnlist):
   stnname = [ x['name'] for x in stnlist ]
   stfind = False
   for items in stnname:
       # Stattion name can be a substring of actual station name
       if stn.lower() in items.lower():
          stfind = True
          logging.info("found station yeah ! %s", stfind)
          return items
   if not stfind:
      return None
def validate_stn(stnname,stnlist):
    stnabbr = [x['abbr'] for x in stnlist]
    stndict ={}
    for items in stnlist:
        name = items['name'].lower()
        stndict[name] = items['abbr']
    if stnname not in stnabbr:
       stnname = stnname.lower()
       try: 
          stnname = validate_name(stnname,stnlist)
          logging.info("Destinaton name is %s", stndict)
          retstn = stndict[stnname.lower()]
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
    dest = validate_name(dest,stnlist)
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

#my test playground 
#ret = getSchedule("Dublin","Daly City")
#print ret
