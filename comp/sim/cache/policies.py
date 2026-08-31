import random

class CachePolicy:
    def __init__(self):
        pass

    def update(self, block_index, accessed=True):
        pass

    def get_victim(self, valid_blocks):
        raise NotImplementedError

class LRUPolicy(CachePolicy):
    def __init__(self):
        super().__init__()
        self.access_order = []

    def update(self, block_index, accessed=True):
        if block_index in self.access_order:
            self.access_order.remove(block_index)
        self.access_order.append(block_index)

    def get_victim(self, valid_blocks):
        for block in self.access_order:
            if block in valid_blocks:
                return block
        if valid_blocks:
            return valid_blocks[0]
        return None

class FIFOPolicy(CachePolicy):
    def __init__(self):
        super().__init__()
        self.insertion_order = []

    def update(self, block_index, accessed=True):
        if not accessed: # only update on insertion
            if block_index not in self.insertion_order:
                self.insertion_order.append(block_index)

    def get_victim(self, valid_blocks):
        for block in self.insertion_order:
            if block in valid_blocks:
                return block
        if valid_blocks:
            return valid_blocks[0]
        return None

class RandomPolicy(CachePolicy):
    def __init__(self):
        super().__init__()

    def update(self, block_index, accessed=True):
        pass

    def get_victim(self, valid_blocks):
        if valid_blocks:
            return random.choice(valid_blocks)
        return None
