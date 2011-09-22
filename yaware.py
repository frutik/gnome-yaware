#!/usr/bin/python

#TODO owning user? previous windows id?

import subprocess
import ConfigParser
import time, string, md5, sys
from sqlobject import *
import logging

from optparse import OptionParser

cmd_options_parser = OptionParser()
cmd_options_parser.add_option("--debug", dest="is_debug", help="Run in debug mode", default=False)
cmd_options_parser.add_option("--config", dest="config_file", help="Config file", default="config.ini")

(cmd_options, args) = cmd_options_parser.parse_args()

DEBUG = cmd_options.is_debug
CONFIG_FILE = cmd_options.config_file

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

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
                result['WM_CLIENT_LEADER'] = line.split('#')[1].strip()
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
    config.read(CONFIG_FILE)
    dsn = config.get('SQL', 'dsn')
    sleep_time = float(config.get('GENERAL', 'sleep'))
except:
    print 'config not found'
    sys.exit()

class YawareEvent(SQLObject):
    added = StringCol()
    windowid = StringCol()
    windowhash = StringCol()
    WM_CLIENT_LEADER = StringCol()
    WM_NAME = StringCol()
    WM_CLASS = StringCol()
    WM_CLIENT_MACHINE = StringCol()


connection = connectionForURI(dsn)
sqlhub.processConnection = connection

try:
    YawareEvent.createTable()
except:
    pass

while True:
    time.sleep(sleep_time)
    row = GetActiveWindow()
    
    logging.debug(row)
    
    YawareEvent(
	added = row[0], 
	windowid = row[1], 
	windowhash = row[2], 
	WM_CLIENT_LEADER = row[3]['WM_CLIENT_LEADER'],
	WM_NAME = row[3]['WM_NAME'],
	WM_CLASS = row[3]['WM_CLASS'],
	WM_CLIENT_MACHINE = row[3]['WM_CLIENT_MACHINE'],
    )
    
    
