#!/usr/bin/env python
import sys
import quopri
import sqlite3

# ====================================================================================================#
#
# ====================================================================================================#
def init_group_count(db):
    db.execute('''
        DROP TABLE IF EXISTS groupConnectionsCount
    ''')
    
    db.execute('''
        CREATE TABLE groupConnectionsCount(Id                   TEXT PRIMARY KEY UNIQUE,
                                           LastName             TEXT,
                                           FirstName            TEXT,
                                           NbrSharedConnections INTEGER)
    ''')

    return()
    
# ====================================================================================================#
#
# ====================================================================================================#
def create_group_count(db):
    db.execute('''
        INSERT INTO groupConnectionsCount(Id, NbrSharedConnections)
            SELECT IdConnectedToMe, COUNT (1) as "NbrSharedConnections"
            FROM sharedConnections AS sc
            GROUP BY sc.IdConnectedToMe
    ''')

    db.execute('''
        UPDATE groupConnectionsCount
        SET FirstName = (SELECT myConnections.FirstName   
                         FROM myConnections 
                         WHERE myConnections.Id=groupConnectionsCount.Id),
            LastName = (SELECT myConnections.LastName   
                         FROM myConnections 
                         WHERE myConnections.Id=groupConnectionsCount.Id)
    ''')
    db.commit()
    
    return()

# ====================================================================================================#
#
# ====================================================================================================#
def report_group_count(db):
    sqlStatement = 'SELECT * FROM groupConnectionsCount ORDER BY NbrSharedConnections DESC'
    for row in db.execute(sqlStatement):
        for field in row:
            #print row[0].encode('utf-8')
            if (type(field) is int):
                sys.stdout.write(str(field))
            else:
                sys.stdout.write(str(field.encode('utf-8')))
            
            sys.stdout.write('\t')
            
        sys.stdout.write('\n')

    return()

# ====================================================================================================#
# ====================================================================================================#
# ========                                                                                     =======#
# ========                 M A I N                                                             =======#
# ========                                                                                     =======#
# ====================================================================================================#
# ====================================================================================================#
if (__name__ == "__main__"):
    db  = sqlite3.connect("../db/linkedin.db")
    init_group_count(db)
    create_group_count(db)
    report_group_count(db)
    print "Done."
    
