#!/usr/bin/env python

import datetime
import oauth2 as oauth
import httplib2
import time, os, simplejson
import sqlite3
from config import Config                       # my class for dealing with configuration info
from linkedinclient import LinkedInClient
from BeautifulSoup import BeautifulSoup


# TODO rewrite this as OO, rather than structured python; Hide implementation details inside objects
# ---- (DONE) Configuration - Config
# ---- (DONE) LinkedInClient- LinkedInClient
# ---- sqlite               - DBManager
#  
# TODO (DONE) github repo   
# TODO use an OLTP/DW approach
# ---- Move the current records into the datawarehouse and empty the database before refreshing snapshot
# TODO Create a commandline environment, as a precursor to a web GUI
# ---- Let user choose to update their database, generate intermediate tables and reports
# TODO create a heatmap of connection strength using affinities 
# ---- show how shared connections are affinitized
# TODO Store employment histories for each connection - similar format to sharedConnections
# build an employment timeline table from the history transactions
# do fuzzy matching on company names (e.g. Sage, Sage NA, Sage Group should all be same company
# TODO create 

# ====================================================================================================#
# Create the tables if they don't already exist
# ====================================================================================================#
def init_db(db):
    db.execute('''
        CREATE TABLE IF NOT EXISTS myConnections (Id         TEXT PRIMARY KEY UNIQUE,
                                                  FirstName  TEXT,
                                                  LastName   TEXT,
                                                  Date       TEXT)
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS sharedConnections (IdConnectedtoMe TEXT,
                                                      IdConnectedToUs TEXT,
                                                      Date            TEXT)
    ''')
    return

# ====================================================================================================#
# ====================================================================================================#
# ========                                                                                     =======#
# ========                 M A I N                                                             =======#
# ========                                                                                     =======#
# ====================================================================================================#
# ====================================================================================================#
if  __name__ == "__main__":
    today = datetime.date.today()

    try:
        config = Config(None)               ;print "Config read: SUCCESS."
        lic    = LinkedInClient(config)     ;print "LinkedIn Client Created: SUCCESS."
    except ConfigError, detail:
        print "Config Error: ", detail
        exit()
    except LicError, detail:
        print "LinkedIn Client Error: ", detail
        exit() 
        
    db  = sqlite3.connect(config.get_dbPath())
    init_db(db)
    connectionRecs = lic.get_connections()
    for rec in connectionRecs:
        db.execute('''INSERT INTO myConnections(Id, FirstName, LastName, Date) 
                                                VALUES (?,?,?,?)''', 
                                               (rec.id, rec.firstName, rec.lastName, today))
        db.commit()

    for rec in connectionRecs:
        sharedConnections = lic.get_sharedConnections(rec.id)
        for sc in sharedConnections:
            db.execute('''INSERT INTO sharedConnections(IdConnectedToMe, IdConnectedToUs, Date) 
                                                        VALUES (?,?,?)''',
                                                       (rec.id, sc, today))
            db.commit()
            
    exit()
# ===========================================


