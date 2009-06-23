'''
db.py

 Created on: Jun 18, 2009
 Authors: dh
 
 $LastChangedBy$
 $LastChangedDate$
 $Revision$
 
 (C) 2008-2009 by Computer Networks and Internet, University of Tuebingen
 
 This file is part of UNISONO Unified Information Service for Overlay 
 Network Optimization.
 
 UNISONO is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 2 of the License, or
 (at your option) any later version.
 
 UNISONO is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 
 You should have received a copy of the GNU General Public License
 along with UNISONO.  If not, see <http://www.gnu.org/licenses/>.
 
'''

import logging
import sqlite3

from unisono.utils import configuration

class NotInCacheError(Exception):
    pass

class InvalidTableLayout(Exception):
    pass

class DataBase():
    '''
    DataBase class for unisono caching
    
    This class provides a generic interface for all caching purposes.
    The database is created in memory. 
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    def __init__(self):
        '''
        Constructor
        '''
        try:
            dbfile = self.config.get('Cache', 'dbfile')
            self.logger.info('Initialize DB: %s', dbfile)
        except:
            self.logger.info('Initialize DB at default location')
            dbfile = '/dev/shm/unisono.db'
        self.config = configuration.get_configparser()
        self.dbcon = sqlite3.connect(dbfile)
        self.dbcursor = self.dbcon.cursor()


    def create_table(self, name, idcount, valuetype):
        '''
        Create a new table in the cache
        
        For each data item, the cache holds its own table. The table is named 
        after the data item (e.g. RTT for RTT data items)
        
        @param name table name as string
        @param idcount number of identifiers required for this data item. Must
                       be >0
        @param valuetype the type of the result values as string. Must be one of
                         TEXT, INT, REAL
        '''
        
        if idcount < 1:
            raise InvalidTableLayout()
        if valuetype not in ['TEXT', 'INT', 'REAL']:
            raise InvalidTableLayout()
        
        command = "create table " + name + "("
        for i in range(idcount):
            command = command + "identifier" + str(i+1) + " TEXT,"
        command = command + " time REAL, value " + valuetype + ");"
        try:
            self.dbcursor.execute(command)
            self.dbcon.commit()
            self.logger.debug("table %s created ! ", name)
        except sqlite3.OperationalError:
            self.logger.info("table %s exists, skipping", name)

        
    def check_for(self, paramap):
        self.logger.debug('Checking db for %s', paramap)
        result = {}
        table = paramap['dataitem']
        if 'identifier1' in paramap.keys():
            identifier1 = paramap['identifier1']
        else:
            raise NotInCacheError
        if 'identifier2' in paramap.keys():
            identifier2 = paramap['identifier2']
        else:
            identifier2 = None
        #TODO get only the rows with correct identifiers
        command = 'select * from ' + table + ' where identifier1="' + identifier1 + '" order by time desc'
        #command = "select * from " + table + " order by time"
        #command = "select * from ? where identifier1=? and identifier2=?"
        c = self.dbcon.cursor()
        try:
            c.execute(command)
#            c.execute('select * from RTT where identifier1="193.196.31.38"; ')
            row = c.fetchone()
            if row != None:
                self.logger.debug('our cached result: %s', row)
                result[table] = row[3]
                return result
            else:
                raise NotInCacheError
        except sqlite3.OperationalError as e:
            self.logger.error(e)
            
            raise NotInCacheError
        

    def store(self, paramap):
        status = 0
        self.logger.debug('Storing %s', paramap)
        # get all stuff out of the paramap
        timestamp = paramap['time']
        del paramap['time']
        identifier1 = paramap['identifier1']
        del paramap['identifier1']
        if 'identifier2' in paramap.keys():
            identifier2 = paramap['identifier2']
            del paramap['identifier2']
        else:
            identifier2 = None
        # delete what we do not need
        self.logger.debug('delete stuff %s', paramap)
        try:
            del paramap['dataitem']
            del paramap['id']
            del paramap['error']
            del paramap['errortext']
            del paramap['type']
        except KeyError:
            self.logger.debug('couldn\'t delete all items, bad luck...')
        # process data items
        self.logger.debug('storing dataitems: %s', paramap)
        c = self.dbcon.cursor()
        if identifier2 != None:
            for d, v in paramap.items():
                try:
                    c.execute("insert into " + d + " values (?, ?, ?, ?);", (identifier1, identifier2, timestamp, v))
                except sqlite3.OperationalError:
                    
                    if type(v) == str:
                        t= 'TEXT'
                    elif type(v) == int:
                        t = 'INT'
                    elif type(v) == float:
                        t = 'REAL'
                    else:
                        t = 'NULL'
                    self.create_table(d, 2, t)
                    c.execute("insert into " + d + " values (?, ?, ?, ?);", (identifier1, identifier2, timestamp, v))
        else:
            for d, v in paramap.items():
                try:
                    c.execute("insert into " + d + " values (?, ?, ?);", (identifier1, timestamp, v))
                except sqlite3.OperationalError:
                    if type(v) == str:
                        t= 'TEXT'
                    elif type(v) == int:
                        t = 'INT'
                    elif type(v) == float:
                        t = 'REAL'
                    else:
                        t = 'NULL'
                    self.create_table(d, 1, t)
                    c.execute("insert into " + d + " values (?, ?, ?);", (identifier1, timestamp, v))
        self.dbcon.commit()
        return status
    
    def purge(self, table, time):
        '''
        Purge all entries in a table upt to a specific time
        
        @param table table to be purged (string)
        @param time unix time stamp in seconds (int) 
        '''
        self.logger.debug('Purge table %s up to %s', table, time)
        c = self.dbcon.cursor()
        c.execute("delete from " + table + " where time < " + str(time) + ";")
        c.close()
        self.dbcon.commit()
