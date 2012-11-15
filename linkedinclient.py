#!/usr/bin/env python
from config import Config                       # my class for dealing with configuration info
from BeautifulSoup import BeautifulSoup
import oauth2 as oauth
import sys
import collections
# ====================================================================================================#
# exception class for errors creating the LinkedInClient
# ====================================================================================================#
class LicError(Exception):
    pass

class LinkedInClient(object):
    def __init__(self, config):
        self.client     = None                                              # init creates the client below
        self.baseURL    = "http://api.linkedin.com/v1/people/"              # URL for the people API
        
        consumer_key    = config.get_consumerKey()
        consumer_secret = config.get_consumerSecret()
        user_token      = config.get_userToken()
        user_secret     = config.get_userSecret()

        try:
            consumer    = oauth.Consumer(consumer_key, consumer_secret)     # Use APIkey & secret to instance --> consumer
            accessToken = oauth.Token(key=user_token, secret=user_secret)   # Use token  & secret to instance --> accessToken
            self.client = oauth.Client(consumer, accessToken)               # Use consumer & accessToken to instance ---> client
        except Exception, detail:
            raise LicError(detail)
            
        return

    #
    # Returns a list of namedtuples 
    # One tuple for each connection of the currently authorized user
    # NB: "private" connections are eliminated (no meaningful data and causes uniqueness errors in DB
    # ====================================================================================================#
    def get_connections(self):
        resp, content = self.client.request(self.baseURL + "~/connections") # get all connections in XML
        soup  = BeautifulSoup(content)                                      # turn the XML into soup
        recordLayout = collections.namedtuple('RecordLayout', 'id firstName lastName locationName countryCode')
        
        connections = []
        for person in soup.findAll("person"):
            firstName = person.find('first-name')
            if (firstName != None):
                firstName = firstName.renderContents(encoding=None).format(u'')  # encoding return unicode
                if (firstName != "private"):
                    lastName     = person.find  ('last-name').renderContents(encoding=None).format(u'')
                    id           = person.find  ('id'       ).renderContents(encoding=None).format(u'')
                    location     = person.find  ('location' )
                    locationName = location.find('name'     ).renderContents(encoding=None).format(u'')
                    country      = location.find('country'  )
                    countryCode  = country.find ('code'     ).renderContents(encoding=None).format(u'')
                    
                    record = recordLayout(id, firstName, lastName, locationName, countryCode)
                    connections.append(record)
        
        return(connections)
        
    #
    # Returns a list of id's 
    # One for each connection shared between authorized user and the "id" in question
    # NB: "private" connections are eliminated (no meaningful data and causes uniqueness errors in DB)
    # ====================================================================================================#
    def get_sharedConnections(self, idConnected):
        start          = 0                                                                  # start the 
        baseReqString  = ":(relation-to-viewer:(related-connections))" + "?count=20&start=" # request string
        reqString      = baseReqString + str(start)                                         # at 0
        
        resp,content   = self.client.request(self.baseURL + idConnected + reqString)        # get the first batch 
        soup           = BeautifulSoup(content)                                             # turn it into soup
        nbrConnections = self.__countSharedConnections(soup)                                # if > 20 connections we need to
        nbrWindows     = nbrConnections/20                                                  # make multiple requests in "windows"

        sharedConnections = []
        curWindow = 0
        while (True):
            for person in soup.findAll("person"):
                idShared = person.find('id')
                if (idShared != None):
                    idShared = idShared.renderContents(encoding=None).format(u'')
                    if (idShared != None):
                        sharedConnections.append(idShared)
            curWindow = curWindow + 1
            if (curWindow > nbrWindows):
                break
            start        = curWindow * 20
            reqString    = baseReqString + str(start)
            resp,content = self.client.request(self.baseURL + idConnected + reqString)
            soup         = BeautifulSoup(content)    

        return(sharedConnections)        
        
    #
    # Count connections
    # ====================================================================================================#
    def __countSharedConnections(self, soup):
        count = 0   
        strCount = soup.find("related-connections")['total']
        if (strCount != None):
            return (int(strCount))
        else:
            return(-1)

# ====================================================================================================#
# ====================================================================================================#
# ========                                                                                     =======#
# ========                 M A I N                                                             =======#
# ========                                                                                     =======#
# ====================================================================================================#
# ====================================================================================================#
if  __name__ == "__main__":
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
    
    connectionRecs = lic.get_connections()
    for record in connectionRecs:
        print record.id, record.lastName, record.firstName
        
        for field in record:
            sys.stdout.write(field.encode('utf-8'))
            sys.stdout.write("\t")
            
        print ""
    
    for record in connectionRecs:
        sharedConnections = lic.get_sharedConnections(record.id)
        for sharedConnection in sharedConnections:
            print sharedConnection
    
    print "Terminating normally."
    exit()
