#-*- coding: utf-8 -*-

'''
Created on 14.07.2009

@author: zxmoo46
'''

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
         type (str): 'oneshot', 'periodic' or 'triggered' 
         dataitem (str): a valid dataitem 
         orderid (str): the unique orderid 
    periodic or triggered:
             interval (int)
    triggered:
            low, high: trigger watermarks
    '''

    def __init__(self, *args, **kwargs):
        # TODO: this still has to migrate to the new calling convention
        super().__init__(*args, **kwargs)
        for key in ('orderid', 'type', 'dataitem'):
            if key not in self:
                raise OrderKeyMissing(400, "%s needed and not given"%key)
            if not isinstance(self[key], str):
                raise OrderKeyInvalid(400, 'Invalid value type for key %s: %s'%(key, type(self[key])))
        if self.type not in ('oneshot', 'periodic', 'triggered'):
            raise OrderKeyInvalid(400, 'Order type %r unkown'%self.type)
        if self.isrepeated():
            try:
                self.interval = int(self["interval"])
            except (KeyError, ValueError, TypeError) as e:
                raise OrderKeyInvalid(411, "Interval paramater invalid") from e
            if self.type == "triggered":  
                for key in ('low', 'high'):
                    if key not in self:
                        raise OrderKeyMissing(412, "%s needed for triggered orders and not given"%key)
        # NOTE: we don't check dataitem here b/c we don't have the list of valid dataitems at hand

    def isrepeated(self):
        """ Is this Order a spawn point for multiple oneshot orders? """
        return self['type'] in ('periodic', 'triggered')

    @property
    def type(self):
        return self["type"]

    @property
    def dataitem(self):
        return self["dataitem"]

    @property
    def orderid(self):
        return self["orderid"]

    def __repr__(self):
        return "Order(%s)"%(super().__repr__(),)
    
if __name__ == '__main__':
    o = Order(type="oneshot", orderid="GoodOrder", dataitem="CINDERELLA_DWARF_COUNT", foo="bar")
    print("Good:", o)
    print("Bad:")
    o = Order(type="periodic", interval="too cool for int", orderid="BadOrder", dataitem="EVIL_BIT_COUNT")
    