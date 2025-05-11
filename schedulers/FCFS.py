from dataclasses import dataclass, field
from typing import Optional, List
import random
import csv
import argparse
import copy
from ProcessClass.process import Process
from utils.file_io import write_execution_csv


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
        self.processes = copy.deepcopy(processes)  # Create a deep copy to preserve original list
        self.current_time = 0                      # Track current simulation time
        self.execution_log = []                    # Log of events during execution
        self.gantt_chart = []                      # Stores execution timeline for Gantt chart
    
    def run(self) -> List[Process]:
        """
        Run the FCFS Scheduling algorithm.
        Returns:
            List of processes after scheduling with calculated metrics
        """
        if not self.processes:
            return []  # Return empty if there are no processes
        
        self.processes.sort(key=lambda p: p.arrival_time)  # Sort processes by arrival time
        self.current_time = self.processes[0].arrival_time  # Start time is first arrival

        for process in self.processes:
            # If CPU is idle before the process arrives, log the idle period
            if self.current_time < process.arrival_time:
                self.gantt_chart.append(("IDLE", self.current_time, process.arrival_time))
                self.current_time = process.arrival_time  # Advance time to arrival

            process.state = "READY"  # Update process state
            process.last_running_time = max(process.arrival_time, self.current_time)  # Set last run time
            process.waiting_time = self.current_time - process.arrival_time  # Calculate waiting time

            log_entry = f"Time {self.current_time}: Starting Process {process.id}"  # Log process start
            self.execution_log.append(log_entry)

            time_used = process.execute(process.burst_time)  # Execute process for burst time

            # Log execution to Gantt chart
            self.gantt_chart.append((process.id, self.current_time, self.current_time + time_used))

            self.current_time += time_used  # Advance current time
            process.complete(self.current_time)  # Mark process as completed

            log_entry = f"Time {self.current_time}: Completed Process {process.id}"  # Log process completion
            self.execution_log.append(log_entry)

            write_execution_csv(self.gantt_chart)  # Save Gantt chart to CSV

        return self.processes  # Return the updated process list

    def calculate_cpu_usage(self) -> float:
        """
        Calculate CPU usage as the percentage of time spent executing processes.
        
        Returns:
            float: CPU usage as a percentage (0-100)
        """
        if not self.gantt_chart:
            return 0.0  # No execution recorded
        
        # Calculate total time from first start to last end
        total_time = self.gantt_chart[-1][2] - self.gantt_chart[0][1]
        if total_time <= 0:
            return 0.0
        
        # Total idle time from Gantt chart
        idle_time = sum(end_time - start_time for proc_id, start_time, end_time in self.gantt_chart if proc_id == "IDLE")
        
        # CPU usage is active time divided by total time
        active_time = total_time - idle_time
        cpu_usage = (active_time / total_time) * 100
        
        return cpu_usage
    
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
                chart_bar = f"| {'IDLE':<{duration}} "  # Visualize idle time
            else:
                chart_bar = f"| P{proc_id:<{duration}} "  # Visualize process execution
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
            print(entry)  # Display each log entry
        print("-" * 50)
