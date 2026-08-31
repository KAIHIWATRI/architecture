from sim.cache.policies import LRUPolicy

class TLB:
    def __init__(self, size: int, latency: float):
        self.size = size
        self.latency = latency
        self.entries = {} # virtual_page -> physical_page (dummy)
        self.policy = LRUPolicy()
        
        self.accesses = 0
        self.hits = 0
        self.misses = 0

    def access(self, page_number: int) -> bool:
        """Returns True if TLB hit, False if TLB miss"""
        self.accesses += 1
        
        if page_number in self.entries:
            self.hits += 1
            self.policy.update(page_number, accessed=True)
            return True
        else:
            self.misses += 1
            if len(self.entries) < self.size:
                self.entries[page_number] = True
                self.policy.update(page_number, accessed=False)
            else:
                victim = self.policy.get_victim(list(self.entries.keys()))
                if victim is not None:
                    del self.entries[victim]
                self.entries[page_number] = True
                self.policy.update(page_number, accessed=False)
            return False

    def invalidate(self, page_number: int):
        if page_number in self.entries:
            del self.entries[page_number]
            # Ideally update policy too, but LRU handles missing items gracefully

    def get_stats(self):
        return {
            'accesses': self.accesses,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hits / self.accesses if self.accesses > 0 else 0,
            'latency': self.latency
        }
