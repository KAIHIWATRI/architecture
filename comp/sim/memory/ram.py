class RAM:
    def __init__(self, size_bytes: int, latency: float):
        self.size = size_bytes
        self.latency = latency
        self.accesses = 0
        self.total_time = 0.0

    def access(self) -> float:
        self.accesses += 1
        self.total_time += self.latency
        return self.latency

    def get_stats(self):
        return {
            'accesses': self.accesses,
            'total_time': self.total_time,
            'latency': self.latency
        }
