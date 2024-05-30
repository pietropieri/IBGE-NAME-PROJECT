from collections import OrderedDict

class CacheDict:
    def __init__(self, max_size):
        self.max_size = max_size
        self.cache = OrderedDict()
    
    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)
    
    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        else:
            return None
    
    def __repr__(self):
        return str(self.cache)

