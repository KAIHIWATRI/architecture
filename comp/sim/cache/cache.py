import math
from typing import Optional
from sim.cache.policies import LRUPolicy, FIFOPolicy, RandomPolicy

class Cache:
    def __init__(self, name: str, size_bytes: int, block_size_bytes: int, associativity: int, latency: float, policy_str: str):
        self.name = name
        self.size = size_bytes
        self.block_size = block_size_bytes
        self.associativity = associativity
        self.latency = latency
        
        self.num_blocks = self.size // self.block_size
        if self.associativity == 0: # Fully associative
            self.num_sets = 1
            self.associativity = self.num_blocks
        else:
            self.num_sets = self.num_blocks // self.associativity

        self.index_bits = int(math.log2(self.num_sets))
        self.offset_bits = int(math.log2(self.block_size))
        
        # sets[set_idx] = { tag: block_idx_in_set }
        # To keep track of valid blocks in a set
        self.sets = [{} for _ in range(self.num_sets)]
        
        if policy_str.upper() == 'LRU':
            self.policies = [LRUPolicy() for _ in range(self.num_sets)]
        elif policy_str.upper() == 'FIFO':
            self.policies = [FIFOPolicy() for _ in range(self.num_sets)]
        elif policy_str.upper() == 'RANDOM':
            self.policies = [RandomPolicy() for _ in range(self.num_sets)]
        else:
            self.policies = [LRUPolicy() for _ in range(self.num_sets)]
            
        self.accesses = 0
        self.hits = 0
        self.misses = 0

    def get_set_index(self, address: int) -> int:
        if self.num_sets == 1:
            return 0
        return (address >> self.offset_bits) & ((1 << self.index_bits) - 1)

    def get_tag(self, address: int) -> int:
        return address >> (self.offset_bits + self.index_bits)

    def access(self, address: int) -> bool:
        """Returns True if hit, False if miss"""
        self.accesses += 1
        set_idx = self.get_set_index(address)
        tag = self.get_tag(address)
        
        cache_set = self.sets[set_idx]
        policy = self.policies[set_idx]
        
        if tag in cache_set:
            self.hits += 1
            policy.update(tag, accessed=True)
            return True
        else:
            self.misses += 1
            if len(cache_set) < self.associativity:
                cache_set[tag] = True
                policy.update(tag, accessed=False)
            else:
                valid_tags = list(cache_set.keys())
                victim_tag = policy.get_victim(valid_tags)
                if victim_tag is not None:
                    del cache_set[victim_tag]
                    # Also need to remove victim from policy if it keeps track, 
                    # but LRU/FIFO will naturally overwrite or we can just ignore it.
                cache_set[tag] = True
                policy.update(tag, accessed=False)
            return False
            
    def get_stats(self):
        return {
            'accesses': self.accesses,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hits / self.accesses if self.accesses > 0 else 0,
            'miss_rate': self.misses / self.accesses if self.accesses > 0 else 0,
            'latency': self.latency
        }
