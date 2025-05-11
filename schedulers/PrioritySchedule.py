from dataclasses import dataclass, field
from typing import Optional, List
import random
import csv
import argparse
import copy
from ProcessClass.process import Process  
from utils.file_io import write_execution_csv


class PriorityScheduler:
    """
    Priority Scheduling Algorithm implementation.
    
    Selects the process with the highest priority (lowest priority value) for execution.
    This is a non-preemptive algorithm.
    
    Attributes:
        processes (List[Process]): List of processes to schedule.
        current_time (int): Current simulation time.
        execution_log (List[str]): Log to track execution history.
        gantt_chart (List[tuple]): For visualizing the execution sequence.
    """
    
    def __init__(self, processes: List[Process]):
        """
        Initialize the Priority scheduler with a list of processes.
        
        Args:
            processes: List of Process objects to schedule
        """
        self.processes = copy.deepcopy(processes)  # Make a deep copy to preserve original list
        self.current_time = 0  # Initialize simulation clock
        self.execution_log = []  # List to keep textual log of events
        self.gantt_chart = []  # List to represent the Gantt chart (execution timeline)
        
    def run(self) -> List[Process]:
        """
        Run the Priority scheduling algorithm.
        
        Returns:
            List of processes after scheduling with calculated metrics
        """
        if not self.processes:
            return []
            
        self.processes.sort(key=lambda p: p.arrival_time)  # Sort processes by arrival time
        self.current_time = self.processes[0].arrival_time  # Start at first arrival time
        
        remaining_processes = copy.deepcopy(self.processes)  # Copy for manipulation
        completed_processes = []  # List to collect finished processes
        
        while remaining_processes:
            # Get all processes that have arrived by current time
            available_processes = [p for p in remaining_processes if p.arrival_time <= self.current_time]
            
            if not available_processes:
                # If no process has arrived yet, CPU stays idle
                next_arrival = min(p.arrival_time for p in remaining_processes)
                self.gantt_chart.append(("IDLE", self.current_time, next_arrival))
                self.execution_log.append(f"Time {self.current_time}: CPU idle until {next_arrival}")
                self.current_time = next_arrival
                continue
            
            # Select process with highest priority (lowest value), breaking ties with arrival time and ID
            selected_process = min(available_processes, key=lambda p: (p.priority, p.arrival_time, p.id))

            selected_process.state = "READY"  # Set process state
            selected_process.last_running_time = max(selected_process.arrival_time, self.current_time)
            selected_process.waiting_time = self.current_time - selected_process.arrival_time  # Calculate waiting time
            
            # Set response time only the first time the process is picked
            if selected_process.response_time is None:
                selected_process.response_time = self.current_time - selected_process.arrival_time
            
            # Log the start of the process
            log_entry = f"Time {self.current_time}: Starting Process {selected_process.id} (priority: {selected_process.priority}, burst time: {selected_process.burst_time})"
            self.execution_log.append(log_entry)
            
            selected_process.state = "RUNNING"
            time_used = selected_process.execute(selected_process.burst_time)  # Run the full burst time
            
            # Record execution in Gantt chart
            self.gantt_chart.append((selected_process.id, self.current_time, self.current_time + time_used))
            
            self.current_time += time_used  # Advance simulation clock
            
            selected_process.complete(self.current_time)  # Mark as complete
            
            # Log completion
            log_entry = f"Time {self.current_time}: Completed Process {selected_process.id}"
            self.execution_log.append(log_entry)
            
            remaining_processes.remove(selected_process)  # Remove from waiting list
            completed_processes.append(selected_process)  # Add to completed list
        
        self.processes = completed_processes  # Save final state

        write_execution_csv(self.gantt_chart)  # Write Gantt chart to CSV
        return self.processes
    
    def calculate_cpu_usage(self) -> float:
        """
        Calculate CPU usage as the percentage of time spent executing processes.
        
        Returns:
            float: CPU usage as a percentage (0-100)
        """
        if not self.gantt_chart:
            return 0.0
        
        # Total simulation duration from first start to last end
        total_time = self.gantt_chart[-1][2] - self.gantt_chart[0][1]
        if total_time <= 0:
            return 0.0
        
        # Time when CPU was idle
        idle_time = sum(end_time - start_time for proc_id, start_time, end_time in self.gantt_chart if proc_id == "IDLE")
        
        # Time when CPU was actively processing
        active_time = total_time - idle_time
        cpu_usage = (active_time / total_time) * 100
        
        return cpu_usage

    def print_gantt_chart(self) -> None:
        """Print a simple Gantt chart of the execution sequence."""
        if not self.gantt_chart:
            print("No processes were executed.")
            return
            
        print("\nGantt Chart:")
        print("-" * 50)
        
        # Print each segment in Gantt chart
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
