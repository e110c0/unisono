'''
dispatcher.py

 Created on: May 5, 2009
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
from queue import Queue
from unisono.connector_interface import XMLRPCServer, XMLRPCReplyHandler
from unisono.event import Event
from unisono.utils import configuration
from unisono.mmplugins.mmtemplates import MMTemplate

import logging, copy
import threading
class Dispatcher:
    '''
    classdocs
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    def __init__(self):
        '''
        Constructor
        '''
        self.config = configuration.get_configparser()
        self.active_orders = {}
        self.eventq = Queue()
        self.start_xmlrpcserver()
        self.start_xmlrpcreplyhandler()
        self.init_plugins()
    
    def start_xmlrpcserver(self):
        # TODO: check whether XMLRPCserver is alread running
        self.xsrv = XMLRPCServer(self.eventq, self)

    def start_xmlrpcreplyhandler(self):
        self.replyq = Queue()
        xrh = XMLRPCReplyHandler(self.xsrv.conmap, self.replyq, self.eventq)
        
    def init_plugins(self):
        # list of registered plugins with their queue and object
        self.plugins = {}
        # list of datitems with the registered plugin and its cost
        self.dataitems = {}
        # initialize M&Ms

        try:
            active_plugins = self.config.get('M&Ms', 'active_plugins')
            self.logger.info('Loading plugins: %s', active_plugins)
        except:
            self.logger.info('No plugins configured, loading defaults.')
            # TODO get all available by default
            active_plugins = 'cvalues'
            pass
        for p in active_plugins.split(','):
            try:
                p = p.strip()
                mod = __import__('unisono.mmplugins', globals(), locals(), [p])
                mod = getattr(mod, p)
                self.logger.debug('Mod: %s', mod)
            except:
                self.logger.error('Could not load plugin %s', p)
            for n, v in vars(mod).items():
                if type(v) == type and issubclass(v, MMTemplate):
                    iq = Queue()
                    mm = v(iq, self.eventq)

                    self.registerMM(n, mm)
                    mm_thread = threading.Thread(target=mm.run)
                    # Exit the server thread when the main thread terminates
                    mm_thread.setDaemon(True)
                    mm_thread.start()
                    self.logger.info("M&M %s loop running in thread: %s", mm.name, mm_thread.name)
        self.logger.debug('plugin list: %r' % self.plugins)
        self.logger.debug('registered dataitems: %s', self.dataitems)

    def registerMM(self, name, mm):
        '''
        To be able to use a M&M plugin, its provided dataitems must be globally
        registered.
        '''
        self.plugins[name] = mm
        self.active_orders[name] = []
        di = mm.availableDataItems()
        cost = mm.getCost()
        self.logger.debug('Data items: %s', di)
        self.logger.debug('Cost: %s', cost)
        # merge with current dataitem list
        for i in di:
            if i in self.dataitems.keys():
                self.dataitems[i].append((cost, name))
                self.dataitems[i].sort()
            else:
                self.dataitems[i] = [(cost,name)]

    def deregisterMM(self, name):
        '''
        deregisterMM removes a M&M from the global register and deactivates it.
        This can be used for runtime module deactivation.
        '''
        self.logger.debug('Unregistering %s', name)
        di = self.plugins[name].availableDataItems()
        for i in di:
            # only delete the correspondent entry
            self.dataitems = [i for i in self.dataitems if i[1] != name]
        del self.plugins[name]

    def run(self):
        '''
        Main loop of the dispatcher
        '''
        while True:
            event = self.eventq.get()
            self.logger.debug('got an event: %s', event.type)
            if event.type == 'CACHE':
                pass
            elif event.type == 'CANCEL':
                pass
            elif event.type == 'ORDER':
                self.logger.debug('order: %s', event.payload)
                self.process_order(event.payload)
            elif event.type == 'RESULT':
                self.logger.debug('result. %s', event.payload)
                self.process_result(event.payload)
            else:
                self.logger.debug('Got an unknown event, discarding.')

    def process_order(self, order):
        # find the correspondent MM
        # TODO: handle cost, active orders etc
        mm = self.dataitems[order['dataitem']][0][1]
        # and its queue
        mmq = self.plugins[mm].inq
        # remember order
        exists = 0
        for o in self.active_orders[mm][:]:
            if (o['conid'] == order['conid']) and (o['orderid'] == order['orderid']):
                exists = 1
                self.logger.error('Order already active, possible id clash? Discarding')
        if exists == 0:
            self.active_orders[mm].append(order)


        # create request for MM
        req = copy.copy(order)
        del req['conid']
        del req['orderid']
        #self.logger.debug['stripped request: %s', req]
        # queue request
        mmq.put(req)

    def process_result(self, result):
        mm = result[0]
        r = result[1]
        # find in all active orders
        # TODO: this is really broken and works only with cvalues 
        for o in self.active_orders[mm][:]:
            if (o['locator1'] == r['locator1']): # and (o['locator2'] == r['locator2']):
                o[o['dataitem']] = r[o['dataitem']]
                self.replyq.put(Event('DELIVER', o))
                # does this delete the right stuff??
                self.active_orders[mm] = [i for i in self.active_orders[mm] if i['orderid'] != o['orderid']]




