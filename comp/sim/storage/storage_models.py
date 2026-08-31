class StorageModel:
    def __init__(self, name: str, read_latency: float, write_latency: float, bandwidth_gbps: float, is_simulated: bool = False):
        self.name = name
        self.read_latency = read_latency   # in ns
        self.write_latency = write_latency # in ns
        self.bandwidth_gbps = bandwidth_gbps
        self.is_simulated = is_simulated
        
        self.read_ops = 0
        self.write_ops = 0
        self.total_read_time = 0.0
        self.total_write_time = 0.0

    def read_page(self, page_size_bytes: int) -> float:
        """Returns time taken to read a page in ns"""
        self.read_ops += 1
        transfer_time = (page_size_bytes / (self.bandwidth_gbps * 1e9)) * 1e9 # ns
        time_taken = self.read_latency + transfer_time
        self.total_read_time += time_taken
        return time_taken

    def write_page(self, page_size_bytes: int) -> float:
        """Returns time taken to write a page in ns"""
        self.write_ops += 1
        transfer_time = (page_size_bytes / (self.bandwidth_gbps * 1e9)) * 1e9 # ns
        time_taken = self.write_latency + transfer_time
        self.total_write_time += time_taken
        return time_taken

    def get_stats(self):
        return {
            'name': self.name,
            'is_simulated': self.is_simulated,
            'read_ops': self.read_ops,
            'write_ops': self.write_ops,
            'read_latency_avg': self.total_read_time / self.read_ops if self.read_ops > 0 else 0,
            'write_latency_avg': self.total_write_time / self.write_ops if self.write_ops > 0 else 0,
            'total_time': self.total_read_time + self.total_write_time
        }

# Pre-defined models
STORAGE_MODELS = {
    'HDD': StorageModel('HDD', read_latency=5_000_000, write_latency=5_000_000, bandwidth_gbps=0.15),
    'SATA SSD': StorageModel('SATA SSD', read_latency=100_000, write_latency=100_000, bandwidth_gbps=0.6),
    'NVMe SSD': StorageModel('NVMe SSD', read_latency=20_000, write_latency=20_000, bandwidth_gbps=3.5),
    'Simulated MRAM': StorageModel('Simulated MRAM', read_latency=100, write_latency=100, bandwidth_gbps=20.0, is_simulated=True),
    'Simulated PCM': StorageModel('Simulated PCM', read_latency=500, write_latency=1000, bandwidth_gbps=10.0, is_simulated=True),
    'Simulated ReRAM': StorageModel('Simulated ReRAM', read_latency=200, write_latency=800, bandwidth_gbps=15.0, is_simulated=True),
}
