#!/usr/bin/python

import subprocess
import ConfigParser
import time, string, md5, sys
from sqlobject import *

def GetActiveWindow():
    result = {}
    id = subprocess.Popen(["xprop", "-root", "_NET_ACTIVE_WINDOW"], stdout=subprocess.PIPE).communicate()[0].strip().split()[-1],
    result['id'] = id[0]
    output = subprocess.Popen(["xprop", "-id", result['id']], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    for item in  output:
        lines = string.split(item, chr(0x00a))
        for line in  lines:
            line = line.strip()
            if line.find('WM_CLIENT_LEADER') == 0:
                result['WM_CLIENT_LEADER'] = line.split('#')[1]
            elif line.find('WM_NAME') == 0:
                result['WM_NAME'] = line.split('=')[1].strip()
            elif line.find('WM_CLASS') == 0:
                result['WM_CLASS'] = line.split('=')[1].strip()
            elif line.find('WM_CLIENT_MACHINE') == 0:
                result['WM_CLIENT_MACHINE'] = line.split('=')[1].strip()
            elif line.find('WM_COMMAND') == 0:
                result['WM_COMMAND'] = line.split('=')[1].strip()

    return  time.time(), result['id'], md5.md5(str(result)).hexdigest(), result

try:
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    dsn = config.get('SQL', 'dsn')
except:
    print 'config not found'
    sys.exit()

class YawareEvent(SQLObject):
    added=DateTimeCol(default=sqlbuilder.func.NOW())
    event = StringCol()
    uniqueid = StringCol(default=None)
    raw = StringCol(default=None)

connection = connectionForURI(dsn)
sqlhub.processConnection = connection

try:
    YawareEvent.createTable()
except:
    pass

while True:
    time.sleep(1.9)
    print GetActiveWindow()
