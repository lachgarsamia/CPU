from dataclasses import dataclass, field
from typing import Optional, List
import random
import csv
import argparse
import copy
from ProcessClass.process import Process


class FCFSScheduler:
    """
    First Come First Serve (FCFS) CPU Scheduling Algorithm
    Processes are executed in the order they arrive.
    This is a non-preemptive algorithm.
    """

    def __init__(self, processes: List[Process]):
        """
        Initialize the FCFS scheduler with a list of processes.
        Args:
            processes (List[Process]): List of processes to be scheduled.
        """

        self.processes = copy.deepcopy(processes)
        self.current_time = 0
        self.execution_log = []
        self.gantt_chart = []
    
    def run(self) -> List[Process]:
        """
        Run the FCFS Scheduling algorithm.
        Returns:
            List of processes after scheduling with calculated metrics
        """
        if not self.processes:
            return []
        
        self.processes.sort(key=lambda p: p.arrival_time)
        self.current_time = self.processes[0].arrival_time

        for process in self.processes:
            if self.current_time < process.arrival_time:
                self.gantt_chart.append(("IDLE", self.current_time, process.arrival_time))
                self.current_time = process.arrival_time

            process.state = "READY"
            process.last_running_time = max(process.arrival_time, self.current_time)

            process.waiting_time = self.current_time - process.arrival_time

            log_entry = f"Time {self.current_time}: Starting Process {process.id}"
            self.execution_log.append(log_entry)

            time_used = process.execute(process.burst_time)

            self.gantt_chart.append((process.id, self.current_time, self.current_time + time_used))

            self.current_time += time_used
            process.complete(self.current_time)

            log_entry = f"Time {self.current_time}: Completed Process {process.id}"
            self.execution_log.append(log_entry)

        return self.processes
    

    def get_statistics(self) -> dict:
        """
        Calculate and return scheduling statistics.
        Returns:
            dict: Various Scheduling metrics including avg waiting time,
                avg turnaround time, …
        """
        if not self.processes:
            return {
                "avg_waiting_time":0,
                "avg_turnaround_time": 0,
                "avg_response_time": 0,
                "total_execution_time": 0,
                "throughput": 0
            }
        
        total_waiting_time = sum(p.waiting_time for p in self.processes)
        total_turnaround_time = sum(p.turnaround_time for p in self.processes)
        total_execution_time = max(p.completion_time for p in self.processes) - \
            min(p.arrival_time for p in self.processes)
        
        return {
            "avg_waiting_time": total_waiting_time / len(self.processes),
            "avg_turnaround_time": total_turnaround_time / len(self.processes),
            "avg_response_time": total_waiting_time / len(self.processes),
            "total_execution_time": total_execution_time,
            "throughput": len(self.processes) / total_execution_time if total_execution_time > 0 else 0
        }
    
    def print_gantt_chart(self) -> None:
        """ 
        Print a simple Gantt chart of the execution sequence.
        """
        if not self.gantt_chart:
            print("No processes were executed")
            return
        
        print("\nGantt Chart:")
        print("-" * 50)

        for proc_id, start_time, end_time in self.gantt_chart:
            duration = end_time - start_time
            if proc_id == "IDLE":
                chart_bar = f"| {'IDLE':<{duration}} "
            else:
                chart_bar = f"| P{proc_id:<{duration}} "
            print(f"Time {start_time: <3} {chart_bar}| Time {end_time:<3}")
        print("-" * 50)

    def print_execution_log(self) -> None:
        """
        Print the execution log
        """
        if not self.execution_log:
            print("No execution log available.")
            return 
        
        print("\nExecution Log: ")
        print("-" * 50)
        for entry in self.execution_log:
            print(entry)
        print("-" * 50)

    def print_results(self) -> None:
        """
        Print detailed results of the scheduling
        """
        if not self.processes:
            print("No processes to display.")
            return 
        
        print("\nProcess Details:")
        print("-" * 80)
        print(f"{'ID':<5} {'Burst Time':<12} {'Arrival':<10} {'Waiting':<10} {'Turnaround':<12} {'Completion':<12}")
        print("-" * 80)

        for p in self.processes:
            print(f"{p.id:<5} {p.burst_time:<12} {p.arrival_time:<10} {p.waiting_time:<10} {p.turnaround_time:<12} {p.completion_time:<12}")

        stats = self.get_statistics()
        print("\nScheduling Statistics: ")
        print("-" * 50)
        print(f"Average Waiting Time       : {stats['avg_waiting_time']:.2f} time units")
        print(f"Average Turnaround Time    : {stats['avg_turnaround_time']:.2f} time units")
        print(f"Average Response Time      : {stats['avg_response_time']:.2f} time units")
        print(f"Total Execution Time       : {stats['total_execution_time']} time units")
        print(f"Throughput                 : {stats['throughput']:.4f} processes/time unit")

def generate_test_processes(num_processes: int= 5, seed: int= None) -> List[Process]:
    """
    Generate test processes for demonstration
    """
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
    

