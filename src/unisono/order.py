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
             interval (str) in seconds
             lifetime (str) in seconds
    triggered:
            lower_threshold, upper_threshold: trigger watermarks (str)
            
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
                for key in ('lower_threshold', 'upper_threshold'):
                    if key not in self['parameters']:
                        raise OrderKeyMissing(412, "%s needed for triggered orders and not given"%key)
                        try:
                            self['parameters'][key] = int(self['parameters'][key])
                        except (ValueError) as e:
                            raise OrderKeyInvalid(411, "%s parameter invalid"%key) from e

        # NOTE: we don't check dataitem here b/c we don't have the list of valid dataitems at hand

    def isrepeated(self):
        """ Is this Order a spawn point for multiple oneshot orders? """
        return self['type'].lower() in ('periodic', 'triggered')

    def append_item(self,key, value):
        '''
        Append a new item to the order
        '''
        self[key] = value
        
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
    def identifierlist(self):
        ids = {}
        for k,v in self.items():
            if 'identifier' in k:
                ids[k] = v
        return ids

    @property
    def identifier_count(self):
        return len(self.identifier())
    
    @property
    def results(self):
        unneeded = ('type','parameters','dataitem')
        results = {}
        for k,v in self.items():
            if k not in unneeded:
                results[k] = v
        return results
    
    def __repr__(self):
        return "Order(%s)"%(super().__repr__(),)
    
if __name__ == '__main__':
    o = Order(type="oneshot", orderid="GoodOrder", dataitem="CINDERELLA_DWARF_COUNT", foo="bar")
    print("Good:", o)
    print("Bad:")
    o = Order(type="periodic", interval="too cool for int", orderid="BadOrder", dataitem="EVIL_BIT_COUNT")
    