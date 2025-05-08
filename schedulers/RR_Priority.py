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
    Priority-based Round Robin CPU Scheduling Algorithm
    
    Combines Round Robin with priority considerations:
    - Processes are organized in priority levels
    - Within each priority level, Round Robin scheduling is applied
    - Higher priority processes always execute before lower priority ones
    
    Attributes:
        processes (List[Process]): List of processes to schedule.
        time_quantum (int): Fixed time slice allocated to each process.
        current_time (int): Current simulation time.
        execution_log (List[str]): Log to track execution history.
        gantt_chart (List[tuple]): For visualizing the execution sequence.
    """
    
    def __init__(self, processes: List[Process], time_quantum: int = 2):
        """
        Initialize the Priority Round Robin scheduler with a list of processes.
        
        Args:
            processes: List of Process objects to schedule
            time_quantum: Time slice allocated to each process
        """
        self.processes = copy.deepcopy(processes)
        self.time_quantum = time_quantum
        self.current_time = 0
        self.execution_log = []  
        self.gantt_chart = []    
        
    def run(self) -> List[Process]:
        """
        Run the Priority Round Robin scheduling algorithm.
        
        Returns:
            List of processes after scheduling with calculated metrics
        """
        if not self.processes:
            return []
            
        self.processes.sort(key=lambda p: p.arrival_time)
        
        # Initialize current time to the earliest arrival
        self.current_time = self.processes[0].arrival_time
        
        remaining_processes = copy.deepcopy(self.processes)
        completed_processes = []
        
        # Instead of a single queue, maintain priority-based queues
        priority_queues = {}
        
        # Add ALL processes that arrive at the initial time to their priority queues
        for process in remaining_processes:
            if process.arrival_time <= self.current_time:
                if process.priority not in priority_queues:
                    priority_queues[process.priority] = deque()
                priority_queues[process.priority].append(process)
        
        while priority_queues or any(p for p in remaining_processes if p not in completed_processes):
            # Handle idle time when no processes are ready
            if not priority_queues:
                next_processes = [p for p in remaining_processes if p not in completed_processes]
                next_arrival = min(p.arrival_time for p in next_processes)
                
                self.gantt_chart.append(("IDLE", self.current_time, next_arrival))
                self.execution_log.append(f"Time {self.current_time}: CPU idle until {next_arrival}")
                self.current_time = next_arrival
                
                # Add ALL processes that arrive at this new time to their priority queues
                for p in next_processes:
                    if p.arrival_time <= self.current_time and p not in completed_processes:
                        if p.priority not in priority_queues:
                            priority_queues[p.priority] = deque()
                        priority_queues[p.priority].append(p)
                continue
            
            # Get the highest priority (lowest number = highest priority)
            highest_priority = min(priority_queues.keys())
            current_queue = priority_queues[highest_priority]
            
            # Get next process from the highest priority queue
            current_process = current_queue.popleft()
            
            # Calculate response time if first time running
            if current_process.response_time is None and current_process.cpu_time_acquired == 0:
                current_process.response_time = self.current_time - current_process.arrival_time
                
            # Update waiting time
            if current_process.cpu_time_acquired > 0:
                wait_time = self.current_time - current_process.arrival_time - current_process.burst_time
                current_process.waiting_time += wait_time
            
            # Log execution
            log_entry = f"Time {self.current_time}: Running Process {current_process.id} "
            log_entry += f"(priority: {current_process.priority}, remaining: {current_process.remaining_time}, quantum: {self.time_quantum})"
            self.execution_log.append(log_entry)
            
            # Execute the process
            current_process.state = "RUNNING"
            time_slice = min(self.time_quantum, current_process.remaining_time)
            time_used = current_process.execute(time_slice)
            
            # Update Gantt chart
            self.gantt_chart.append((current_process.id, self.current_time, self.current_time + time_used))
            
            current_process.last_running_time = self.current_time + time_used
            self.current_time += time_used
            
            # Check for new arrivals during this time slice and add them to appropriate priority queues
            for p in remaining_processes:
                if (p.arrival_time <= self.current_time and 
                    p not in completed_processes and 
                    p != current_process):
                    
                    # Check if this process is already in any queue
                    in_queue = False
                    for priority, queue in priority_queues.items():
                        if p in queue:
                            in_queue = True
                            break
                    
                    if not in_queue:
                        if p.priority not in priority_queues:
                            priority_queues[p.priority] = deque()
                        priority_queues[p.priority].append(p)
            
            # Handle process completion or return to ready queue
            if current_process.is_completed():
                current_process.complete(self.current_time)
                log_entry = f"Time {self.current_time}: Completed Process {current_process.id}"
                self.execution_log.append(log_entry)
                completed_processes.append(current_process)
            else:
                # Put back in the appropriate priority queue
                if current_process.priority not in priority_queues:
                    priority_queues[current_process.priority] = deque()
                priority_queues[current_process.priority].append(current_process)
                current_process.state = "READY"
            
            # Clean up empty queues
            empty_priorities = [p for p, q in priority_queues.items() if not q]
            for p in empty_priorities:
                del priority_queues[p]
        
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
        print("-" * 60)
        
        for proc_id, start_time, end_time in self.gantt_chart:
            proc_label = f"P{proc_id}" if proc_id != "IDLE" else "IDLE"
            print(f"Time {start_time:<3} | {proc_label:<5} | Time {end_time:<3}")
            
        print("-" * 60)
    
    def print_execution_log(self) -> None:
        """Print the execution log."""
        if not self.execution_log:
            print("No execution log available.")
            return
            
        print("\nExecution Log:")
        print("-" * 90)
        for entry in self.execution_log:
            print(entry)
        print("-" * 90)
    
    def print_results(self) -> None:
        """Print detailed results of the scheduling."""
        if not self.processes:
            print("No processes to display results for.")
            return
            
        print("\nProcess Details:")
        print("-" * 100)
        print(f"{'ID':<5} {'Burst Time':<12} {'Priority':<10} {'Arrival':<10} {'Waiting':<10} {'Response':<10} {'Turnaround':<12} {'Completion':<12}")
        print("-" * 100)
        
        sorted_processes = sorted(self.processes, key=lambda p: p.id)
        for p in sorted_processes:
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