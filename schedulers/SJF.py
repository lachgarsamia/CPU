from dataclasses import dataclass, field
from typing import Optional, List
import random
import csv
import argparse
import copy
from ProcessClass.process import Process  
from utils.file_io import write_execution_csv


class SJFScheduler:
    """
    Shortest Job First (SJF) CPU Scheduling Algorithm
    
    Selects the process with the shortest burst time among all available processes.
    This is a non-preemptive algorithm.
    """
    
    def __init__(self, processes: List[Process]):
        """
        Initialize the SJF scheduler with a list of processes.
        
        Args:
            processes: List of Process objects to schedule
        """
        self.processes = copy.deepcopy(processes)
        self.current_time = 0
        self.execution_log = []  
        self.gantt_chart = []    
        
    def run(self) -> List[Process]:
        """
        Run the SJF scheduling algorithm.
        
        Returns:
            List of processes after scheduling with calculated metrics
        """
        if not self.processes:
            return []
            
        self.processes.sort(key=lambda p: p.arrival_time)
        
        self.current_time = self.processes[0].arrival_time
        
        remaining_processes = copy.deepcopy(self.processes)
        completed_processes = []
        
        while remaining_processes:
            available_processes = [p for p in remaining_processes if p.arrival_time <= self.current_time]
            
            if not available_processes:
                next_arrival = min(p.arrival_time for p in remaining_processes)
                self.gantt_chart.append(("IDLE", self.current_time, next_arrival))
                self.execution_log.append(f"Time {self.current_time}: CPU idle until {next_arrival}")
                self.current_time = next_arrival
                continue
            
            selected_process = min(available_processes, key=lambda p: p.burst_time)
            
            selected_process.state = "READY"
            selected_process.last_running_time = max(selected_process.arrival_time, self.current_time)
            
            selected_process.waiting_time = self.current_time - selected_process.arrival_time
            
            log_entry = f"Time {self.current_time}: Starting Process {selected_process.id} (burst time: {selected_process.burst_time})"
            self.execution_log.append(log_entry)
            
            time_used = selected_process.execute(selected_process.burst_time)
            
            self.gantt_chart.append((selected_process.id, self.current_time, self.current_time + time_used))
            
            self.current_time += time_used
            
            selected_process.complete(self.current_time)
            
            log_entry = f"Time {self.current_time}: Completed Process {selected_process.id}"
            self.execution_log.append(log_entry)
            
            remaining_processes.remove(selected_process)
            completed_processes.append(selected_process)
        
        self.processes = completed_processes

        write_execution_csv(self.gantt_chart)
        return self.processes
    
    def get_statistics(self) -> dict:
        """
        Calculate and return scheduling statistics.
        
        Returns:
            dict: Various scheduling metrics including average waiting time,
                 average turnaround time, etc.
        """
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
        total_execution_time = max(p.completion_time for p in self.processes) - \
                               min(p.arrival_time for p in self.processes)
        
        return {
            "avg_waiting_time": total_waiting_time / len(self.processes),
            "avg_turnaround_time": total_turnaround_time / len(self.processes),
            "avg_response_time": total_waiting_time / len(self.processes),  # In SJF, response time equals waiting time
            "total_execution_time": total_execution_time,
            "throughput": len(self.processes) / total_execution_time if total_execution_time > 0 else 0
        }
    
    def print_gantt_chart(self) -> None:
        """Print a simple Gantt chart of the execution sequence."""
        if not self.gantt_chart:
            print("No processes were executed.")
            return
            
        print("\nGantt Chart:")
        print("-" * 50)
        
        for proc_id, start_time, end_time in self.gantt_chart:
            duration = end_time - start_time
            if proc_id == "IDLE":
                chart_bar = f"| {'IDLE':<{duration}} "
            else:
                chart_bar = f"| P{proc_id:<{duration}} "
            print(f"Time {start_time:<3} {chart_bar}| Time {end_time:<3}")
            
        print("-" * 50)
    
    def print_execution_log(self) -> None:
        """Print the execution log."""
        if not self.execution_log:
            print("No execution log available.")
            return
            
        print("\nExecution Log:")
        print("-" * 50)
        for entry in self.execution_log:
            print(entry)
        print("-" * 50)
    
    def print_results(self) -> None:
        """Print detailed results of the scheduling."""
        if not self.processes:
            print("No processes to display results for.")
            return
            
        # Print process details
        print("\nProcess Details:")
        print("-" * 80)
        print(f"{'ID':<5} {'Burst Time':<12} {'Arrival':<10} {'Waiting':<10} {'Turnaround':<12} {'Completion':<12}")
        print("-" * 80)
        
        # Sort by process ID for display
        sorted_processes = sorted(self.processes, key=lambda p: p.id)
        for p in sorted_processes:
            print(f"{p.id:<5} {p.burst_time:<12} {p.arrival_time:<10} {p.waiting_time:<10} {p.turnaround_time:<12} {p.completion_time:<12}")
        
        # Print statistics
        stats = self.get_statistics()
        print("\nScheduling Statistics:")
        print("-" * 50)
        print(f"Average Waiting Time    : {stats['avg_waiting_time']:.2f} time units")
        print(f"Average Turnaround Time : {stats['avg_turnaround_time']:.2f} time units")
        print(f"Average Response Time   : {stats['avg_response_time']:.2f} time units")
        print(f"Total Execution Time    : {stats['total_execution_time']} time units")
        print(f"Throughput              : {stats['throughput']:.4f} processes/time unit")
        

def generate_test_processes(num_processes: int = 5, seed: int = None) -> List[Process]:
    """Generate test processes for demonstration."""
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
