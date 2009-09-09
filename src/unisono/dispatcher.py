# -*- coding: utf-8 -*-
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
from heapq import heappush, heapreplace, heapify, heappop
from queue import Queue, Empty
from time import time as system_time
from unisono.db import DataBase, restoreDataBase
from unisono.db import NotInCacheError
from unisono.order import Order
from unisono.connector_interface import XMLRPCServer, XMLRPCReplyHandler
from unisono.event import Event
from unisono.utils import configuration
from unisono.mmplugins.mmtemplates import MMTemplate

import logging, copy
import threading


class Scheduler:
    '''
    Schedules periodic/triggerd measurements and cleanup tasks. Think of this as a glorified heapq.
    '''

    class Task:
        def __init__(self, at, finish, data):
            self.at = at
            self.finish = finish
            self.data = data
        
        def __lt__(self, other):
            return self.at < other.at
    
        def __repr__(self):
            return "Task(at=%r, finish=%r, data=%r)" % (self.at, self.finish, self.data)

    def __init__(self, parent):
        """ The parent object is a dispatcher. """
        self.logger = logging.getLogger(self.__class__.__name__)
        #self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.parent = parent
        self.queue = parent.eventq
        self.tasks = []

    def now(self):
        return int(system_time())

    def schedule_order(self, order):
        """ Add an order to the task list. """
        t = Scheduler.Task(int(self.now() + order.parameters["interval"]), int(self.now() + order.parameters["lifetime"]), order)
        heappush(self.tasks, t)
        
    def cancel_order(self, conid, orderid):
        self.tasks = [t for t in self.tasks if "orderid" not in t.data or not (t.data["conid"] == conid and (orderid is None or t.data["orderid"] == orderid))]
        heapify(self.tasks)

        
    def get(self):
        """ Get event, either from schedule or from outside world """
        # On empty scheduler, just wait for event
        if not self.tasks:
            return self.queue.get()
        # else wait till next task
        nextt = self.tasks[0]
        wait = max(0, nextt.at - self.now())
        try:
            ev = self.queue.get(timeout=wait)
        except Empty:
            ev = Event("SCHED", nextt.data)
            nextt.at = self.now() + ev.payload.parameters["interval"]
            self.logger.debug('The next task: %s', nextt)
            if nextt.at <= nextt.finish:
                heapreplace(self.tasks, nextt)
            else:
                self.logger.debug('we should delete this task now! %s', nextt)
                heappop(self.tasks)
                nextt.data['finished']= True
        return ev

class Dispatcher:
    '''
    This is the unisono event loop with associated helper functions.
    
    It will listen on the input queue for events and dispatch them to
    it's subsystems as appropriate.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        self.config = configuration.get_configparser()
        
        self.pending_orders = {}
        self.eventq = Queue()
        # TODO: add bogus task to help signal handling / cache garbage collection
        self.scheduler = Scheduler(self)
        self.init_database()
        self.start_xmlrpcserver()
        self.start_xmlrpcreplyhandler()
        self.init_plugins()
        
    def __del__(self):
        self.logger.debug("Calling destructor for Dispatcher")
        self.cache.save()

    def init_database(self):
        restoreDataBase()
        self.cache = DataBase()

    def start_xmlrpcserver(self):
        # TODO: check whether XMLRPCserver is already running
        self.xsrv = XMLRPCServer(self.eventq, self)

    def start_xmlrpcreplyhandler(self):
        self.replyq = Queue()
        xrh = XMLRPCReplyHandler(self.xsrv.conmap, self.replyq, self.eventq)
        
    def init_plugins(self):
        # list of registered plugins with their queue and object
        self.plugins = {}
        # list of dataitems with the registered plugin and its cost
        self.dataitems = {}
        # initialize M&Ms

        try:
            active_plugins = self.config.get('M&Ms', 'active_plugins')
            self.logger.info('Loading plugins: %s', active_plugins)
        except:
            self.logger.info('No plugins configured, loading defaults.')
            active_plugins = 'cvalues'
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
                    mm_thread.setName(mm.__class__.__name__)
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
            event = self.scheduler.get()
            self.logger.debug('got an event: %s', event.type)
            if event.type == 'CACHE':
                pass
            elif event.type == 'CANCEL':
                self.cancel_order(*event.payload)
            elif event.type == 'SCHED':
                self.logger.debug('scheduler event: %s', event.payload)
                if event.payload == "IDLE":
                    continue
                self.process_sched_order(event.payload)
            elif event.type == 'ORDER':
                self.logger.debug('order: %s', event.payload)
                self.process_order(event.payload)
            elif event.type == 'RESULT':
                self.logger.debug('result. %s', event.payload)
                self.process_result(event.payload)
#            elif event.type == 'FINISHED':
#                self.logger.debug('finished %s', event.payload)
#                self.replyq.put(event)
            else:
                self.logger.debug('Got an unknown event %r, discarding.' % (event.type,))

    def cancel_order(self, conid, orderid=None):
        """ 
        Cancel an order (or, if no orderid is given, all orders belonging to one connector).
        """
        self.scheduler.cancel_order(conid, orderid)
        # TODO: cancel one-shot orders. BC of order aggregation and threaded MM's,
        # this is not as simple as it sounds.

    def process_sched_order(self, order):
        order["subid"] += 1
        neword = copy.copy(order)
        neword["type"] = "oneshot"
        self.process_order(neword)

    def process_order(self, order):
        # get all possible m&m's
        order['mmlist'] = [i[1] for i in self.dataitems[order.dataitem]]
        # sanity checks
        if order.type in ("periodic", "triggered"):
            self.logger.debug('Got a periodic or triggered order')
            order.append_item('subid', - 1)
            self.scheduler.schedule_order(order)
            self.process_sched_order(order)
            return
        if self.satisfy_from_cache(order):
            return
        elif self.aggregate_order(order):
            return
        else: 
            self.queue_order(order)

    def satisfy_from_cache(self, order):
        self.logger.debug('trying cache')
        try:
            result = self.cache.check_for(order)
            order.update(result)
            # for at least the ariba connector (deprecated)
            order.append_item('result',order[order.dataitem])
#            self.logger.debug('result from cache: %s', result)
#            self.logger.debug('updated order: %s', order)
            order['error'] = 0
            order['errortext'] = 'Everything went fine'
            self.replyq.put(Event('DELIVER', order))
            if order['finished']:
                self.replyq.put(Event('FINISHED', order))
            self.logger.debug('cache hit')
            return True
        except NotInCacheError:
            return False

    def aggregate_order(self, order):
        self.logger.debug('trying aggregation')
        for curmm, mmlist, paramap, waitinglist in self.pending_orders.values():
            if curmm in order['mmlist']:
                c = order.identifier_count
                idlist  = order.identifierlist
                id1 = idlist['identifier1']
                if c > 1:
                    id2 = idlist['identifier2']
                else:
                    id2 = None
                if id1 is not None and id1 != paramap.get("identifier1", None) or \
                    id2 is not None and id2 != paramap.get("identifier2", None):
                    return False
                # delete the curmm from the mmlist for this aggregated order
                order['mmlist'].remove(curmm)
                waitinglist.append(order)
                self.logger.info('aggregated the order with already queued order')
                return True
        return False

    def put_in_mmq(self, mmq, id, order):
        # create request for MM
        req = order.identifierlist
        req['id'] = id
        #self.logger.debug['stripped request: %s', req]
        # queue request
        mmq.put(req)

    def queue_order(self, order):
        self.logger.debug('trying queue')
        id = order['conid'], order.orderid
        curmm = order['mmlist'].pop()
        self.pending_orders[id] = (curmm, order['mmlist'], order, [])
        self.put_in_mmq(self.plugins[curmm].inq, id, order)
        return

    def fill_order(self, order, result):
        self.logger.debug('order: %s result: %s',type(order),type(result))
        try:
            di = order.dataitem
            order.append_item(di,result[di])
            # for at least the ariba connector (deprecated)
            order.append_item('result',result[di])
        except KeyError:
            order['error'] = 666
            order['errortext'] = 'dataitem not in result'
        try:
            del(order['mmlist'])
        except KeyError:
            pass
        return order

    def trigger_match(self,order,result):
        self.logger.debug('checking trigger now')
        return true

    def process_result(self, result):
        self.logger.debug('trying result processing')
        mm = result[0]
        r = result[1]
        id = r['id']
        try:
            # get the orders and get them out of the pending list
            curmm, mmlist, paramap, waitinglist = self.pending_orders.pop(id)
            self.logger.debug("aggregations: %s %s %s %s",
                              curmm, mmlist, paramap, waitinglist)
            self.logger.debug("agg count: %i", len(waitinglist))
        except KeyError:
            # order has been canceled
            self.logger.debug("Dropping connector %r order %r result" % id)
            return

        if r['error'] != 0:
            self.logger.debug('The result included an error')
            for o in waitinglist[:]:
                if len(o["mmlist"]) > 0:
                    if not self.aggregate_order(o):
                        self.queue_order(o)
                else:
                    self.logger.debug('No more modules to try, passing error to connector.')
                    o['error'] = r['error']
                    o['errortext'] = r['errortext']
                    self.replyq.put(Event('DELIVER', o))
                    if paramap['finished']:
                        self.replyq.put(Event('FINISHED', o))
                waitinglist.remove(o)
                
            if len(mmlist) > 0:
                if not self.aggregate_order(paramap):
                    self.queue_order(paramap)
            else:
                self.logger.debug('No more modules to try, passing error to connector.')
                paramap['error'] = r['error']
                paramap['errortext'] = r['errortext']
                self.replyq.put(Event('DELIVER', paramap))
                if paramap['finished']:
                    self.replyq.put(Event('FINISHED', paramap))
        else:
            self.logger.debug('Everything\'s fine, delivering results now')
            # cache results
            self.cache.store(copy.copy(r))
            # deliver results
            for o in waitinglist:
                # check trigger
                if (o.type != 'triggered') or (o.type == 'triggered' and self.trigger_match(o,r)):
                    self.replyq.put(Event('DELIVER', self.fill_order(o, r)))
                    if o['finished']:
                        self.replyq.put(Event('FINISHED', o))
            # check trigger
            if (paramap.type != 'triggered') or (paramap.type == 'triggered' and self.trigger_match(paramap,r)):
                self.replyq.put(Event('DELIVER', self.fill_order(paramap, r)))
                if paramap['finished']:
                    self.replyq.put(Event('FINISHED', paramap))
