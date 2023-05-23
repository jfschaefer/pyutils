from __future__ import annotations

import time
from typing import Optional


class CumulativeTimer:
    def __init__(self, name: str = 'anonymous timer'):
        self._name: str = name
        self._total_time: float = 0.0
        self._number_of_events_timed: int = 0
        self._start_time_of_current_event: Optional[float] = None

    def start(self):
        if self._start_time_of_current_event is not None:
            raise Exception('Timer is already timing something')
        self._start_time_of_current_event = time.time()

    def stop(self):
        if self._start_time_of_current_event is None:
            raise Exception('Timer is not timing anything')
        self._total_time += time.time() - self._start_time_of_current_event
        self._start_time_of_current_event = None
        self._number_of_events_timed += 1

    def __enter__(self) -> CumulativeTimer:
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def get_total_time(self) -> float:
        return self._total_time

    def get_number_of_events_timed(self) -> int:
        return self._number_of_events_timed

    def get_name(self) -> str:
        return self._name

    def info_string(self) -> str:
        return f'Results of {self._name}: {self._total_time} seconds in total for {self._number_of_events_timed} events'
