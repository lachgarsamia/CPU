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
    
    Selecting the process with the shortest burst time among all available processes.
    This is a non-preemptive scheduling method.
    """
    
    def __init__(self, processes: List[Process]):
        """
        Initializing the SJF scheduler with a list of processes.
        
        Args:
            processes: List of Process objects to be scheduled
        """
        self.processes = copy.deepcopy(processes)  # Working with a deep copy to preserve original input
        self.current_time = 0                      # Tracking the current time of simulation
        self.execution_log = []                    # Storing the sequence of process events
        self.gantt_chart = []                      # Building Gantt chart entries for visual timeline
    
    
    def run(self) -> List[Process]:
        """
        Running the SJF scheduling algorithm.

        Returns:
            List of scheduled processes with computed metrics
        """
        if not self.processes:
            return []

        # Sorting processes by arrival time to start scheduling in order
        self.processes.sort(key=lambda p: p.arrival_time)
        self.current_time = self.processes[0].arrival_time

        remaining_processes = copy.deepcopy(self.processes)
        completed_processes = []

        while remaining_processes:
            # Collecting all processes that have arrived by the current time
            available_processes = [p for p in remaining_processes if p.arrival_time <= self.current_time]

            if not available_processes:
                # Simulating idle time until the next process arrives
                next_arrival = min(p.arrival_time for p in remaining_processes)
                self.gantt_chart.append(("IDLE", self.current_time, next_arrival))
                self.execution_log.append(f"Time {self.current_time}: CPU idle until {next_arrival}")
                self.current_time = next_arrival
                continue

            # Selecting the process with the shortest burst time (breaking ties by arrival time)
            selected_process = min(available_processes, key=lambda p: (p.burst_time, p.arrival_time))

            # Updating process state and timing information
            selected_process.state = "READY"
            selected_process.last_running_time = max(selected_process.arrival_time, self.current_time)
            selected_process.waiting_time = self.current_time - selected_process.arrival_time

            # Logging the start of execution
            log_entry = f"Time {self.current_time}: Starting Process {selected_process.id} (burst time: {selected_process.burst_time})"
            self.execution_log.append(log_entry)

            # Calculating start and end times
            start_time = self.current_time
            end_time = start_time + selected_process.burst_time
            self.gantt_chart.append((selected_process.id, start_time, end_time))
            self.current_time = end_time

            # Setting completion and turnaround times
            selected_process.completion_time = self.current_time
            selected_process.turnaround_time = selected_process.completion_time - selected_process.arrival_time

            # Logging process completion
            log_entry = f"Time {self.current_time}: Completed Process {selected_process.id}"
            self.execution_log.append(log_entry)

            # Moving process from remaining to completed list
            remaining_processes.remove(selected_process)
            completed_processes.append(selected_process)

        # Updating internal state to reflect completed scheduling
        self.processes = completed_processes

        # Writing Gantt chart data to CSV file
        write_execution_csv(self.gantt_chart)
        return self.processes

    def calculate_cpu_usage(self) -> float:
        """
        Calculating CPU usage as the percentage of active processing time.

        Returns:
            float: CPU usage percentage (0–100)
        """
        if not self.gantt_chart:
            return 0.0
        
        # Determining total simulated time from first to last recorded event
        total_time = self.gantt_chart[-1][2] - self.gantt_chart[0][1]
        if total_time <= 0:
            return 0.0
        
        # Summing the time intervals where the CPU was idle
        idle_time = sum(end_time - start_time for proc_id, start_time, end_time in self.gantt_chart if proc_id == "IDLE")
        
        # Calculating CPU active time and converting to percentage
        active_time = total_time - idle_time
        cpu_usage = (active_time / total_time) * 100
        
        return cpu_usage
        
    def print_gantt_chart(self) -> None:
        """Displaying a simple Gantt chart representing the execution timeline."""
        if not self.gantt_chart:
            print("No processes were executed.")
            return
            
        print("\nGantt Chart:")
        print("-" * 50)
        
        for proc_id, start_time, end_time in self.gantt_chart:
            duration = end_time - start_time
            if proc_id == "IDLE":
                chart_bar = f"| {'IDLE':<{duration}} "  # Visualizing idle periods
            else:
                chart_bar = f"| P{proc_id:<{duration}} "  # Visualizing process execution
            print(f"Time {start_time:<3} {chart_bar}| Time {end_time:<3}")
            
        print("-" * 50)
    
    def print_execution_log(self) -> None:
        """Displaying the sequence of process execution events."""
        if not self.execution_log:
            print("No execution log available.")
            return
            
        print("\nExecution Log:")
        print("-" * 50)
        for entry in self.execution_log:
            print(entry)
        print("-" * 50)
