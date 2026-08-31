from typing import List, Dict
from sim.cache.cache import Cache
from sim.memory.ram import RAM
from sim.virtual_memory.tlb import TLB
from sim.virtual_memory.page_table import PageTable
from sim.storage.storage_models import StorageModel

class Simulator:
    def __init__(self, config: Dict):
        self.config = config
        
        # Initialize Cache Hierarchy
        self.caches = []
        if config.get('l1_size', 0) > 0:
            self.caches.append(Cache('L1', config['l1_size'], config['block_size'], config['l1_assoc'], config['l1_latency'], config['cache_policy']))
        if config.get('l2_size', 0) > 0:
            self.caches.append(Cache('L2', config['l2_size'], config['block_size'], config['l2_assoc'], config['l2_latency'], config['cache_policy']))
        if config.get('l3_size', 0) > 0:
            self.caches.append(Cache('L3', config['l3_size'], config['block_size'], config['l3_assoc'], config['l3_latency'], config['cache_policy']))
            
        # Initialize RAM
        self.ram = RAM(config['ram_size'], config['ram_latency'])
        
        # Initialize Virtual Memory
        self.use_virtual_memory = config.get('use_virtual_memory', False)
        if self.use_virtual_memory:
            self.tlb = TLB(config['tlb_size'], config['tlb_latency']) if config.get('tlb_size', 0) > 0 else None
            self.page_table = PageTable(config['page_size'], config['ram_size'], config['page_replacement_policy'])
            self.storage = config['storage_model'] # This should be a StorageModel instance
        else:
            self.tlb = None
            self.page_table = None
            self.storage = None
            
        self.trace = []
        self.total_time_ns = 0.0

    def run(self, workload: List[int], generate_trace: bool = False):
        if self.use_virtual_memory and self.page_table:
            self.page_table.set_future_references(workload)
            
        for i, address in enumerate(workload):
            trace_entry = {
                'access_num': i + 1,
                'address': address,
                'events': [],
                'latency': 0.0
            }
            
            latency = 0.0
            page_fault = False
            
            # 1. Address Translation (Virtual Memory)
            if self.use_virtual_memory:
                page_number = self.page_table.get_page_number(address)
                
                # Check TLB
                tlb_hit = False
                if self.tlb:
                    latency += self.tlb.latency
                    if self.tlb.access(page_number):
                        tlb_hit = True
                        trace_entry['events'].append('TLB: HIT')
                    else:
                        trace_entry['events'].append('TLB: MISS')
                
                # If TLB miss or no TLB, check Page Table in RAM
                if not tlb_hit:
                    # Page table walk requires RAM access
                    latency += self.ram.access()
                    
                    if self.page_table.access(address):
                        trace_entry['events'].append('Page Table: HIT')
                    else:
                        trace_entry['events'].append('Page Table: MISS')
                        trace_entry['events'].append('Page Fault: YES')
                        page_fault = True
                        
                        # Handle Page Fault (Storage Access)
                        latency += self.storage.read_page(self.page_table.page_size)
                        # Assume we also write back a dirty page (simplified for simulation)
                        latency += self.storage.write_page(self.page_table.page_size)
                        
                        # Once page is in RAM, we would update TLB
                        if self.tlb:
                            self.tlb.access(page_number) # Force a hit to populate
            
            # 2. Cache Hierarchy Access
            cache_hit = False
            for cache in self.caches:
                latency += cache.latency
                if cache.access(address):
                    trace_entry['events'].append(f'{cache.name}: HIT')
                    cache_hit = True
                    break
                else:
                    trace_entry['events'].append(f'{cache.name}: MISS')
                    
            # 3. Main Memory Access (if missed all caches)
            if not cache_hit:
                latency += self.ram.access()
                trace_entry['events'].append('RAM: HIT') # Data fetched from RAM
                
            trace_entry['latency'] = latency
            self.total_time_ns += latency
            
            if generate_trace and i < 100: # Limit trace size
                self.trace.append(trace_entry)

    def get_stats(self):
        stats = {
            'total_time_ns': self.total_time_ns,
            'caches': [c.get_stats() for c in self.caches],
            'ram': self.ram.get_stats(),
        }
        if self.use_virtual_memory:
            stats['virtual_memory'] = {
                'tlb': self.tlb.get_stats() if self.tlb else None,
                'page_table': self.page_table.get_stats(),
                'storage': self.storage.get_stats()
            }
        return stats
