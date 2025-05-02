# system/system.py

from ProcessClass.process import Process
from typing import List
import pandas as pd
import random

class System:
    def __init__(self, processes: List[Process] = None, context_switching_time: int = 0, quantum: int = 1):
        self.processes = processes
        self.context_switching = context_switching_time
        self.quantum = quantum

    @staticmethod
    def generate_processes(file_directory: str, number_of_processes: int, max_burst: int, min_burst: int, max_arrival_time: int) -> List[Process]:
        processes = []
        with open(file_directory, 'w') as f:
            f.write("id,burst_time,priority,arrival_time\n")
            for i in range(1, number_of_processes + 1):
                burst_time = random.randint(min_burst, max_burst)
                priority = random.randint(1, 5) # Should see how to enter priority
                arrival_time = random.randint(0, max_arrival_time)
                process = Process(id=i, burst_time=burst_time, priority=priority, arrival_time=arrival_time)
                processes.append(process)
                f.write(f"{process.id},{process.burst_time},{process.priority},{process.arrival_time}\n")
        return processes

    @staticmethod
    def load_from_csv(file_directory: str) -> List[Process]:
        df = pd.read_csv(file_directory)
        processes = []
        for _, row in df.iterrows():
            process = Process(
                id=int(row['id']),
                burst_time=int(row['burst_time']),
                priority=int(row['priority']),
                arrival_time=int(row['arrival_time'])
            )
            processes.append(process)
        return processes

    @staticmethod
    def save_processes_csv(file_directory: str, processes: List[Process]) -> None:
        with open(file_directory, 'w') as f:
            f.write("id,burst_time,priority,arrival_time,waiting_time,turnaround_time,completion_time\n")
            for p in processes:
                f.write(f"{p.id},{p.burst_time},{p.priority},{p.arrival_time},{p.waiting_time},{p.turnaround_time},{p.completion_time}\n")

    def system_to_csv(self, file_directory: str) -> None:
        with open(file_directory, 'w') as f:
            f.write(f"{self.quantum},{self.context_switching}")

    @staticmethod
    def load_system_txt(file_directory: str, processes: List[Process]) -> 'System':
        with open(file_directory, 'r') as f:
            parts = f.read().strip().split(',')
        quantum = int(parts[0])
        context_switching = int(parts[1])
        return System(processes, context_switching_time=context_switching, quantum=quantum)
