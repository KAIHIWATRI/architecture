from sim.virtual_memory.page_replacement import LRUPageReplacement, FIFOPageReplacement, OptimalPageReplacement

class PageTable:
    def __init__(self, page_size_bytes: int, physical_memory_size: int, replacement_policy: str):
        self.page_size = page_size_bytes
        self.physical_memory_size = physical_memory_size
        self.num_physical_pages = self.physical_memory_size // self.page_size
        
        self.page_table = {} # virtual_page -> physical_page
        self.physical_pages_in_use = []
        
        policy_str = replacement_policy.upper()
        if policy_str == 'LRU':
            self.policy = LRUPageReplacement()
        elif policy_str == 'FIFO':
            self.policy = FIFOPageReplacement()
        elif policy_str == 'OPTIMAL':
            self.policy = OptimalPageReplacement()
        else:
            self.policy = FIFOPageReplacement()
            
        self.accesses = 0
        self.hits = 0
        self.faults = 0
        self.pages_loaded = 0
        self.pages_evicted = 0
        
        self.future_references = [] # Used for Optimal policy
        self.current_access_index = 0

    def set_future_references(self, memory_accesses):
        # Convert addresses to page numbers
        self.future_references = [addr // self.page_size for addr in memory_accesses]
        self.current_access_index = 0

    def get_page_number(self, address: int) -> int:
        return address // self.page_size

    def access(self, address: int) -> bool:
        """Returns True if page hit (present in RAM), False if page fault"""
        self.accesses += 1
        page_number = self.get_page_number(address)
        
        if page_number in self.page_table:
            self.hits += 1
            self.policy.update(page_number, accessed=True)
            self.current_access_index += 1
            return True
        else:
            self.faults += 1
            self.pages_loaded += 1
            
            if len(self.physical_pages_in_use) < self.num_physical_pages:
                self.physical_pages_in_use.append(page_number)
                self.page_table[page_number] = len(self.physical_pages_in_use) - 1
                self.policy.update(page_number, accessed=False)
            else:
                self.pages_evicted += 1
                victim = self.policy.get_victim(
                    self.physical_pages_in_use, 
                    self.future_references, 
                    self.current_access_index
                )
                if victim is not None:
                    self.physical_pages_in_use.remove(victim)
                    del self.page_table[victim]
                
                self.physical_pages_in_use.append(page_number)
                self.page_table[page_number] = 0 # Dummy physical page
                self.policy.update(page_number, accessed=False)
                
            self.current_access_index += 1
            return False

    def get_stats(self):
        return {
            'accesses': self.accesses,
            'hits': self.hits,
            'faults': self.faults,
            'fault_rate': self.faults / self.accesses if self.accesses > 0 else 0,
            'pages_loaded': self.pages_loaded,
            'pages_evicted': self.pages_evicted
        }
