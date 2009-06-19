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
from queue import Queue, Empty
from unisono.db import DataBase
from unisono.db import NotInCacheError

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
        self.pending_orders = {}
        self.eventq = Queue()
        self.init_database()
        self.start_xmlrpcserver()
        self.start_xmlrpcreplyhandler()
        self.init_plugins()
    
    def init_database(self):
        self.cache = DataBase()
    
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
            active_plugins = 'cvalues'
            pass
        for p in active_plugins.split(','):
            try:
                p = p.strip()
                mod = __import__('unisono.mmplugins', globals(), locals(), [p])
                self.logger.debug('Mod: %s', mod)
                mod = getattr(mod, p)

            except:
                self.logger.error('Could not load plugin %s', p)
                continue
            for n, v in vars(mod).items():
                if type(v) == type and issubclass(v, MMTemplate):
                    iq = Queue()
                    mm = v(iq, self.eventq)

                    self.registerMM(n, mm)
                    mm_thread = threading.Thread(target=mm.run)
                    # Exit the server thread when the main thread terminates
                    mm_thread.setDaemon(True)
                    mm_thread.start()
                    self.logger.info("M&M %s loop running in thread: %s", mm.__class__.__name__, mm_thread.name)
        self.logger.debug('plugin list: %r' % self.plugins)
        self.logger.debug('registered dataitems: %s', self.dataitems)

    def registerMM(self, name, mm):
        '''
        To be able to use a M&M plugin, its provided dataitems must be globally
        registered.
        '''
        self.plugins[name] = mm
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
                self.dataitems[i] = [(cost, name)]

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
            try:
                event = self.eventq.get(timeout=5)
            except Empty:
                pass
            else:
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
        # sanity checks
        for i in ['type', 'dataitem', 'orderid']:
            if i not in order.keys():
                self.logger.error('Order is incomplete (missing %s), discarding.', i)
                self.logger.debug('%s', order)
                order['error'] = 400
                order['errortext'] = 'Order incomplete, missing ' + i
                self.replyq.put(Event('DISCARD', order))
                return
        if order['dataitem'] not in self.dataitems.keys():
            self.logger.error('Order requests unknown data item %s, discarding.', order['dataitem'])
            order['error'] = 404
            order['errortext'] = 'Unknown data item ' + order['dataitem']
            self.replyq.put(Event('DISCARD', order))
            return
        if order['type'] not in ['oneshot','periodic','triggered']:
            self.logger.error('Order type %s unknown, discarding.', order['type'])
            order['error'] = 404
            order['errortext'] = 'Unknown order type ' + order['type']
            self.replyq.put(Event('DISCARD', order))
            return
        if (order['type'] != "oneshot"):
            self.logger.debug('Got a periodic or triggered order')
        if self.satisfy_from_cache(order):
            return
        elif self.aggregate_order(order):
            return
        else: 
            self.queue_order(order)

    def satisfy_from_cache(self, order):
        try:
            result = self.cache.check_for(order)
            order.update(result)
            # for at least the ariba connector (deprecated)
            order['result'] = order[order['dataitem']]
#            self.logger.debug('result from cache: %s', result)
#            self.logger.debug('updated order: %s', order)
            order['error'] = 0
            order['errortext'] = 'Everything went fine'
            self.replyq.put(Event('DELIVER', order))
            return True
        except NotInCacheError:
            return False

    def aggregate_order(self, order):
        di = order["dataitem"]
        compat_mms = set(i[1] for i in self.dataitems[di])
        for curmm, mmlist, paramap, waitinglist in self.pending_orders.values():
            if curmm in compat_mms:
                id1 = order.get("identifier1", None)
                id2 = order.get("identifier2", None)
                if id1 is not None and id1 != paramap.get("identifier1", None) or \
                    id2 is not None and id2 != paramap.get("identifier2", None):
                    return False
                self.logger.info('aggregated the order with already queued order')
                waitinglist.append(order)
                return True
        return False

    def put_in_mmq(self, mmq, id, order):
        # create request for MM
        req = copy.copy(order)
        del req['conid']
        del req['orderid']
        req['id'] = id
        #self.logger.debug['stripped request: %s', req]
        # queue request
        mmq.put(req)

    def queue_order(self, order):
        id = order['conid'], order['orderid']
        mmlist = copy.copy(self.dataitems[order["dataitem"]])
        curmm = mmlist.pop(0)[1]
        self.put_in_mmq(self.plugins[curmm].inq, id, order)
        self.pending_orders[id] = (curmm, mmlist, order, [])
        return

    def fill_order(self, order, result):
        try:
            di = order['dataitem']
            order[di] = result[di]
            # for at least the ariba connector (deprecated)
            order['result'] = result[di]
        except KeyError:
            order['error'] = 666
            order['errortext'] = 'dataitem not in result'
        return order

    def process_result(self, result):
        mm = result[0]
        r = result[1]
        id = r['id']
        curmm, mmlist, paramap, waitinglist = self.pending_orders[id]
        
        if r['error'] != 0:
            self.logger.debug('The result included an error')
            try:
                curmm = mmlist.pop(0)[1]
                self.put_in_mmq(self.plugins[curmm].inq, id, paramap)
            except IndexError:
                self.logger.debug('No more modules to try, passing error to connector.')
                paramap['error'] = r['error']
                paramap['errortext'] = r['errortext']
                self.replyq.put(Event('DELIVER', paramap))
        else:
            self.logger.debug('Everything fine, delivering results now')
            # cache results
            self.cache.store(copy.copy(r))
            # deliver results
            for o in waitinglist:
                self.replyq.put(Event('DELIVER', self.fill_order(o, r)))
            self.replyq.put(Event('DELIVER', self.fill_order(paramap, r)))
            del self.pending_orders[id]
