#!/usr/bin/env python

import datetime
import oauth2 as oauth
import httplib2
import time, os, simplejson
import sqlite3
from config import Config                       # my class for dealing with configuration info
from linkedinclient import LinkedInClient
from BeautifulSoup import BeautifulSoup


# TODO rewrite this as OO, rather than structured python
# ---- Configuration (DONE) - Config
# ---- LinkedInClient       - LinkedInClient
# ---- sqlite               - DBManager
# ---- Hide the implementation details inside objects
# TODO integrate with github
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
# Initiatize the linkedin client
# ====================================================================================================#
def init_linkedin_client(config): 
    consumer_key    = config.get_consumerKey()
    consumer_secret = config.get_consumerSecret()
    user_token      = config.get_userToken()
    user_secret     = config.get_userSecret()

    consumer    = oauth.Consumer(consumer_key, consumer_secret)     # Use APIkey & secret to instance --> consumer
    accessToken = oauth.Token(key=user_token, secret=user_secret)   # Use token  & secret to instance --> accessToken
    client      = oauth.Client(consumer, accessToken)               # Use consumer & accessToken to instance ---> client
    return (client)

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
# returns (TRUE) if no connection records exist with today's timestamp
# ====================================================================================================#
def connections_are_stale(db, today):
    today = (str(today),)                                               # reformat today for exec
    cur = db.cursor()
    cur.execute('SELECT * FROM myConnections WHERE Date=?', today)      # select all of today's recs
    if cur.fetchone() == None:                                          # 
        return True
    else:
        return False

# ====================================================================================================#
# Add the connections in SOUP to the db with timestamp==today
# ====================================================================================================#
def add_connections_snapshot(db, soup, today):
    count = 0
    for person in soup.findAll("person"):
        firstName = person.find('first-name')
        if (firstName != None):
            firstName = firstName.renderContents(encoding=None).format(u'')  # encoding return unicode
            if (firstName != "private"):
                lastName  = person.find('last-name').renderContents(encoding=None).format(u'')
                id        = person.find('id'       ).renderContents(encoding=None).format(u'')
                db.execute('''INSERT INTO myConnections(Id, FirstName, LastName, Date) 
                                                        VALUES (?,?,?,?)''', 
                                                       (id, firstName, lastName, today))
                count = count+1
    if (count > 0):
        db.commit()
    return(count)

# ====================================================================================================#
# Add shared connections to the database
# ====================================================================================================#
def add_shared_connections(baseURL, liClient, db, today):
    today = str(today)                                               # reformat today for exec
    count = 0
    curOuter = db.cursor()
    curOuter.execute('SELECT * FROM myConnections WHERE Date=?', (today, ))                     # a list of 1
    rows = curOuter.fetchall()                                                                  # multiple cur in nested loop=prob!
    for row in rows:
        idConnectedToMe  = row[0]
        firstName        = row[1]
        lastName         = row[2]
        
        count, sharedCons = get_shared_connections(liClient, baseURL, idConnectedToMe)
        print idConnectedToMe + "\t" + lastName + ", "  + firstName + "\t has " + str(count) + " shared connections"
        
        curInner = db.cursor()
        for con in sharedCons:
            idConnectedToUs = con[0]
            if (idConnectedToUs != 'private'):
                print "\t", con[0], "\t", con[1], "\t", con[2]
                curInner.execute('''INSERT INTO sharedConnections(IdConnectedToMe, IdConnectedToUs, Date) 
                                                                  VALUES (?,?,?)''',
                                                                 (idConnectedToMe, idConnectedToUs, today))
        db.commit()
        count = count +1
    return(count)

# ====================================================================================================#
# Count connections
# ====================================================================================================#
def count_connections(soup):
    count = 0
    strCount = soup.find("related-connections")['total']
    if (strCount != None):
        return (int(strCount))
    else:
        return(-1)

# ====================================================================================================#
#  TODO fix Id / id -- confusing
# ====================================================================================================#
def get_shared_connections(liClient, baseURL, Id):

    start          = 0
    baseReqString  = ":(relation-to-viewer:(related-connections))" + "?count=20&start="
    reqString      = baseReqString + str(start)
    resp,content   = liClient.request(baseURL + Id + reqString)
    soup           = BeautifulSoup(content)
    nbrConnections = count_connections(soup)
    nbrWindows     = nbrConnections/20             # liapi returns max 20 connections - retrieve in windows

    sharedConnections = []
    curWindow = 0
    while (True):
        for person in soup.findAll("person"):
            first = person.find('first-name')
            if (first != None):
                first = first.renderContents()
                last  = person.find('last-name').renderContents()
                id    = person.find('id').renderContents()
                sharedConnections.append([id, last, first])
        curWindow = curWindow + 1
        if (curWindow > nbrWindows):
            break
        start        = curWindow * 20
        reqString    = baseReqString + str(start)
        resp,content = liClient.request(baseURL + Id + reqString)
        soup         = BeautifulSoup(content)    

    return(nbrConnections, sharedConnections)

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
        config = Config(None)
        print "Config read: SUCCESS."
        lic    = LinkedInClient(config)
        print "LinkedIn Client Created: SUCCESS."
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

    db  = sqlite3.connect(config.get_dbPath())
    init_db(db)
    
    liClient = init_linkedin_client(config)

    baseURL = "http://api.linkedin.com/v1/people/"
    
    print "===========================\n"

    # if connections are stale, add a snapshot of connections
    if connections_are_stale(db, today):
        resp, content = liClient.request(baseURL + "~/connections")     # get all connections in XML
        soup  = BeautifulSoup(content)                                  # turn the XML into soup
        count = add_connections_snapshot(db, soup, today)               # turn the soup into db records
        db.commit()
        print count, "connections were added to db"
    else:
        print "Connections are current"

    # build the shared connections graph
    count = add_shared_connections(baseURL, liClient, db, today)        # TODO clean up the parameter list      
    print count, "shared connections were added"

    db.close()
