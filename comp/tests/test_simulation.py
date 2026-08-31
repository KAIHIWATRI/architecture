import pytest
from sim.cache.policies import LRUPolicy, FIFOPolicy, RandomPolicy
from sim.virtual_memory.page_replacement import OptimalPageReplacement
from sim.cache.cache import Cache
from sim.core.simulator import Simulator
from sim.storage.storage_models import STORAGE_MODELS

def test_cache_lru():
    policy = LRUPolicy()
    policy.update(1)
    policy.update(2)
    policy.update(3)
    policy.update(1, accessed=True)
    # Order should be 2, 3, 1
    assert policy.get_victim([1, 2, 3]) == 2

def test_optimal_page_replacement():
    policy = OptimalPageReplacement()
    # References: 1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5
    future_refs = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    valid_pages = [1, 2, 3] # Currently in memory
    
    # At index 0 (accessing 1), if we need to replace and valid pages are 1,2,3
    # Next use: 1 (at 0), 2 (at 1), 3 (at 2) -> Farthest is 3 (at 2)
    victim = policy.get_victim(valid_pages, future_refs, current_index=0)
    assert victim == 3

def test_cache_hit_miss():
    cache = Cache('L1', 128, 64, 2, 1.0, 'LRU')
    # 2 blocks per set. Size 128 / 64 = 2 blocks total. So 1 set.
    
    hit1 = cache.access(0)   # Block 0 -> Miss
    hit2 = cache.access(64)  # Block 1 -> Miss
    hit3 = cache.access(0)   # Block 0 -> Hit
    hit4 = cache.access(128) # Block 2 -> Miss, evicts Block 1 (LRU)
    
    assert not hit1
    assert not hit2
    assert hit3
    assert not hit4
    
    assert cache.hits == 1
    assert cache.misses == 3

def test_simulator_basic():
    config = {
        'l1_size': 1024,
        'l1_assoc': 2,
        'l1_latency': 1.0,
        'block_size': 64,
        'cache_policy': 'LRU',
        'ram_size': 1024 * 1024,
        'ram_latency': 100.0,
        'use_virtual_memory': False
    }
    
    sim = Simulator(config)
    workload = [0, 64, 128, 0, 64, 1024]
    sim.run(workload)
    
    stats = sim.get_stats()
    assert stats['total_time_ns'] > 0
    assert stats['caches'][0]['hits'] == 2 # 0 and 64 hit the second time
    assert stats['caches'][0]['misses'] == 4
    assert stats['ram']['accesses'] == 4 # RAM is accessed on cache miss
