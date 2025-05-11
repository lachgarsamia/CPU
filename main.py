#!/usr/bin/env python3

import os
import sys
import random
import time
import io
import copy
from typing import List, Dict
from contextlib import redirect_stdout
import uuid

# Import the scheduling algorithms and Process class
from ProcessClass.process import Process
from schedulers.FCFS import FCFSScheduler
from schedulers.SJF import SJFScheduler
from schedulers.PrioritySchedule import PriorityScheduler
from schedulers.RR import RoundRobinScheduler
from schedulers.RR_Priority import PriorityRoundRobinScheduler

# Import matplotlib for optional PNG output
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# Define scheduler types
SCHEDULERS = {
    "fcfs": {
        "name": "First Come First Serve",
        "class": FCFSScheduler,
        "params": [],
        "description": "Non-preemptive scheduler that executes processes in the order they arrive."
    },
    "sjf": {
        "name": "Shortest Job First",
        "class": SJFScheduler,
        "params": [],
        "description": "Non-preemptive scheduler that selects the process with the shortest burst time."
    },
    "priority": {
        "name": "Priority Scheduling",
        "class": PriorityScheduler,
        "params": [],
        "description": "Non-preemptive scheduler that selects the process with the highest priority (lowest value)."
    },
    "rr": {
        "name": "Round Robin",
        "class": RoundRobinScheduler,
        "params": ["time_quantum"],
        "description": "Preemptive scheduler that allocates each process a fixed time quantum."
    },
    "rrp": {
        "name": "Round Robin with Priority",
        "class": PriorityRoundRobinScheduler,
        "params": ["time_quantum"],
        "description": "Preemptive scheduler combining priority with Round Robin."
    }
}

class OutputTee:
    def __init__(self, terminal, buffer):
        self.terminal = terminal
        self.buffer = buffer

    def write(self, message):
        self.terminal.write(message)
        self.buffer.write(message)
    
    def flush(self):
        self.terminal.flush()
        self.buffer.flush()

# =============================================
# Terminal Related Functions
# =============================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print(f"\n{'=' * 80}")
    print(f"CPU SCHEDULING ALGORITHM VISUALIZER".center(80))
    print(f"{'=' * 80}")

def print_menu():
    print(f"\nAvailable Scheduling Algorithms:")
    print("-" * 50)
    for idx, (key, value) in enumerate(SCHEDULERS.items(), 1):
        print(f"{idx}. {value['name']} ({key})")
        print(f"   {value['description']}")
    print(f"\nOther Options:")
    print(f"{len(SCHEDULERS) + 1}. Compare All Algorithms")
    print(f"{len(SCHEDULERS) + 2}. Exit")
    print(f"Or type 'q' to quit")
    print("-" * 50)

def progress_bar(seconds: int):
    bar_length = 30
    start_time = time.time()
    while time.time() - start_time < seconds:
        elapsed = time.time() - start_time
        progress = elapsed / seconds
        filled = int(bar_length * progress)
        bar = '█' * filled + '-' * (bar_length - filled)
        sys.stdout.write(f'\rRunning scheduler [{bar}] {int(progress * 100)}%')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write(f'\rScheduler completed!{" " * 50}\n')
 
# ============================================
# Scanner Functions (Input Functions)
# ============================================

def get_int_input(prompt: str, min_val: int = None, max_val: int = None) -> int:
    while True:
        try:
            value = input(f"{prompt}").strip()
            if value.lower() in ['q', 'quit']:
                print(f"\nExiting program. Goodbye!")
                sys.exit(0)
            value = int(value)
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}.")
                continue
            return value
        except ValueError:
            print(f"Please enter a valid integer or 'q' to quit.")

def get_string_input(prompt: str) -> str:
    value = input(f"{prompt}").strip()
    if value.lower() in ['q', 'quit']:
        print(f"\nExiting program. Goodbye!")
        sys.exit(0)
    return value

def get_scheduler_params(scheduler_type: str) -> dict:
    params = {}
    for param in SCHEDULERS[scheduler_type]["params"]:
        if param == "time_quantum":
            params["time_quantum"] = get_int_input("Enter time quantum [default=2]: ", 1) or 2
        elif param == "aging_factor":
            params["aging_factor"] = get_int_input("Enter aging factor [default=1]: ", 1) or 1
    return params

def process_input_options():
    print(f"\nProcess Input Options:")
    print("1. Generate random processes")
    print("2. Enter processes manually")
    print("3. Load processes from file")
    print("4. Return to main menu")
    return get_int_input("Select an option: ", 1, 4)

# ==============================================
# Process Related Functions
# ==============================================

def generate_random_processes() -> List[Process]:
    num_processes = get_int_input("Number of processes [1-20]: ", 1, 20)
    use_seed = get_string_input("Use random seed? (y/n): ").lower() == 'y'
    seed = get_int_input("Enter seed value: ") if use_seed else None
    
    min_burst = get_int_input("Minimum burst time [1+]: ", 1)
    max_burst = get_int_input("Maximum burst time: ", min_burst)
    min_priority = get_int_input("Maximum priority [1+]: ", 1)
    max_priority = get_int_input("Minimum priority: ", min_priority)
    min_arrival = get_int_input("Minimum arrival time [0+]: ", 0)
    max_arrival = get_int_input("Maximum arrival time: ", min_arrival)

    if seed is not None:
        random.seed(seed)

    return [Process(
        id=i,
        burst_time=random.randint(min_burst, max_burst),
        priority=random.randint(min_priority, max_priority),
        arrival_time=random.randint(min_arrival, max_arrival)
    ) for i in range(1, num_processes + 1)]

def enter_processes_manually() -> List[Process]:
    num_processes = get_int_input("Number of processes [1+]: ", 1)
    processes = []
    for i in range(1, num_processes + 1):
        print(f"\nProcess {i}:")
        burst_time = get_int_input("Burst time [1+]: ", 1)
        priority = get_int_input("Priority [1+]: ", 1)
        arrival_time = get_int_input("Arrival time [0+]: ", 0)
        processes.append(Process(id=i, burst_time=burst_time, priority=priority, arrival_time=arrival_time))
    return processes

def load_processes_from_file() -> List[Process]:
    """Load processes from a CSV file, skipping header row if present."""
    filename = get_string_input("Enter the CSV file path: ")

    try:
        processes = []
        with open(filename, 'r') as file:
            lines = file.readlines()
            if not lines:
                print("File is empty.")
                return None
            
            # Check for header row
            start_line = 0
            first_line = lines[0].strip().split(',')
            if first_line and first_line[0].lower() in ['id', 'pid']:
                print("Skipping header row.")
                start_line = 1
            
            for line_num, line in enumerate(lines[start_line:], start_line + 1):
                try:
                    parts = line.strip().split(',')
                    if len(parts) < 4:
                        print(f"Line {line_num}: Insufficient data - skipping")
                        continue
                    
                    proc_id = int(parts[0])
                    burst_time = int(parts[1])
                    priority = int(parts[2])
                    arrival_time = int(parts[3])
                    
                    processes.append(Process(
                        id=proc_id,
                        burst_time=burst_time,
                        priority=priority,
                        arrival_time=arrival_time
                    ))
                except (ValueError, IndexError) as e:
                    print(f"Error parsing line {line_num}: {e}")
                    continue
        
        if not processes:
            print("No valid processes found in file.")
            return None
        
        print(f"Successfully loaded {len(processes)} processes.")
        return processes

    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

def save_processes_to_file(processes: List[Process]):
    if not processes:
        print(f"No processes to save.")
        return
    filename = get_string_input("Enter filename (CSV): ") + ".csv"
    try:
        with open(filename, 'w') as file:
            file.write("id,burst_time,priority,arrival_time\n")
            for p in processes:
                file.write(f"{p.id},{p.burst_time},{p.priority},{p.arrival_time}\n")
        print(f"Successfully saved {len(processes)} processes to {filename}")
    except Exception as e:
        print(f"Error saving file: {e}")

def display_processes(processes: List[Process]):
    if not processes:
        print(f"No processes to display.")
        return
    print(f"\nProcess List:")
    print("-" * 60)
    print(f"{'ID':<5} {'Burst':<8} {'Priority':<10} {'Arrival':<10}")
    print("-" * 60)
    for p in sorted(processes, key=lambda x: x.id):
        print(f"{p.id:<5} {p.burst_time:<8} {p.priority:<10} {p.arrival_time:<10}")
    print("-" * 60)

# =============================================
# Scheduler Execution Functions
# =============================================

def run_scheduler(scheduler_type: str, processes: List[Process], params: dict):
    if not processes:
        print(f"No processes to schedule.")
        return None

    scheduler_output = io.StringIO()
    original_stdout = sys.stdout
    scheduler_class = SCHEDULERS[scheduler_type]["class"]
    scheduler_name = SCHEDULERS[scheduler_type]["name"]
    
    print(f"\nRunning {scheduler_name}...")
    scheduler_params = {k: v for k, v in params.items() if k in SCHEDULERS[scheduler_type]["params"]}
    is_interactive = params.get("interactive", True)

    scheduler = scheduler_class(processes, **scheduler_params) if scheduler_params else scheduler_class(processes)
    
    progress_bar(2 if is_interactive else 1)
    
    sys.stdout = OutputTee(original_stdout, scheduler_output)
    completed_processes = scheduler.run()
    
    avg_waiting_time = sum(p.waiting_time for p in completed_processes) / len(completed_processes)
    avg_turnaround_time = sum(p.turnaround_time for p in completed_processes) / len(completed_processes)
    max_completion_time = max(p.completion_time for p in completed_processes)
    
    metrics = {
        "avg_waiting_time": avg_waiting_time,
        "avg_turnaround_time": avg_turnaround_time,
        "max_completion_time": max_completion_time,
        "completed_processes": completed_processes
    }

    print(f"\n{'='*80}")
    print(f"Results: {scheduler_name}".center(80))
    print(f"{'='*80}\n")
    
    print(f"Process Details:")
    print("-" * 70)
    print(f"{'ID':<5} {'Arrival':<6} {'Burst':<7} {'Priority':<6} {'Waiting':<7} {'Turnaround':<7} {'Completion':<7}")
    print("-" * 70)
    for p in sorted(completed_processes, key=lambda x: x.id):
        print(f"{p.id:<5} {p.arrival_time:<6} {p.burst_time:<7} {p.priority:<6} "
              f"{p.waiting_time:<7} {p.turnaround_time:<7} {p.completion_time:<7}")
    print("-" * 70)

    print(f"\nStatistics:")
    print("-" * 50)
    print(f"Avg Waiting Time   : {avg_waiting_time:.2f} units")
    print(f"Avg Turnaround Time: {avg_turnaround_time:.2f} units")
    print(f"Total Execution    : {max_completion_time} units")
    print(f"Throughput         : {(len(completed_processes)/max_completion_time):.4f} processes/unit")
    print(f"CPU Utilization    : {scheduler.calculate_cpu_usage():.2f} %")
    print("-" * 50)

    sys.stdout = original_stdout
    
    if is_interactive:
        if get_string_input("\nShow Gantt chart? (y/n): ").lower() == 'y':
            sys.stdout = OutputTee(original_stdout, scheduler_output)
            scheduler.print_gantt_chart()
            sys.stdout = original_stdout

        if get_string_input("Show execution log? (y/n): ").lower() == 'y':
            sys.stdout = OutputTee(original_stdout, scheduler_output)
            scheduler.print_execution_log()
            sys.stdout = original_stdout

        if get_string_input("Save schedule to CSV? (y/n): ").lower() == 'y':
            filename = get_string_input("Filename (no .csv): ") + ".csv"
            try:
                with open(filename, 'w') as f:
                    f.write("id,arrival_time,burst_time,priority,waiting_time,turnaround_time,completion_time\n")
                    for p in sorted(completed_processes, key=lambda x: x.id):
                        f.write(f"{p.id},{p.arrival_time},{p.burst_time},{p.priority},{p.waiting_time},{p.turnaround_time},{p.completion_time}\n")
                print(f"Saved to {filename}")
            except Exception as e:
                print(f"Error saving file: {e}")

        if get_string_input("Save output to text file? (y/n): ").lower() == 'y':
            filename = get_string_input("Filename (no .txt): ") + ".txt"
            try:
                with open(filename, 'w') as f:
                    f.write(scheduler_output.getvalue())
                print(f"Saved output to {filename}")
            except Exception as e:
                print(f"Error saving file: {e}")

        input(f"\nPress Enter to continue...")
    
    return metrics

# =============================================
# Comparison of Algorithms
# =============================================

def compare_all_schedulers(processes: List[Process]):
    if not processes:
        print(f"No processes to schedule.")
        return
    
    print(f"\nComparing all scheduling algorithms...")
    all_metrics = {}
    
    time_quantum = get_int_input("Time quantum for Round Robin [default=2]: ", 1) or 2
    params_store = {
        "rr": {"time_quantum": time_quantum},
        "rrp": {"time_quantum": time_quantum}
    }
    
    for scheduler_type, scheduler_info in SCHEDULERS.items():
        params = params_store.get(scheduler_type, {}).copy()
        params["interactive"] = False
        try:
            metrics = run_scheduler(scheduler_type, [p.copy() for p in processes], params)
            if metrics:
                all_metrics[scheduler_type] = metrics
        except Exception as e:
            print(f"Error running {scheduler_info['name']}: {e}")
    
    clear_screen()
    print_header()
    print(f"\nPerformance Comparison")
    print("=" * 80)
    print(f"{'Algorithm':<20} {'Avg Wait':<12} {'Avg Turn':<12} {'Max Comp':<12}")
    print("-" * 80)
    for scheduler_type, metrics in all_metrics.items():
        name = SCHEDULERS[scheduler_type]["name"][:18]
        print(f"{name:<20} {metrics['avg_waiting_time']:<12.2f} {metrics['avg_turnaround_time']:<12.2f} {metrics['max_completion_time']:<12}")
    print("-" * 80)
    
    if get_string_input("Save comparative Gantt chart as PNG? (y/n): ").lower() == 'y':
        try:
            fig, axes = plt.subplots(len(all_metrics), 1, figsize=(10, 2 * len(all_metrics)))
            if len(all_metrics) == 1:
                axes = [axes]
            for i, (scheduler_type, metrics) in enumerate(all_metrics.items()):
                ax = axes[i]
                name = SCHEDULERS[scheduler_type]["name"]
                for p in metrics["completed_processes"]:
                    if p.completion_time is not None:
                        start_time = p.completion_time - p.burst_time
                        ax.barh(f"P{p.id}", p.burst_time, left=start_time, height=0.4)
                ax.set_title(f"{name}")
                ax.set_xlabel("Time")
                ax.grid(True, alpha=0.3)
            plt.tight_layout()
            plot_filename = f"gantt_comparison_{uuid.uuid4().hex[:8]}.png"
            plt.savefig(plot_filename, bbox_inches='tight')
            plt.close()
            print(f"Comparative Gantt chart saved as {plot_filename}")
        except Exception as e:
            print(f"Error generating plot: {e}")
    
    if get_string_input("Save comparison to CSV? (y/n): ").lower() == 'y':
        filename = get_string_input("Filename (no .csv): ") + ".csv"
        try:
            with open(filename, 'w') as f:
                f.write("Algorithm,Avg Waiting Time,Avg Turnaround Time,Max Completion Time\n")
                for scheduler_type, metrics in all_metrics.items():
                    name = SCHEDULERS[scheduler_type]["name"]
                    f.write(f"{name},{metrics['avg_waiting_time']:.2f},{metrics['avg_turnaround_time']:.2f},{metrics['max_completion_time']}\n")
            print(f"Saved comparison to {filename}")
        except Exception as e:
            print(f"Error saving file: {e}")
    
    input(f"\nPress Enter to continue...")

# =============================================
# Main Function
# =============================================

def main():
    processes = None
    while True:
        clear_screen()
        print_header()
        
        if processes:
            print(f"\n{len(processes)} processes loaded")
            if get_string_input("View processes? (y/n): ").lower() == 'y':
                display_processes(processes)
        else:
            print(f"\nNo processes loaded.")
        
        print_menu()
        try:
            choice_input = get_string_input("Enter choice: ")
            if choice_input.lower() in ['q', 'quit']:
                print(f"\nExiting program. Goodbye!")
                break
            
            choice = int(choice_input)
            if choice == len(SCHEDULERS) + 2:
                print(f"\nExiting program. Goodbye!")
                break
            
            if choice == len(SCHEDULERS) + 1:
                if not processes:
                    print(f"No processes loaded. Please input processes first.")
                    input(f"Press Enter to continue...")
                    continue
                compare_all_schedulers([p.copy() for p in processes])
                continue
            
            scheduler_type = list(SCHEDULERS.keys())[choice - 1]
            
            if not processes or get_string_input("Use current processes? (y/n): ").lower() != 'y':
                input_choice = process_input_options()
                if input_choice == 1:
                    processes = generate_random_processes()
                    if processes and get_string_input("Save processes to file? (y/n): ").lower() == 'y':
                        save_processes_to_file(processes)
                elif input_choice == 2:
                    processes = enter_processes_manually()
                    if processes and get_string_input("Save processes to file? (y/n): ").lower() == 'y':
                        save_processes_to_file(processes)
                elif input_choice == 3:
                    new_processes = load_processes_from_file()
                    if new_processes:
                        processes = new_processes
                elif input_choice == 4:
                    continue
            
            if not processes:
                print(f"No processes available. Please input processes first.")
                input(f"Press Enter to continue...")
                continue
            
            params = get_scheduler_params(scheduler_type)
            params["interactive"] = True
            run_scheduler(scheduler_type, [p.copy() for p in processes], params)
            
            if get_string_input("Compare with other algorithms? (y/n): ").lower() == 'y':
                compare_all_schedulers([p.copy() for p in processes])
            
        except ValueError:
            print(f"Invalid input. Please enter a number or 'q' to quit.")
            input(f"Press Enter to continue...")
        except KeyboardInterrupt:
            print(f"Operation cancelled by user.")
            input(f"Press Enter to continue...")
        except Exception as e:
            print(f"An error occurred: {e}")
            input(f"Press Enter to continue...")

if __name__ == "__main__":
    main()