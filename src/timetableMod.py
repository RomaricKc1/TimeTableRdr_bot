# -*- coding: utf-8 -*-
#!/usr/bin/python


from logging import debug
from os import terminal_size
from ics import Calendar

import requests
from datetime import datetime, timezone
from pytz import UTC
from tatsu.bootstrap import main # timezone
import time

url = '' # url to your ics file
table = Calendar(requests.get(url).text)

# read from existing file
# cont_ = open('cal.ics','r')
# table = Calendar(cont_.read())

#--------------------------------------------------------------------------------------------

main_data = []

hour_before = 3600 #s
half_hour_before = 1800
quart_hour_before = 900
five_min_before = 300

DEBUG = False

#--------------------------------------------------------------------------------------------
class Item(object):
    def __init__(self, uid, title, begin, end, descp, lates_mod, where, org, rt_date):
        self.title = title
        self.begin = begin
        self.end = end
        self.descp = descp
        self.lates_mod = lates_mod
        self.where = where
        self.org = org

        self.UID = uid
        self.rt_date = rt_date  #strftime("%A %d. %B %Y - %H:%M:%S")
        self.timestmp = time.mktime(datetime.strptime(self.begin, "%A %d. %B %Y - %H:%M:%S").astimezone().timetuple())

        # 000 -> Not notified yet
        # 001 -> 1h notified
        # 010 -> 1h, hh notified
        # 011 -> 1h, hh, qh notified
        # 100 -> 1h, hh, qh, lw notified

        self.notif_status = 0b00

    def getNotifStatus(self):
        return self.notif_status
    def setNotifStatus(self, status):
        self.notif_status = status
   
    def getTimestmp(self):
        return self.timestmp
    def introduce(self):
        print('START'.center(60, '-'))
        print(f'\nTITLE: # {self.title};\n****BEGIN: {self.begin}, END: {self.end}****\n\nDESC_&_LECTURER: {self.descp}\nLATEST_MOD: {self.lates_mod}\n\nWHERE: {self.where}; ORGANIZED_BY: {self.org}\nUID: {self.UID}\n\n\nRETRIEVED FROM INTERNET ON (UTC): {self.rt_date}')
        print('END'.center(60, '-'))

    def getTitle(self):
        return self.title
    def getBegin(self):
        return self.begin
    def getEnd(self):
        return self.end
    def getDesc(self):
        return str(self.descp) + ' Organized by: ' + str(self.org)
    def getLates_mod(self):
        return self.lates_mod

    def getLocation(self):
        return self.where
    def getInternet(self):
        return self.rt_date
    def getUID(self):
        return self.UID
    
def retrieve_data(table, main_data):

    data = {}
    
    for component in table.events:
        data['Name'] = component.name
        data['Alarm'] = component.alarms
        data['Extra'] = component.extra
        data['Attendees'] = component.attendees
        data['Categories'] = component.categories

        data['Created'] = datetime.strptime(str(component.created), "%Y-%m-%dT%H:%M:%S%z").astimezone().strftime("%A %d. %B %Y - %H:%M:%S")
        data['Description'] = component.description
        data['Last_Mod'] = component.last_modified
        data['Location'] = component.location
        data['Organizer'] = component.organizer

        data['Transparent'] = component.transparent
        data['URL'] = component.url
        data['UID'] = component.uid

        data['Begin'] = datetime.strptime(str(component._begin), "%Y-%m-%dT%H:%M:%S%z").astimezone().strftime("%A %d. %B %Y - %H:%M:%S")
        data['End'] = datetime.strptime(str(component._end_time), "%Y-%m-%dT%H:%M:%S%z").astimezone().strftime("%A %d. %B %Y - %H:%M:%S")
    
        format_data(data, main_data)
        
def format_data(data, main_data):

    title = data['Name']
    description =  data['Description']
    created = data['Created']
    mod = data['Last_Mod']
    location = data['Location']
    org =  data['Organizer']
    uid = data['UID']
    begin = data['Begin']
    end = data['End']

    m = Item(uid, title, begin, end, description, mod, location, org, created)
    main_data.append(m)

    """ print(f'\nTITLE: # {title};\n****BEGIN: {begin}, END: {end}****\n\nDESC_&_LECTURER: {description}\nLATEST_MOD: {mod}\n\nWHERE: {location}; ORGANIZED_BY: {org}\nUID: {uid}\n\n\nRETRIEVE FROM INTERNET ON: {created}')
    print('END'.center(60, '-')) """

retrieve_data(table, main_data)

if DEBUG:
    main_data[0].introduce()
    print(main_data[0].getTimestmp())


#---- data ready, begin getting the next class data by timestamp

wait_state = False # if the bot spot a class starting like 10 mins, it won't bother you again :(

#----USEFUL THINGS
def send_now(obj, now, msg):

    print('\b \n')
    print('New class starting soon'.center(80, '*'))
    print('\nWarning: Class may start soon\n')
    obj.introduce()
    eta = (obj.getTimestmp() - now) /60 #minutes
    print(f'ETA: {eta} minutes. {msg}')
    print('notif'.center(60, '*'))
    print('\n')

def NOTIFY(now=time.time()):
    send_data = []
    now_human = datetime.fromtimestamp(now).astimezone().strftime("%A %d. %B %Y - %H:%M:%S")

    if DEBUG:
        print(f'UTC: {now_human}')

    imminent_class = False
    next_class_id = None
    status = 0b000

    for i in range(len(main_data)):
        current_class = main_data[i]

        if (now > current_class.getTimestmp()): #classes that are over
            imminent_class = False
            if DEBUG:
                print('Those classes are over')
                print(f'Heck, {now_human} and  {datetime.fromtimestamp(main_data[i].getTimestmp()).astimezone().strftime("%A %d. %B %Y - %H:%M:%S")}')
            else:
                pass
        elif True: #not over yet
            # not notified yet, status = 0x000, next time, it will be 0x001
            if (current_class.getTimestmp() - now) <= hour_before and current_class.getNotifStatus() == 0b000:
                #1h notif pending
                imminent_class = True
                next_class_id = i
                
                if DEBUG:
                    print('\nYee soon')
                break #to save our precious key
            
            elif (current_class.getTimestmp() - now) <= half_hour_before and current_class.getNotifStatus() == 0b001:
                # aka only(==) 1hour notif already sent
                #.5h notif pending
                imminent_class = True
                next_class_id = i
                
                if DEBUG:
                    print('\nYee soon')
                break #to save our precious key

            elif (current_class.getTimestmp() - now) <= quart_hour_before and current_class.getNotifStatus() == 0b010:
                # aka only(==) 1hour and half hour notif already sent
                #0.25h notif pending
                imminent_class = True
                next_class_id = i
                
                if DEBUG:
                    print('\nYee soon')
                break #to save our precious key

            elif (current_class.getTimestmp() - now) <= five_min_before and current_class.getNotifStatus() == 0b011:
                # aka only(==) 1hour, half hour and q hour notif already sent
                #5m notif pending
                imminent_class = True
                next_class_id = i
                
                if DEBUG:
                    print('\nYee soon')
                break #to save our precious key


    if not imminent_class:
        send_data = []
        if DEBUG:
            print('No imminent class'.center(80, '-'))
        
    else: # something to send as notif, 1h or hh, or qh, or lw
        send_data = [] #reset send_data

        if main_data[next_class_id].getNotifStatus() == 0b000:
            # i.e. no notif hasn't been sent
            #start with 1h
            # go ahead and send it
            #send_now(main_data[next_class_id], now, 'Take yo time. Class start in 1 hour ^^')
            kind_words = 'Take yo time. Class start in 1 hour ^^'
            send_data.append(True)
            send_data.append(main_data[next_class_id])
            send_data.append(kind_words)
            send_data.append('1H')
            
            main_data[next_class_id].setNotifStatus(0b001) # i.e. 1h notif sent

        elif main_data[next_class_id].getNotifStatus() == 0b001:
            # i.e. 1h notif has been sent
            #next hh notif
            #send_now(main_data[next_class_id], now, 'Less than 30 mins.')
            kind_words = 'Less than 30 mins.'
            send_data.append(True)
            send_data.append(main_data[next_class_id])
            send_data.append(kind_words)
            send_data.append('HH')

            main_data[next_class_id].setNotifStatus(0b010) # i.e. 1h, hh notif sent

        elif main_data[next_class_id].getNotifStatus() == 0b010:
            # i.e. 1h, hh notif has been sent
            #next qh notif
            #send_now(main_data[next_class_id], now, 'Less than 15 mins, hurry up :) ')
            kind_words = 'Less than 15 mins, hurry up :)'
            send_data.append(True)
            send_data.append(main_data[next_class_id])
            send_data.append(kind_words)
            send_data.append('15m')
            
            main_data[next_class_id].setNotifStatus(0b011) # i.e. 1h, hh, qh notif sent

        elif main_data[next_class_id].getNotifStatus() == 0b011:
            # i.e. 1h, hh, qh notif has been sent
            #next lw notif
            #send_now(main_data[next_class_id], now, 'Yo last chance to be there. I am not going to tell you again ^_^')
            kind_words = 'Yo last chance to be there. I am not going to tell you again ^_^'
            send_data.append(True)
            send_data.append(main_data[next_class_id])
            send_data.append(kind_words)
            send_data.append('5m')

            main_data[next_class_id].setNotifStatus(0b100) # i.e. 1h, hh, qh, lw notif sent

    return send_data

def partition(array, begin, end):
    pivot = begin
    for i in range(begin+1, end+1):
        if array[i] <= array[begin]:
            pivot += 1
            array[i], array[pivot] = array[pivot], array[i]
    array[pivot], array[begin] = array[begin], array[pivot]
    return pivot

def quicksort(array, begin=0, end=None):
    if end is None:
        end = len(array) - 1
    def _quicksort(array, begin, end):
        if begin >= end:
            return
        pivot = partition(array, begin, end)
        _quicksort(array, begin, pivot-1)
        _quicksort(array, pivot+1, end)
    return _quicksort(array, begin, end)

def NextClass():
    timestamps = []
    now = time.time()
    next_class_id = 0
    next_class_timestamp = 0

    print(f'TimeZone: {datetime.fromtimestamp(now).astimezone().strftime("%A %d. %B %Y - %H:%M:%S")}')

    for i in range(len(main_data)):
        timestamps.append( main_data[i].getTimestmp() )
    quicksort(timestamps)

    for i in range(len(main_data)):
        current_timestamp = timestamps[i]

        if (now > current_timestamp): #classes that are over
            if DEBUG:
                print('These classes are over')
                print(datetime.fromtimestamp(current_timestamp).astimezone().strftime("%A %d. %B %Y - %H:%M:%S"))
            else:
                pass
        elif True: #not over yet
            next_class_id = i
            next_class_timestamp = timestamps[next_class_id]
            # since timestamps are sorted, the first time seeing a class that is not over is definetly the 1st next class
            if DEBUG:   
                print(f'\nNext class timestamp: {next_class_timestamp}\n')
                print(datetime.fromtimestamp(next_class_timestamp).astimezone().strftime("%A %d. %B %Y - %H:%M:%S") + '\n')
            break

    return next_class_timestamp

#-------- find the class data from original main data array
def Data_next_classe(tmp):
    data = None

    #execute a simple search algorithm
    for i in range(len(main_data)):
        current_class = main_data[i]
        if current_class.getTimestmp() == tmp:
            data = current_class

    return data

def intro_next_cls():
    obj_next_class = Data_next_classe(NextClass())
    return obj_next_class
