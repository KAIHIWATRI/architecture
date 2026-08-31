import random

class WorkloadGenerator:
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

    def generate_sequential(self, start_address: int, count: int, stride: int = 4):
        return [start_address + i * stride for i in range(count)]

    def generate_random(self, min_address: int, max_address: int, count: int, alignment: int = 4):
        accesses = []
        for _ in range(count):
            addr = random.randint(min_address, max_address)
            addr = (addr // alignment) * alignment
            accesses.append(addr)
        return accesses

    def generate_locality(self, base_address: int, count: int, locality_range: int = 1024, jump_probability: float = 0.1, alignment: int = 4):
        accesses = []
        current_base = base_address
        for _ in range(count):
            if random.random() < jump_probability:
                current_base = random.randint(0, 2**30) # Jump somewhere else
            
            # Normal distribution around current base for spatial locality
            offset = int(random.gauss(0, locality_range / 4))
            addr = current_base + offset
            
            # Ensure positive and aligned
            addr = max(0, addr)
            addr = (addr // alignment) * alignment
            accesses.append(addr)
        return accesses

    def generate_stress(self, count: int, cache_size: int):
        # Generates a workload that repeatedly accesses exactly cache_size + 1 elements
        # This causes thrashing for LRU and FIFO
        accesses = []
        for i in range(count):
            accesses.append((i % (cache_size + 64)) * 64)
        return accesses
