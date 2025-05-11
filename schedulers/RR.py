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

    Executing processes in a circular order, giving each one a fixed time slice (quantum).
    This is a preemptive scheduling approach.
    
    Attributes:
        processes (List[Process]): List of processes to be scheduled.
        time_quantum (int): Duration of each time slice allocated to a process.
        current_time (int): Keeps track of simulation progress.
        execution_log (List[str]): Records details of process execution events.
        gantt_chart (List[tuple]): Stores data for timeline visualization.
    """

    def __init__(self, processes: List[Process], time_quantum: int = 2):
        """
        Setting up the scheduler with the provided processes and quantum.

        Args:
            processes: List of Process instances to simulate.
            time_quantum: Fixed duration of CPU allocation per cycle.
        """
        self.original_processes = copy.deepcopy(processes)
        self.processes = copy.deepcopy(processes)
        self.time_quantum = time_quantum
        self.current_time = 0
        self.execution_log = []
        self.gantt_chart = []

    def run(self) -> List[Process]:
        """
        Executing the Round Robin scheduling simulation.

        Returns:
            List of processes with updated metrics.
        """
        if not self.processes:
            return []

        # Preparing each process for simulation
        for p in self.processes:
            p.remaining_time = p.burst_time
            p.first_response = False
            p.finished = False

        # Sorting processes by arrival to ensure correct startup order
        self.processes.sort(key=lambda p: p.arrival_time)
        ready_queue = deque()
        completed = 0
        n = len(self.processes)
        self.current_time = self.processes[0].arrival_time

        while completed < n:
            # Gathering processes that have arrived and are not yet finished or queued
            new_arrivals = [p for p in self.processes
                            if p.arrival_time <= self.current_time and not p.finished and p not in ready_queue]

            # Ensuring the current process isn't added twice
            if 'process' in locals():
                new_arrivals = [p for p in new_arrivals if p != process]

            # Adding new arrivals to the ready queue while maintaining order
            new_arrivals.sort(key=lambda p: p.arrival_time)
            ready_queue.extend(new_arrivals)

            if ready_queue:
                # Fetching the next process to execute
                process = ready_queue.popleft()

                # Recording first response time
                if not process.first_response:
                    process.response_time = self.current_time - process.arrival_time
                    process.first_response = True

                # Determining the time slice for execution
                exec_time = min(self.time_quantum, process.remaining_time)
                self.execution_log.append(f"Time {self.current_time}: Running Process {process.id} for {exec_time} units")
                self.gantt_chart.append((process.id, self.current_time, self.current_time + exec_time))

                self.current_time += exec_time
                process.remaining_time -= exec_time

                # Adding new arrivals that appeared during this time slice
                for p in self.processes:
                    if (p.arrival_time <= self.current_time and not p.finished and p not in ready_queue and p != process):
                        ready_queue.append(p)

                if process.remaining_time == 0:
                    # Completing the process
                    process.completion_time = self.current_time
                    process.turnaround_time = process.completion_time - process.arrival_time
                    process.waiting_time = process.turnaround_time - process.burst_time
                    process.finished = True
                    self.execution_log.append(f"Time {self.current_time}: Completed Process {process.id}")
                    completed += 1
                else:
                    # Re-queuing the process for the next cycle
                    ready_queue.append(process)
            else:
                # Recording idle time when no process is available
                self.gantt_chart.append(("IDLE", self.current_time, self.current_time + 1))
                self.execution_log.append(f"Time {self.current_time}: CPU idle")
                self.current_time += 1

        # Saving the Gantt chart results
        write_execution_csv(self.gantt_chart)
        return self.processes

    def calculate_cpu_usage(self) -> float:
        """
        Calculating how efficiently the CPU was utilized.

        Returns:
            float: Percentage of time the CPU spent executing processes.
        """
        if not self.gantt_chart:
            return 0.0

        total_time = self.gantt_chart[-1][2] - self.gantt_chart[0][1]
        if total_time <= 0:
            return 0.0

        idle_time = sum(end_time - start_time for proc_id, start_time, end_time in self.gantt_chart if proc_id == "IDLE")
        active_time = total_time - idle_time
        cpu_usage = (active_time / total_time) * 100
        return cpu_usage

    def print_gantt_chart(self) -> None:
        """
        Displaying the Gantt chart showing execution order and durations.
        """
        if not self.gantt_chart:
            print("No processes were executed.")
            return

        print("\nGantt Chart:")
        print("-" * 50)
        for proc_id, start_time, end_time in self.gantt_chart:
            print(f"Time {start_time:<3} | {'IDLE' if proc_id == 'IDLE' else f'P{proc_id}'} | Time {end_time:<3}")
        print("-" * 50)

    def print_execution_log(self) -> None:
        """
        Displaying the log of events during the scheduling simulation.
        """
        if not self.execution_log:
            print("No execution log available.")
            return

        print("\nExecution Log:")
        print("-" * 80)
        for entry in self.execution_log:
            print(entry)
        print("-" * 80)
