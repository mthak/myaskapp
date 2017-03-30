#!/usr/bin/env python
import json
import xmltodict
import json
import requests
import logging

stations = ['12th St. Oakland City Center', '16th St. Mission', '19th St. Oakland', '24th St. Mission', 'Ashby', 'Balboa Park', 'Bay Fair', 'Castro Valley', 'Civic Center', 'Coliseum', 'Colma', 'Concord', 'Daly City', 'Downtown Berkeley', 'Dublin', 'El Cerrito del Norte', 'El Cerrito Plaza', 'Embarcadero', 'Fremont', 'Fruitvale', 'Glen Park', 'Hayward', 'Lafayette', 'Lake Merritt', 'MacArthur', 'Millbrae', 'Montgomery St.', 'North Berkeley', 'North Concord', "Oakland Int'l Airport", 'Orinda', 'Pittsburg Bay Point', 'Pleasant Hill', 'Powell St.', 'Richmond', 'Rockridge', 'San Bruno', "San Francisco Int'l Airport", 'San Leandro', 'South Hayward', 'South San Francisco', 'Union City', 'Walnut Creek', 'West Dublin', 'West Oakland']
key="MW9S-E7SL-26DU-VV8V"
def validate_name(stn,stnlist):
   stnname = [ x['name'] for x in stnlist ]
   stfind = False
   for items in stnname:
       # Stattion name can be a substring of actual station name
       print "items ins " , items
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
       stnname = validate_name(stnname,stnlist)
       logging.info("Destinaton name is %s", stndict)
       if stnname:
          try:
              retstn = stndict[stnname.lower()]
          except KeyError,e:
              retstn = None
       else:
           retstn = None
    else:
       retstn = stnname
    return retstn

def getrouteInfo(source,dest):
    stns = requests.get("http://bart.crudworks.org/api/stations")
    stnlist = json.loads(stns.content)
    print "stattion list " , stnlist
    source = validate_stn(source,stnlist)
    if not source:
       return [" You have specified an invalid source stattion , Please ask help to get list of stations" ]
    dest = validate_stn(dest,stnlist)
    print "destination is ", dest
    if not dest:
       print "dest not found"
       return ["The destination station you requested is not correct. Please ask help to get lis of all bart stations"]
    print "source and etination are ", source,dest
    allroutes = requests.get("http://api.bart.gov/api/route.aspx?cmd=routes&key="+key)
    routesjson = xmltodict.parse(allroutes.content)
    myroutes = routesjson['root']['routes']['route']
    routeid = []
    result = []
    for route in myroutes:
        print json.dumps(route)
        print "route id is ", route['number']
        routeid.append(route['number'])
    for rid in routeid:
        routeinfoxml = requests.get("http://api.bart.gov/api/route.aspx?cmd=routeinfo&route="+rid+"&key="+key)
        routeinfo = xmltodict.parse(routeinfoxml.content)
        stationlist = routeinfo['root']['routes']['route']['config']['station']
        print " station list " , stationlist
        if dest in stationlist and source in stationlist and stationlist.index(source) < stationlist.index(dest):
           finaldest = routeinfo['root']['routes']['route']['destination']
           if finaldest != source:
              logging.debug(" my station list %s" , stationlist)
              print "my route number " , rid
              mydata = getSchedule(source,finaldest)
              print " mydata is ", mydata
              if mydata:
                 result.extend(mydata)
    print " data is ",result
    # remove duplicated and dump it back in list
    # set does not order data back in same manner so do a sort later for the list
    if not result:
       result = ["No train available from Source to Destination"]
    # onlu if we get result as list of strings we shall add next train string
    if all(isinstance(item, int) for item in result):
        result = list(set(result))
        result.sort(key=int)
        result = [ "next train in "+str(items) +"  minutes      " for items in result ]
    print "result is " , result  
    # alexa does not like lists as it speaks , as comma in response so convert it to string
    spaces = ' '*50
    if len(result) > 5 :
       result = spaces.join(result[:5])
    else:
        result =spaces.join(result)
    print "result is " , result  
    return result 

def getSchedule(source,dest):
    stns = requests.get("http://bart.crudworks.org/api/stations")     
    stnlist = json.loads(stns.content)
    print "source and destination is " , source,dest
    source = validate_stn(source,stnlist)
    if not source:
       return [" Invalid Source Station , Please pick a valid station. Ask help for list of all stations"]
    dest = validate_stn(dest,stnlist)
    print "destination is ", dest
    if not dest:
       return ["The destination station in not correct. Please ask help for list of all stations"]
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
        result = ["Sorry Could not retrieve bart information at this time. Please try later"]
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
        if alldestinations['abbreviation'] == dest:
           found = True
           if type (alldestinations['estimate']) != list:
              alltimes = [ alldestinations['estimate']['minutes'] ]
           else:
               alltimes = [ data['minutes'] for data in alldestinations['estimate'] ]
           for time in alltimes:
              if "Leaving" in time:
                  time = 0
              result.append(int(time))
    if not found:
       result = None
       #result = ["No train available from Source to Destination"]
    return  result

#my test playground 
#ret = getrouteInfo("Dublin","Fremont")
#print ret
