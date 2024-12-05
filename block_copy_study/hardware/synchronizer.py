# synchronizer.py
# hardware/synchronizer.py
import numpy as np
import time
from collections import defaultdict


class DataSynchronizer:
    def __init__(self, streams=['gaze', 'head', 'chest', 'mobile']):
        self.streams = streams
        self.timestamps = defaultdict(list)
        self.sync_window = 5.0  # seconds

    def add_timestamp(self, stream, timestamp):
        self.timestamps[stream].append(timestamp)
        self._cleanup_old_timestamps()

    def _cleanup_old_timestamps(self):
        current_time = time.time()
        for stream in self.streams:
            self.timestamps[stream] = [t for t in self.timestamps[stream]
                                       if current_time - t < self.sync_window]

    def check_sync(self):
        sync_stats = {}
        for i, stream1 in enumerate(self.streams):
            for stream2 in self.streams[i + 1:]:
                diffs = []
                for t1 in self.timestamps[stream1]:
                    if self.timestamps[stream2]:
                        closest_t2 = min(self.timestamps[stream2],
                                         key=lambda t: abs(t - t1))
                        diffs.append(abs(t1 - closest_t2))

                if diffs:
                    sync_stats[f'{stream1}-{stream2}'] = {
                        'mean_diff': np.mean(diffs),
                        'std_diff': np.std(diffs),
                        'max_diff': max(diffs)
                    }

        return sync_stats