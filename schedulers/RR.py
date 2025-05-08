from dataclasses import dataclass, field
from typing import Optional, List
import random
import csv
import argparse
import copy
from collections import deque
from ProcessClass.process import Process
from utils.file_io import write_execution_csv

class RoundRobinScheduler:
    """
    Round Robin CPU Scheduling Algorithm
    
    Allocates CPU to each process for a fixed time quantum in a circular manner.
    This is a preemptive algorithm.
    
    Attributes:
        processes (List[Process]): List of processes to schedule.
        time_quantum (int): Fixed time slice allocated to each process.
        current_time (int): Current simulation time.
        execution_log (List[str]): Log to track execution history.
        gantt_chart (List[tuple]): For visualizing the execution sequence.
    """

    def __init__(self, processes: List[Process], time_quantum: int = 2):
        self.original_processes = copy.deepcopy(processes)
        self.processes = copy.deepcopy(processes)
        self.time_quantum = time_quantum
        self.current_time = 0
        self.execution_log = []
        self.gantt_chart = []

    def run(self) -> List[Process]:
        if not self.processes:
            return []

        for p in self.processes:
            p.remaining_time = p.burst_time
            p.first_response = False
            p.finished = False

        self.processes.sort(key=lambda p: p.arrival_time)
        ready_queue = deque()
        completed = 0
        n = len(self.processes)
        self.current_time = self.processes[0].arrival_time

        while completed < n:
            new_arrivals = [ p for p in self.processes
    if p.arrival_time <= self.current_time and not p.finished and p not in ready_queue ]
            # Optional: if inside a loop after popping `process`, exclude it explicitly
            if 'process' in locals():
                new_arrivals = [p for p in new_arrivals if p != process]

            # Preserve arrival order
            new_arrivals.sort(key=lambda p: p.arrival_time)
            ready_queue.extend(new_arrivals)


            if ready_queue:
                process = ready_queue.popleft()

                if not process.first_response:
                    process.response_time = self.current_time - process.arrival_time
                    process.first_response = True

                exec_time = min(self.time_quantum, process.remaining_time)
                self.execution_log.append(f"Time {self.current_time}: Running Process {process.id} for {exec_time} units")
                self.gantt_chart.append((process.id, self.current_time, self.current_time + exec_time))

                self.current_time += exec_time
                process.remaining_time -= exec_time

                for p in self.processes:
                    if (p.arrival_time <= self.current_time and not p.finished and p not in ready_queue and p != process):
                        ready_queue.append(p)

                if process.remaining_time == 0:
                    process.completion_time = self.current_time
                    process.turnaround_time = process.completion_time - process.arrival_time
                    process.waiting_time = process.turnaround_time - process.burst_time
                    process.finished = True
                    self.execution_log.append(f"Time {self.current_time}: Completed Process {process.id}")
                    completed += 1
                else:
                    ready_queue.append(process)
            else:
                self.gantt_chart.append(("IDLE", self.current_time, self.current_time + 1))
                self.execution_log.append(f"Time {self.current_time}: CPU idle")
                self.current_time += 1

        write_execution_csv(self.gantt_chart)
        return self.processes

    def get_statistics(self) -> dict:
        if not self.processes:
            return {
                "avg_waiting_time": 0,
                "avg_turnaround_time": 0,
                "avg_response_time": 0,
                "total_execution_time": 0,
                "throughput": 0
            }

        total_waiting_time = sum(p.waiting_time for p in self.processes)
        total_turnaround_time = sum(p.turnaround_time for p in self.processes)
        total_response_time = sum(p.response_time for p in self.processes if p.response_time is not None)
        total_execution_time = max(p.completion_time for p in self.processes) - min(p.arrival_time for p in self.processes)

        return {
            "avg_waiting_time": total_waiting_time / len(self.processes),
            "avg_turnaround_time": total_turnaround_time / len(self.processes),
            "avg_response_time": total_response_time / len(self.processes),
            "total_execution_time": total_execution_time,
            "throughput": len(self.processes) / total_execution_time if total_execution_time > 0 else 0
        }

    def print_gantt_chart(self) -> None:
        if not self.gantt_chart:
            print("No processes were executed.")
            return

        print("\nGantt Chart:")
        print("-" * 50)
        for proc_id, start_time, end_time in self.gantt_chart:
            print(f"Time {start_time:<3} | {'IDLE' if proc_id == 'IDLE' else f'P{proc_id}'} | Time {end_time:<3}")
        print("-" * 50)

    def print_execution_log(self) -> None:
        if not self.execution_log:
            print("No execution log available.")
            return

        print("\nExecution Log:")
        print("-" * 80)
        for entry in self.execution_log:
            print(entry)
        print("-" * 80)

    def print_results(self) -> None:
        if not self.processes:
            print("No processes to display results for.")
            return

        print("\nProcess Details:")
        print("-" * 100)
        print(f"{'ID':<5} {'Burst Time':<12} {'Priority':<10} {'Arrival':<10} {'Waiting':<10} {'Response':<10} {'Turnaround':<12} {'Completion':<12}")
        print("-" * 100)
        for p in sorted(self.processes, key=lambda x: x.id):
            print(f"{p.id:<5} {p.burst_time:<12} {p.priority:<10} {p.arrival_time:<10} {p.waiting_time:<10} {p.response_time:<10} {p.turnaround_time:<12} {p.completion_time:<12}")

        stats = self.get_statistics()
        print("\nScheduling Statistics:")
        print("-" * 50)
        print(f"Average Waiting Time    : {stats['avg_waiting_time']:.2f} time units")
        print(f"Average Turnaround Time : {stats['avg_turnaround_time']:.2f} time units")
        print(f"Average Response Time   : {stats['avg_response_time']:.2f} time units")
        print(f"Total Execution Time    : {stats['total_execution_time']} time units")
        print(f"Throughput              : {stats['throughput']:.4f} processes/time unit")
        print(f"Time Quantum            : {self.time_quantum} time units")


def generate_test_processes(num_processes: int = 5, seed: int = None) -> List[Process]:
    if seed is not None:
        random.seed(seed)

    processes = []
    for i in range(1, num_processes + 1):
        processes.append(Process(
            id=i,
            burst_time=random.randint(1, 10),
            priority=random.randint(1, 5),
            arrival_time=random.randint(0, 20)
        ))
    return processes