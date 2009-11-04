#-*- coding: utf-8 -*-
'''
dataitem.py

 Created on: Jul 14th, 2009
 Authors: zxmoo46
 
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
import time
logger = logging.getLogger(__file__)

class OrderError(ValueError):
    """ An Error with a numeric status code, much like EnvironmentError's errno """
    def __init__(self, status, *args, **kwargs):
        self.status = status
        super().__init__(*args, **kwargs)

class OrderKeyMissing(OrderError):
    pass

class OrderKeyInvalid(OrderError):
    pass

class Order(dict):
    '''
    An UNISONO order™
    
    This will check for all the required fields on __init__ as good as it can.
    If any of them is missing or invalid you'll get an OrderError.
    To access the numeric error code use OrderError.status.
    
    Fields:
         type (str): 'oneshot', 'periodic', 'triggered' 
         dataitem (str): a valid dataitem 
         orderid (str): the unique orderid 
    periodic or triggered:
             interval (str) in seconds
             lifetime (str) in seconds
    triggered:
        either:
            - a onChange triggered order
            - lower_threshold, upper_threshold: trigger watermarks (str)
            
    Additional fields are a number of identifiers:
        identifierN with N in (1,2) (str) identifier of the target
                                          (e.g. IP address)
    
    For network measurements the first identifier is always the source of the
    measurement, the second is the target.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key in ('orderid', 'type', 'dataitem'):
            if key not in self:
                raise OrderKeyMissing(400, "%s needed and not given"%key)
            if not isinstance(self[key], str):
                raise OrderKeyInvalid(400, 'Invalid value type for key %s: %s'%(key, type(self[key])))
        if self.type.lower() not in ('oneshot', 'periodic', 'triggered'):
            raise OrderKeyInvalid(400, 'Order type %r unkown'%self.type)
        if self.isrepeated():
            if 'parameters' not in self:
                raise OrderKeyMissing(400, "%s needed and not given"%key)
            for key in ('lifetime','interval'):
                if key not in self['parameters']:
                    raise OrderKeyMissing(412, "%s needed for repeated orders and not given"%key)
                else:
                    try:
                        self['parameters'][key] = int(self['parameters'][key])
                    except (ValueError) as e:
                        raise OrderKeyInvalid(411, "%s parameter invalid"%key) from e
            if self.type == "triggered":
                # check: either both thresholds are defined or neither
                keys = ('lower_threshold', 'upper_threshold')
                if not set(keys).isdisjoint(set(self.keys())):
                    for key in keys:
                        if key not in self['parameters']:
                            raise OrderKeyMissing(412, "%s needed for triggered orders and not given"%key)
                            try:
                                self['parameters'][key] = float(self['parameters'][key])
                            except (ValueError) as e:
                                raise OrderKeyInvalid(411, "%s parameter invalid"%key) from e
        self['finished']= False

        # NOTE: we don't check dataitem here b/c we don't have the list of valid dataitems at hand

    def isrepeated(self):
        """ Is this Order a spawn point for multiple oneshot orders? """
        return self['type'].lower() in ('periodic', 'triggered')

    def istriggermatch(self, measured_value):
        """ check if this order is triggered and value fits trigger criteria. Return True for untriggered orders. """
        if not (issubclass(type(self), InternalOrder) or issubclass(type(self), RemoteOrder)):
            logger.debug("istriggermatch called (conid, orderid, subid) = (%s, %s, %s)",self.conid, self.orderid, self.get("subid", None))
        if not ("parent" in self and self["parent"].type == "triggered"):
            return True
        p = self["parent"]
        params = p["parameters"]
        if "lower_threshold" in params:
            logger.debug("istriggermatch for thresholds")
            try:
                v = float(measured_value)
            except:
                return False
            oldval = p.get("lastval", True)
            val_in_range = params["lower_threshold"] <= v <= params["upper_threshold"]
            p["lastval"] = val_in_range
            logger.debug("istriggermatch val_in_range old: %s, now: %s", oldval, val_in_range)
            return oldval ^ val_in_range
        else:
            oldval = p.get("lastval", None)
            p["lastval"] = measured_value
            return oldval != measured_value

    def isalive(self):
        if "alive" in self:
            return self["alive"]
        elif "parent" in self and "alive" in self["parent"]:
            return self["parent"]["alive"]
        else:
            return True

    def append_item(self, key, value):
        '''
        Append a new item to the order
        '''
        self[key] = value

    def get_item(self, key):
        '''
        get the value of key
        '''
        return self[key]

    def mark_dead(self):
        self["alive"] = False
        
    @property
    def parameters(self):
        return self['parameters']

    @property
    def type(self):
        return self["type"]

    @property
    def dataitem(self):
        return self["dataitem"]

    @property
    def orderid(self):
        return self["orderid"]

    @property
    def conid(self):
        return self["conid"]

    @property
    def identifierlist(self):
        ids = {}
        for k,v in self.items():
            if 'identifier' in k:
                ids[k] = v
        return ids

    @property
    def identifier_count(self):
        return len(self.identifierlist)
    
    @property
    def results(self):
        unneeded = ('type', 'parameters', 'dataitem', 'finished', 'mmlist', 'parent')
        results = {}
        for k,v in self.items():
            if k not in unneeded:
                results[k] = v
        return results
    
    def __repr__(self):
        return "Order(%s)"%(super().__repr__(),)

class InternalOrder(Order):
    def __init__(self, module_id, *args, **kwargs):
        order_id = time.time()
        kwargs.update({'orderid':str(order_id),'moduleid':str(module_id),'type':'oneshot'})
        super().__init__(*args, **kwargs)


class RemoteOrder(Order):
    def __init__(self, sender, receiver, *args, **kwargs):
        order_id = time.time()
        kwargs.update({'orderid':str(order_id),'senderip':str(sender.ip), 'senderid':str(sender.id), 'receiverip':str(receiver.ip), 'receiverid':str(receiver.id),'type':'oneshot'})
        super().__init__(*args, **kwargs)
