from dataclasses import dataclass, field
from typing import Optional, List
import random
import csv
import argparse
import copy
from collections import deque
from ProcessClass.process import Process
from utils.file_io import write_execution_csv

class PriorityRoundRobinScheduler:

    """
    Round Robin with Priority CPU Scheduling Algorithm
    
    Combines priority scheduling with Round Robin. Processes are organized into priority 
    queues, with higher priority processes scheduled first. Within each priority level, 
    processes execute in Round Robin fashion with a fixed time quantum.
    
    This is a preemptive algorithm.
    
    Attributes:
        processes (List[Process]): List of processes to schedule.
        time_quantum (int): Fixed time slice allocated to each process.
        current_time (int): Current simulation time.
        execution_log (List[str]): Log to track execution history.
        gantt_chart (List[tuple]): For visualizing the execution sequence.
        aging_factor (int): Number of time units after which a process's priority increases.
    """
    
    def __init__(self, processes: List[Process], time_quantum: int = 2, aging_factor: int = 10):
        """
        Initialize the Round Robin with Priority scheduler.
        
        Args:
            processes: List of Process objects to schedule
            time_quantum: Time slice allocated to each process
            aging_factor: Number of time units after which a process's priority increases
        """
        # Create deep copies of processes to avoid modifying the originals
        self.processes = copy.deepcopy(processes)
        self.time_quantum = time_quantum
        self.aging_factor = aging_factor
        self.current_time = 0
        self.execution_log = []  # Log to track execution history
        self.gantt_chart = []    # For visualizing the execution sequence
        
    def run(self) -> List[Process]:
        """
        Run the Round Robin with Priority scheduling algorithm.
        
        Returns:
            List of processes after scheduling with calculated metrics
        """
        if not self.processes:
            return []
            
        # Sort processes by arrival time initially
        self.processes.sort(key=lambda p: p.arrival_time)
        
        # Reset current time to the arrival time of the first process
        self.current_time = self.processes[0].arrival_time
        
        remaining_processes = copy.deepcopy(self.processes)
        completed_processes = []
        
        # Ready queues for each priority level
        priority_queues = {}
        
        # Add the first arrived process to the appropriate priority queue
        first_process = remaining_processes[0]
        if first_process.priority not in priority_queues:
            priority_queues[first_process.priority] = deque()
        priority_queues[first_process.priority].append(first_process)
        
        while any(priority_queues.values()) or any(p for p in remaining_processes if p not in completed_processes and not any(p in q for q in priority_queues.values())):
            # If all queues are empty, find the next arriving process
            if not any(priority_queues.values()):
                next_processes = [p for p in remaining_processes if p not in completed_processes]
                next_arrival = min(p.arrival_time for p in next_processes)
                
                # Advance time to next arrival
                self.gantt_chart.append(("IDLE", self.current_time, next_arrival))
                self.execution_log.append(f"Time {self.current_time}: CPU idle until {next_arrival}")
                self.current_time = next_arrival
                
                # Add all processes that arrive at this time to their priority queues
                for p in next_processes:
                    if p.arrival_time == self.current_time:
                        if p.priority not in priority_queues:
                            priority_queues[p.priority] = deque()
                        priority_queues[p.priority].append(p)
                continue
            
            # Get the highest priority (lowest value) non-empty queue
            priority = min([p for p in priority_queues if priority_queues[p]])
            
            # Get the next process from the priority queue
            current_process = priority_queues[priority].popleft()
            
            # Set response time if this is the first time the process runs
            if current_process.response_time is None and current_process.cpu_time_acquired == 0:
                current_process.response_time = self.current_time - current_process.arrival_time
                
            # Calculate waiting time since last execution
            if current_process.cpu_time_acquired > 0:  # Not the first execution
                wait_time = self.current_time - current_process.last_running_time
                current_process.waiting_time += wait_time
                
                # Apply aging - if process has been waiting too long, increase its priority
                if wait_time >= self.aging_factor:
                    old_priority = current_process.priority
                    if current_process.priority > 1:  # Don't increase beyond highest priority (1)
                        current_process.priority -= 1
                        self.execution_log.append(f"Time {self.current_time}: Process {current_process.id} priority increased from {old_priority} to {current_process.priority} due to aging")
            
            # Log process execution start
            log_entry = f"Time {self.current_time}: Running Process {current_process.id} "
            log_entry += f"(remaining: {current_process.remaining_time}, priority: {current_process.priority}, quantum: {self.time_quantum})"
            self.execution_log.append(log_entry)
            
            # Execute process for the time quantum or until completion
            current_process.state = "RUNNING"
            time_slice = min(self.time_quantum, current_process.remaining_time)
            time_used = current_process.execute(time_slice)
            
            # Record in Gantt chart
            self.gantt_chart.append((current_process.id, self.current_time, self.current_time + time_used))
            
            # Update the last running time
            current_process.last_running_time = self.current_time + time_used
            
            # Advance time
            self.current_time += time_used
            
            # Check for newly arrived processes during this time slice
            for p in remaining_processes:
                if (p.arrival_time > current_process.last_running_time - time_used and 
                    p.arrival_time <= self.current_time and 
                    p not in completed_processes and 
                    not any(p in q for q in priority_queues.values()) and
                    p != current_process):
                    if p.priority not in priority_queues:
                        priority_queues[p.priority] = deque()
                    priority_queues[p.priority].append(p)
                    self.execution_log.append(f"Time {p.arrival_time}: Process {p.id} arrived with priority {p.priority}")
            
            # Check if the process is completed
            if current_process.is_completed():
                current_process.complete(self.current_time)
                log_entry = f"Time {self.current_time}: Completed Process {current_process.id}"
                self.execution_log.append(log_entry)
                completed_processes.append(current_process)
            else:
                # Process not completed, put it back in its priority queue
                if current_process.priority not in priority_queues:
                    priority_queues[current_process.priority] = deque()
                priority_queues[current_process.priority].append(current_process)
                current_process.state = "READY"
        
        # Update the original processes list with the completed processes
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
        total_response_time = sum(p.response_time for p in self.processes if p.response_time is not None)
        total_execution_time = max(p.completion_time for p in self.processes) - \
                               min(p.arrival_time for p in self.processes)
        
        return {
            "avg_waiting_time": total_waiting_time / len(self.processes),
            "avg_turnaround_time": total_turnaround_time / len(self.processes),
            "avg_response_time": total_response_time / len(self.processes),
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
                chart_bar = f"| {'IDLE' + ' ' * duration} "
            else:
                chart_bar = f"| P{proc_id}" + " " * duration + " "
            print(f"Time {start_time:<3} {chart_bar}| Time {end_time:<3}")
            
        print("-" * 50)
    
    def print_execution_log(self) -> None:
        """Print the execution log."""
        if not self.execution_log:
            print("No execution log available.")
            return
            
        print("\nExecution Log:")
        print("-" * 80)
        for entry in self.execution_log:
            print(entry)
        print("-" * 80)
    
    def print_results(self) -> None:
        """Print detailed results of the scheduling."""
        if not self.processes:
            print("No processes to display results for.")
            return
            
        # Print process details
        print("\nProcess Details:")
        print("-" * 100)
        print(f"{'ID':<5} {'Burst Time':<12} {'Priority':<10} {'Arrival':<10} {'Waiting':<10} {'Response':<10} {'Turnaround':<12} {'Completion':<12}")
        print("-" * 100)
        
        # Sort by process ID for display
        sorted_processes = sorted(self.processes, key=lambda p: p.id)
        for p in sorted_processes:
            print(f"{p.id:<5} {p.burst_time:<12} {p.priority:<10} {p.arrival_time:<10} {p.waiting_time:<10} {p.response_time:<10} {p.turnaround_time:<12} {p.completion_time:<12}")
        
        # Print statistics
        stats = self.get_statistics()
        print("\nScheduling Statistics:")
        print("-" * 50)
        print(f"Average Waiting Time    : {stats['avg_waiting_time']:.2f} time units")
        print(f"Average Turnaround Time : {stats['avg_turnaround_time']:.2f} time units")
        print(f"Average Response Time   : {stats['avg_response_time']:.2f} time units")
        print(f"Total Execution Time    : {stats['total_execution_time']} time units")
        print(f"Throughput              : {stats['throughput']:.4f} processes/time unit")
        print(f"Time Quantum            : {self.time_quantum} time units")
        print(f"Aging Factor            : {self.aging_factor} time units")


# Simple process generator function for demonstration
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


