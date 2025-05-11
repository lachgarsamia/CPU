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
        # Create a deep copy of input processes to avoid side effects
        self.processes = copy.deepcopy(processes)
        self.time_quantum = time_quantum
        self.current_time = 0
        self.execution_log = []  # Stores human-readable execution messages
        self.gantt_chart = []    # Tracks the execution timeline
    
    def run(self) -> List[Process]:
        """
        Run the Priority Round Robin scheduling algorithm.
        
        Returns:
            List of processes after scheduling with calculated metrics
        """
        if not self.processes:
            return []
        
        # Sort processes by arrival time to simulate realistic arrival order
        self.processes.sort(key=lambda p: p.arrival_time)
        self.current_time = self.processes[0].arrival_time
        
        # Make a working copy to manage state changes during scheduling
        remaining_processes = copy.deepcopy(self.processes)
        completed_processes = []

        # Dictionary to hold queues of processes grouped by priority
        priority_queues = {}

        # Load initial processes that have arrived into their respective queues
        for process in remaining_processes:
            if process.arrival_time <= self.current_time:
                if process.priority not in priority_queues:
                    priority_queues[process.priority] = deque()
                priority_queues[process.priority].append(process)
        
        # Main scheduling loop: continues while there are uncompleted or arriving processes
        while priority_queues or any(p for p in remaining_processes if p not in completed_processes):
            # If no processes are ready, CPU goes idle
            if not priority_queues:
                next_processes = [p for p in remaining_processes if p not in completed_processes]
                next_arrival = min(p.arrival_time for p in next_processes)
                
                # Log idle time
                self.gantt_chart.append(("IDLE", self.current_time, next_arrival))
                self.execution_log.append(f"Time {self.current_time}: CPU idle until {next_arrival}")
                self.current_time = next_arrival

                # Load newly arrived processes into queues
                for p in next_processes:
                    if p.arrival_time <= self.current_time and p not in completed_processes:
                        if p.priority not in priority_queues:
                            priority_queues[p.priority] = deque()
                        priority_queues[p.priority].append(p)
                continue
            
            # Pick the highest priority queue (lower number = higher priority)
            highest_priority = min(priority_queues.keys())
            current_queue = priority_queues[highest_priority]
            current_process = current_queue.popleft()
            
            # Calculate response time if it's the process's first execution
            if current_process.response_time is None and current_process.cpu_time_acquired == 0:
                current_process.response_time = self.current_time - current_process.arrival_time
            
            # Update waiting time for subsequent executions
            if current_process.cpu_time_acquired > 0:
                wait_time = self.current_time - current_process.arrival_time - current_process.burst_time
                current_process.waiting_time += wait_time
            
            # Log execution details
            log_entry = f"Time {self.current_time}: Running Process {current_process.id} "
            log_entry += f"(priority: {current_process.priority}, remaining: {current_process.remaining_time}, quantum: {self.time_quantum})"
            self.execution_log.append(log_entry)

            # Simulate process execution
            current_process.state = "RUNNING"
            time_slice = min(self.time_quantum, current_process.remaining_time)
            time_used = current_process.execute(time_slice)

            # Record execution in Gantt chart
            self.gantt_chart.append((current_process.id, self.current_time, self.current_time + time_used))
            current_process.last_running_time = self.current_time + time_used
            self.current_time += time_used

            # Check for new arrivals during the execution and add them to queues
            for p in remaining_processes:
                if (p.arrival_time <= self.current_time and 
                    p not in completed_processes and 
                    p != current_process):
                    
                    # Avoid duplicate entries in queues
                    in_queue = any(p in queue for queue in priority_queues.values())
                    if not in_queue:
                        if p.priority not in priority_queues:
                            priority_queues[p.priority] = deque()
                        priority_queues[p.priority].append(p)
            
            # Decide whether to complete or requeue the process
            if current_process.is_completed():
                current_process.complete(self.current_time)
                self.execution_log.append(f"Time {self.current_time}: Completed Process {current_process.id}")
                completed_processes.append(current_process)
            else:
                # Requeue the process for further execution
                if current_process.priority not in priority_queues:
                    priority_queues[current_process.priority] = deque()
                priority_queues[current_process.priority].append(current_process)
                current_process.state = "READY"

            # Clean up any empty queues
            empty_priorities = [p for p, q in priority_queues.items() if not q]
            for p in empty_priorities:
                del priority_queues[p]
        
        # Save Gantt chart to file
        self.processes = completed_processes
        write_execution_csv(self.gantt_chart)
        return self.processes

    def calculate_cpu_usage(self) -> float:
        """
        Calculate CPU usage as the percentage of time spent executing processes.
        
        Returns:
            float: CPU usage as a percentage (0-100)
        """
        if not self.gantt_chart:
            return 0.0
        
        # Determine total time from first start to last finish
        total_time = self.gantt_chart[-1][2] - self.gantt_chart[0][1]
        if total_time <= 0:
            return 0.0
        
        # Compute total idle time from Gantt chart
        idle_time = sum(end_time - start_time for proc_id, start_time, end_time in self.gantt_chart if proc_id == "IDLE")
        
        # Calculate CPU active time and usage
        active_time = total_time - idle_time
        cpu_usage = (active_time / total_time) * 100
        
        return cpu_usage

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
