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
from unisono.order import Order, InternalOrder, RemoteOrder
from unisono.connector_interface import XMLRPCServer, XMLRPCReplyHandler
from unisono.event import Event
from unisono.utils import configuration
from unisono.mmplugins.mmtemplates import MMTemplate, MMMCTemplate, MMServiceTemplate
# RB
from unisono.mission_control import MissionControl, Message, Node
#

import logging, copy
import threading

# TODO: move to an appropriate location
# TODO: work for all IF not only the primary
import socket
def getIpAddresses(): 
    addrList = socket.getaddrinfo(socket.gethostname(), None) 

    ipList=[] 
    for item in addrList:
        if (":" not in item[4][0]):
            ipList.append(item[4][0])
    return ipList

class Scheduler:
    '''
    Schedules periodic/triggerd measurements and cleanup tasks. Think of this as a glorified heapq.
    '''

    class Task:
        def __init__(self, at, interval = 0, finish = None, data = None):
            self.at = at
            self.finish = finish
            self.interval = interval
            self.data = data
        
        def __lt__(self, other):
            return self.at < other.at
    
        def __repr__(self):
            return "Task(at=%r, interval=%r, finish=%r, data=%r)" % (self.at, self.interval, self.finish, self.data)

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
        t = Scheduler.Task(
            int(self.now() + order.parameters["interval"]),
            order.parameters["interval"],
            int(self.now() + order.parameters["lifetime"]),
            order
        )
        heappush(self.tasks, t)
    
    def schedule(self, task):
        """ Add a generic Task (see schedule_order for orders) """
        heappush(self.tasks, task)
        
    def cancel_order(self, conid, orderid):
        """ Mark order as dead and remove it from task list """
        self.parent.logger.debug("Scheduler: cancel_order(%s, %s) - my task list is: %r", conid, orderid, self.tasks)
        for t in self.tasks[:]:
            if isinstance(t.data, Order) and t.data["conid"] == conid and (orderid is None or t.data["orderid"] == orderid):
                t.data.mark_dead()
                self.tasks.remove(t)
        heapify(self.tasks)
        self.parent.logger.debug("Task list is now: %r", self.tasks)
        
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
            self.logger.debug('The next task: %s', nextt)
            if nextt.interval and (not nextt.finish or nextt.at <= nextt.finish):
                nextt.at = self.now() + nextt.interval
                heapreplace(self.tasks, nextt)
            else:
                self.logger.debug('we should delete this task now! %s', nextt)
                heappop(self.tasks)
                if isinstance(nextt.data, dict):
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
        # RB
        # if mc should filter the receivers the list of plugins should be parameters
        self.mc = MissionControl(self.eventq)
        #
        
        # TODO: add bogus task to help signal handling / cache garbage collection
        self.scheduler = Scheduler(self)
        self.init_plugins()
        self.init_database()
        self.start_xmlrpcserver()
        self.start_xmlrpcreplyhandler()

        # memorize local IPs
        self.ips = getIpAddresses()

    def at_exit(self):
        """ to be called at system exit """
        self.logger.debug("Calling destructor for Dispatcher")
        self.cache.save()

    def init_database(self):
        restoreDataBase(self.dataitemprops)
        self.cache = DataBase(self.dataitemprops)
        self.scheduler.schedule(Scheduler.Task(self.scheduler.now(), self.config.getint("Cache", "vacinterval"), finish=None, data="VACDB"))

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
        self.dataitemprops = {}
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

                for n, v in vars(mod).items():
                    if type(v) == type and issubclass(v, MMTemplate):
                        iq = Queue()
                        mm = v(iq, self.eventq)
                        self.logger.debug("created module at this point")
                        self.registerMM(n, mm)
                        mm_thread = threading.Thread(target=mm.run)
                        # Exit the server thread when the main thread terminates
                        mm_thread.setDaemon(True)
                        mm_thread.setName(mm.__class__.__name__)
                        mm_thread.start()
                        self.logger.info("M&M %s loop running in thread: %s", mm.__class__.__name__, mm_thread.name)
                    elif type(v) == type and issubclass(v, MMMCTemplate):
                        orderq = Queue()
                        msgq = Queue()
                        self.logger.debug('dispatcher created orderq %s and msgq %s',orderq, msgq)
                        mm = v(orderq, msgq, self.eventq, self.mc)
    
                        self.registerMMMC(n, mm)
                        mm_thread = threading.Thread(target = mm.run, args = ())
                        # Exit the server thread when the main thread terminates
                        mm_thread.setDaemon(True)
                        mm_thread.setName(mm.__class__.__name__)
                        mm_thread.start()
                        self.logger.info("M&M&MC %s loop running in thread: %s", mm.__class__.__name__, mm_thread.name)
    
                    elif type(v) == type and issubclass(v, MMServiceTemplate):
                        msgq = Queue()
                        self.logger.debug('dispatcher created msgq %s',msgq)
                        mm = v(msgq, self.eventq, self.mc)
    
                        self.registerMMService(n, mm)
                        mm_thread = threading.Thread(target = mm.run, args = ())
                        # Exit the server thread when the main thread terminates
                        mm_thread.setDaemon(True)
                        mm_thread.setName(mm.__class__.__name__)
                        mm_thread.start()
                        self.logger.info("M&M&Service %s loop running in thread: %s", mm.__class__.__name__, mm_thread.name)
            except Exception as e:
                self.logger.error('Could not load plugin %s: %s', p, e)
                continue
        self.logger.info("Plugin initialization done, %i plugins with %i dataitems.", len(self.plugins), len(self.dataitems))
        self.logger.debug('plugin list: %r' % self.plugins)
        self.logger.debug('registered dataitems: %s', self.dataitems)
        self.logger.debug('registered dataitem properties: %s', self.dataitemprops)

    def registerMMMC(self, name, mm):
        # may change that behavior
        self.registerMM(name, mm)

    def registerMMService(self, name, mm):
        # may change that behavior
        self.registerMM(name, mm)

    def registerMM(self, name, mm):
        '''
        To be able to use a M&M plugin, its provided dataitems must be globally
        registered.
        '''
        self.logger.debug("Registrating %s", name)
        self.plugins[name] = mm
        cost = mm.getCost()
        # merge with current dataitem list
        for i in mm.availableDataItems():
            if i.name in self.dataitems.keys():
                self.dataitems[i.name].append((cost, name))
                self.dataitems[i.name].sort()
            else:
                self.dataitems[i.name] = [(cost, name)]
            if i.name not in self.dataitemprops.keys():
                self.dataitemprops[i.name] = i

    def deregisterMM(self, name):
        '''
        deregisterMM removes a M&M from the global register and deactivates it.
        This can be used for runtime module deactivation.
        '''
        self.logger.debug('Unregistering %s', name)
        for i in self.plugins[name].availableDataItems():
            # only delete the correspondent entry
            self.dataitems = [i for i in self.dataitems if i[1] != name]
            if i.name not in self.dataitems.keys():
                del self.dataitemprops[i.name]
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
                self.logger.debug("Cancel order: %s", event.payload)
                self.cancel_order(*event.payload)
            elif event.type == 'SCHED':
                self.logger.debug('scheduler event: %s', event.payload)
                if event.payload == "IDLE":
                    continue
                elif event.payload == "VACDB":
                    self.logger.debug('Thou shallst clean thy cache!')
                    self.cache.vacuum()
                elif isinstance(event.payload, Order):
                    self.process_sched_order(event.payload)
                else:
                    self.logger.warn('Got invalid sched event: %r', event.payload)
            elif event.type == 'ORDER':
                self.logger.debug('order: %s', event.payload)
                self.process_order(event.payload)
            elif event.type == 'RESULT':
                self.logger.debug('result. %s', event.payload)
                self.process_result(event.payload)
            elif event.type == 'FINISHED':
                self.logger.debug('finished %s', event.payload)
                self.replyq.put(event)
#RB
            elif event.type == 'MESSAGE':
                self.logger.debug('message: %s', event.payload.msgtype)
                self.queue_message(event.payload)
            elif event.type == 'MESSAGE_OUT':
                self.logger.debug('messageout: %s', event.payload.msgtype)
                self.mc.put(event.payload)
            elif event.type == 'INTERN_ORDER':
                # handle it like a normal order, but get the result and put it into a response message
                self.process_order(event.payload)
#
            else:
                self.logger.warn('Internal error: unknown event %r, discarding.' % (event.type,))

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
        neword["parent"] = order
        neword["type"] = "oneshot"
        self.process_order(neword)

    def process_order(self, order):
        if not order.isalive():
            return
        # get all possible m&m's
        order['mmlist'] = [i[1] for i in self.dataitems[order.dataitem]]
        # handle periodic and triggered
        if order.type in ("periodic", "triggered"):
            self.logger.debug('Got a periodic or triggered order')
            order.append_item('subid', - 1)
            self.scheduler.schedule_order(order)
            self.process_sched_order(order)
            return
        if self.satisfy_from_cache(order):
            return
        # handle remote orders
        if not order.identifierlist["identifier1"] in self.ips:
           self.logger.debug("=========  yeah, got a remote order, pushing it out ========")
           # create message
           snd_ip = self.ips[0]
           snd_id = 'Dispatcher'
           rcv_ip = order['identifier1']
           rcv_id = 'Dispatcher'
           sender = Node(snd_ip,snd_id)
           receiver = Node(rcv_ip,rcv_id)
           r = RemoteOrder(sender, receiver, order)
           #force orderid to be the same as the original order!
           self.logger.debug("remote order: %s",r)
           message = Message(sender, receiver, "REMOTE_ORDER",r)
           # save it to pending orders
           id = order['conid'], order.orderid
           curmm = order['mmlist'].pop()
           self.pending_orders[id] = (curmm, [], order, [])
           self.eventq.put(Event("MESSAGE_OUT",message))
           # send out to remote host
           return
        elif self.aggregate_order(order):
            return
        else:
            self.queue_order(order)

    def satisfy_from_cache(self, order):
        self.logger.debug('trying cache')
        try:
            result = self.cache.check_for(order)
            if order.istriggermatch(result[order.dataitem]):
                order.update(result)
                # for at least the ariba connector (deprecated)
                order.append_item('result',order[order.dataitem])
    #            self.logger.debug('result from cache: %s', result)
    #            self.logger.debug('updated order: %s', order)
                order['error'] = 0
                order['errortext'] = 'Everything went fine'
                o = order
                r = order[order.dataitem]
                if issubclass(type(o), InternalOrder):
                    receiver = Node(None,order['moduleid'])
                    message = Message(None,receiver,'RESULT',None,{order.dataitem:r})
                    self.put_in_mmmcq(self.plugins[o['moduleid']].msgq, o['moduleid'], message)
                    self.logger.info("queue_message into msgq %s", self.plugins[o['moduleid']].msgq)
                elif issubclass(type(o), RemoteOrder):
                        sender = Node(o['senderip'], o['senderid'])
                        receiver = Node(o['receiverip'], o['receiverid'])
                        o['errorcode'] = 0
                        o['result'] = r[o['dataitem']]
                        msgtype = 'RESULT'
                        payload = o
                        outmsg = Message(sender,receiver,msgtype,payload,r[o['dataitem']])
                        # queues response in dispatcher queue
                        ev = Event("MESSAGE_OUT",outmsg)
                        self.eventq.put(ev)
                else:
                    self.replyq.put(Event('DELIVER', order))
            if order['finished']:
                self.logger.debug('Finished Order, create FINISHED event')
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
        
        if 'moduleid' in order:
            req['moduleid'] = order['moduleid']
        if 'identifier1' in order:
            req['identifier1'] = order['identifier1']
        if 'identifier2' in order:
            req['identifier2'] = order['identifier2']
        self.logger.debug(req)
        
        #self.logger.debug['stripped request: %s', req]
        # queue request
        mmq.put(req)

# RB
    def put_in_mmmcq(self, q, id, request):
        q.put(request)
#

    def queue_order(self, order):
        self.logger.debug('trying queue')
        if issubclass(type(order), InternalOrder):
            id = order['moduleid'], order.orderid
        elif issubclass(type(order), RemoteOrder):
            id = 'mc', order.orderid
        else:
            id = order['conid'], order.orderid
        curmm = order['mmlist'].pop()
        self.pending_orders[id] = (curmm, order['mmlist'], order, [])
        self.put_in_mmq(self.plugins[curmm].orderq, id, order)
        return

# RB
    def queue_message(self, message):
        if message.msgtype == 'REMOTE_ORDER':
            self.process_order(message.payload)
            
        elif message.msgtype == "RESULT":
            self.logger.info("queue_message %s",message.msgtype)
            id = message.sender.id # maybe change that
            #self.pending_messages[id] = (curmm, mmlist, message, [])
            if message.tomsgqueue == 1:
                # default case
                self.logger.debug("running tomsgqueue")
                self.logger.debug(message.sender.ip)
                self.logger.debug(message.receiver.ip)
                self.logger.debug(message.payload)
                if message.receiver.id == "Dispatcher":
                    self.logger.debug("result for Dispatcher")
                    self.eventq.put(Event('RESULT', [self.__class__.__name__, message.payload]))
                else:
                    self.put_in_mmmcq(self.plugins[message.receiver.id].msgq, id, message)
                    self.logger.info("queue_message into msgq %s", self.plugins[message.receiver.id].msgq)
            else:
                self.logger.debug("running tomsgqueue else")
                self.put_in_mmmcq(self.plugins[message.receiver.id].orderq, id, message)
                self.logger.info("queue_message into orderq %s", self.plugins[message.receiver.id].orderq)
                
        else:
            self.logger.info("queue_message %s",message.msgtype)
            id = message.receiver.id # maybe change that
            #self.pending_messages[id] = (curmm, mmlist, message, [])
            if message.tomsgqueue == 1:
                # default case
                self.put_in_mmmcq(self.plugins[message.receiver.id].msgq, id, message)
                self.logger.info("queue_message into msgq %s", self.plugins[message.receiver.id].msgq)
            else:
                self.put_in_mmmcq(self.plugins[message.receiver.id].orderq, id, message)
                self.logger.info("queue_message into orderq %s", self.plugins[message.receiver.id].orderq)
#

    def fill_order(self, order, result):
#        try:
#            order['error'] = result['error']
#            order['errortext'] = result['errortext']
#        except KeyError:
#            order['error'] = 666
#            order['errortext'] = 'error code not in result'
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
        id = ""
        try:
            id = r['id']
        except KeyError:
            id = (r['conid'],r['orderid'])
            self.logger.debug("had to recreate the id: %s", id)
        try:
            # get the orders and get them out of the pending list
            curmm, mmlist, paramap, waitinglist = self.pending_orders.pop(id)
        except KeyError:
            # order has been canceled
            self.logger.debug("Dropping connector %r order %r result" % id)
            return

        if r['error'] != 0:
            self.logger.debug('The result included an error')
            for o in waitinglist + [paramap]:
                if len(o["mmlist"]) > 0:
                    if not self.aggregate_order(o):
                        self.queue_order(o)
                else:
                    o['error'] = r['error']
                    o['errortext'] = r['errortext']
                    
                    if issubclass(type(o), InternalOrder):
                        message = Message(None,None,'ERROR',None,None)
                        self.put_in_mmmcq(self.plugins[o['moduleid']].msgq, o['moduleid'], message)
                        self.logger.info("queue_message into msgq %s", self.plugins[o['moduleid']].msgq)
                    elif issubclass(type(o), RemoteOrder):
                        receiver = Node(o['senderip'], o['senderid'])
                        sender = Node(o['receiverip'], o['receiverid'])
                        o['errorcode'] = -1
                        msgtype = 'ERROR'
                        payload = o
                        outmsg = Message(sender,receiver,msgtype,payload)
                        # queues response in dispatcher queue
                        ev = Event("MESSAGE_OUT",outmsg)
                        self.eventq.put(ev)
                    else:
                        self.replyq.put(Event('DELIVER', o))
                    
                    if o['finished']:
                        self.replyq.put(Event('FINISHED', o))
                try:
                    waitinglist.remove(o)
                except ValueError:
                    pass
        else:
            self.logger.debug('Everything\'s fine, delivering results now')
            # cache results
            try:
                self.cache.store(copy.copy(r))
            except KeyError:
                # result had no timestamp, must be from remote
                # create a current timestamp, should be accurate enough
                r['time'] = system_time()
                self.cache.store(copy.copy(r))
            # deliver results
            for o in waitinglist + [paramap]:
                if o.istriggermatch(r[o.dataitem]):
                    if issubclass(type(o), InternalOrder):
                        message = Message(None,None,'RESULT',None,r)
                        self.put_in_mmmcq(self.plugins[o['moduleid']].msgq, o['moduleid'], message)
                        self.logger.info("queue_message into msgq %s",  self.plugins[o['moduleid']].msgq)
                    elif issubclass(type(o), RemoteOrder):
                        self.logger.debug("It's the result for a remote order")
                        receiver = Node(o['senderip'], o['senderid'])
                        sender = Node(o['receiverip'], o['receiverid'])
                        self.logger.debug("sender: %s", sender.ip)
                        self.logger.debug("receiver: %s", receiver.ip)
                        msgtype = 'RESULT'
                        payload = self.fill_order(o, r)
                        payload['error'] = r['error']
                        payload['errortext'] = r['errortext']
                        payload['errorcode'] = r['errorcode']
                        self.logger.debug("payload %s", o)
                        outmsg = Message(sender,receiver,msgtype,payload,r[o['dataitem']])
                        # queues response in dispatcher queue
                        ev = Event("MESSAGE_OUT",outmsg)
                        self.eventq.put(ev)
                    else:
                        self.replyq.put(Event('DELIVER', self.fill_order(o, r)))
                if o['finished']:
                    self.replyq.put(Event('FINISHED', o))
