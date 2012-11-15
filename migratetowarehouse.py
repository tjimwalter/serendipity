#!/usr/bin/env python
import sys
import quopri
import sqlite3

# ====================================================================================================#
#
# ====================================================================================================#
def init_warehouse(db):
    db.execute('''
        CREATE TABLE IF NOT EXISTS myConnections( Id          TEXT NOT NULL,
                                                  LastName    TEXT,
                                                  FirstName   TEXT,
                                                  Date        TEXT NOT NULL, 
                                                  PRIMARY KEY (Id, Date))
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS sharedConnections( IdConnectedToMe    TEXT NOT NULL,
                                                      IdConnectedToUs    TEXT NOT NULL,
                                                      Date               TEXT NIT NULL, 
                                                      PRIMARY KEY (IdConnectedToMe, IdConnectedToUs, Date)); 
    ''')
    db.commit()
    return()
    
# ====================================================================================================#
#
# ====================================================================================================#
def etl_to_warehouse(db):
    destPath =     '/home/jim/linkedin/db/warehouse.db'
    sourcePaths = ['/home/jim/linkedin/db/li1028.db',
                   '/home/jim/linkedin/db/li1029.db',
                   '/home/jim/linkedin/db/li1030.db',
                   '/home/jim/linkedin/db/li1101.db',
                   '/home/jim/linkedin/db/li1102.db',
                   '/home/jim/linkedin/db/li1103.db',
                   '/home/jim/linkedin/db/li1104.db']

    cur = db.cursor()
    cur.execute('ATTACH ? AS dest', (destPath,))    
    for sourcePath in sourcePaths:
        cur.execute('ATTACH ? AS source', (sourcePath,))
        cur.execute('INSERT INTO dest.myConnections     SELECT * FROM source.myConnections')
        cur.execute('INSERT INTO dest.sharedConnections SELECT * FROM source.sharedConnections')
        cur.execute('DETACH source')
        db.commit()

    #db.commit()
    return()

# ====================================================================================================#
#
# ====================================================================================================#
def report_on_warehouse(db):
    print "not reports yet."
    return()

# ====================================================================================================#
# ====================================================================================================#
# ========                                                                                     =======#
# ========                 M A I N                                                             =======#
# ========                                                                                     =======#
# ====================================================================================================#
# ====================================================================================================#
if (__name__ == "__main__"):
    db  = sqlite3.connect("../db/warehouse.db")
    init_warehouse(db)
    etl_to_warehouse(db)
    report_on_warehouse(db)
    print "Done."
    
