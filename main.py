#!/usr/bin/env python3

import os
import sys
import random
import argparse
from typing import List, Dict, Type
import time
import io
import copy
from contextlib import redirect_stdout

# Import the scheduling algorithms and Process class
from ProcessClass.process import Process
from schedulers.FCFS import FCFSScheduler
from schedulers.SJF import SJFScheduler
from schedulers.PrioritySchedule import PriorityScheduler
from schedulers.RR import RoundRobinScheduler
from schedulers.RR_Priority import PriorityRoundRobinScheduler

# Import matplotlib for optional PNG output
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# Define scheduler types for easy referencing
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
        "description": "Preemptive scheduler that allocates each process a fixed time quantum in a circular manner."
    },
    "rrp": {
        "name": "Round Robin with Priority",
        "class": PriorityRoundRobinScheduler,
        "params": ["time_quantum", "aging_factor"],
        "description": "Preemptive scheduler combining priority with Round Robin. Higher priority processes are scheduled first."
    }
}

class OutputTee:
    """Class to tee output to both terminal and buffer"""
    def __init__(self, terminal, buffer):
        self.terminal = terminal
        self.buffer = buffer

    def write(self, message):
        self.terminal.write(message)
        self.buffer.write(message)
    
    def flush(self):
        self.terminal.flush()
        self.buffer.flush()

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    print("\n" + "=" * 80)
    print("CPU SCHEDULING ALGORITHM VISUALIZER".center(80))
    print("=" * 80)

def print_menu():
    """Print the main menu options."""
    print("\nAvailable Scheduling Algorithms:")
    print("-" * 50)

    for idx, (key, value) in enumerate(SCHEDULERS.items(), 1):
        print(f"{idx}. {value['name']} ({key})")
        print(f"   {value['description']}")

    print("\nOther Options:")
    print(f"{len(SCHEDULERS) + 1}. Compare All Scheduling Algorithms")
    print(f"{len(SCHEDULERS) + 2}. Exit")
    print("Or type 'q' or 'quit' to exit immediately")
    print("-" * 50)

def get_int_input(prompt: str, min_val: int = None, max_val: int = None) -> int:
    """Get integer input from user with validation."""
    while True:
        try:
            value = input(prompt).strip()
            if value.lower() in ['q', 'quit']:
                print("\nExiting program. Goodbye!")
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
            print("Please enter a valid integer or 'q' to quit.")

def get_string_input(prompt: str) -> str:
    """Get string input from user with quit option."""
    value = input(prompt).strip()
    if value.lower() in ['q', 'quit']:
        print("\nExiting program. Goodbye!")
        sys.exit(0)
    return value

def get_scheduler_params(scheduler_type: str) -> dict:
    """Get scheduler-specific parameters from user."""
    params = {}

    for param in SCHEDULERS[scheduler_type]["params"]:
        if param == "time_quantum":
            params["time_quantum"] = get_int_input("Enter time quantum: ", 1)
        elif param == "aging_factor":
            params["aging_factor"] = get_int_input("Enter aging factor: ", 1)

    return params

def process_input_options():
    """Show process input options and get user selection."""
    print("\nProcess Input Options:")
    print("1. Generate random processes")
    print("2. Enter processes manually")
    print("3. Load processes from file")
    print("4. Return to main menu")

    choice = get_int_input("Select an option: ", 1, 4)
    return choice

def generate_random_processes() -> List[Process]:
    """Generate random processes based on user input."""
    num_processes = get_int_input("Enter number of processes to generate: ", 1, 20)
    use_seed = get_string_input("Use random seed for reproducibility? (y/n): ").lower() == 'y'

    seed = None
    if use_seed:
        seed = get_int_input("Enter seed value: ")

    min_burst = get_int_input("Enter minimum burst time: ", 1)
    max_burst = get_int_input("Enter maximum burst time: ", min_burst)

    min_priority = get_int_input("Enter maximum priority (smaller value = higher priority): ", 1)
    max_priority = get_int_input("Enter minimum priority: ", min_priority)

    min_arrival = get_int_input("Enter minimum arrival time: ", 0)
    max_arrival = get_int_input("Enter maximum arrival time: ", min_arrival)

    if seed is not None:
        random.seed(seed)

    processes = []
    for i in range(1, num_processes + 1):
        processes.append(Process(
            id=i,
            burst_time=random.randint(min_burst, max_burst),
            priority=random.randint(min_priority, max_priority),
            arrival_time=random.randint(min_arrival, max_arrival)
        ))

    return processes

def enter_processes_manually() -> List[Process]:
    """Allow user to enter processes manually."""
    num_processes = get_int_input("Enter number of processes: ", 1)
    processes = []

    for i in range(1, num_processes + 1):
        print(f"\nEnter details for Process {i}:")
        burst_time = get_int_input("Burst time: ", 1)
        priority = get_int_input("Priority (smaller value = higher priority): ", 1)
        arrival_time = get_int_input("Arrival time: ", 0)
        
        processes.append(Process(
            id=i,
            burst_time=burst_time,
            priority=priority,
            arrival_time=arrival_time
        ))

    return processes

def load_processes_from_file() -> List[Process]:
    """Load processes from a CSV file."""
    filename = get_string_input("Enter the CSV file path: ")

    try:
        processes = []
        with open(filename, 'r') as file:
            for line_num, line in enumerate(file, 1):
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
    """Save processes to a CSV file."""
    if not processes:
        print("No processes to save.")
        return

    filename = get_string_input("Enter filename to save processes (CSV): ")

    try:
        with open(filename, 'w') as file:
            file.write("id,burst_time,priority,arrival_time\n")
            for p in processes:
                file.write(f"{p.id},{p.burst_time},{p.priority},{p.arrival_time}\n")
        print(f"Successfully saved {len(processes)} processes to {filename}")
    except Exception as e:
        print(f"Error saving file: {e}")

def display_processes(processes: List[Process]):
    """Display the list of processes in a table format."""
    if not processes:
        print("No processes to display.")
        return

    print("\nProcess List:")
    print("-" * 60)
    print(f"{'ID':<5} {'Burst Time':<12} {'Priority':<10} {'Arrival Time':<15}")
    print("-" * 60)

    for p in sorted(processes, key=lambda x: x.id):
        print(f"{p.id:<5} {p.burst_time:<12} {p.priority:<10} {p.arrival_time:<15}")

    print("-" * 60)

def animation_spinner(seconds: int):
    """Display a spinner animation for the given number of seconds."""
    spinner = ['|', '/', '-', '\\']
    start_time = time.time()

    i = 0
    while time.time() - start_time < seconds:
        sys.stdout.write(f"\rRunning scheduler {spinner[i % len(spinner)]}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1

    sys.stdout.write('\rScheduler completed!    \n')

def print_ascii_gantt_chart(completed_processes: List[Process], scheduler_name: str):
    """Print an ASCII Gantt chart in the terminal."""
    if not completed_processes:
        print("No processes to display in Gantt chart.")
        return

    print(f"\nASCII Gantt Chart for {scheduler_name}:")
    print("-" * 80)

    # Determine the maximum time for the chart
    max_time = max(p.completion_time for p in completed_processes if p.completion_time is not None)
    time_scale = max(1, max_time // 50)  # Scale to fit terminal (approx 50 chars wide)

    # Create a timeline for each process
    for p in sorted(completed_processes, key=lambda x: x.id):
        if p.completion_time is None:
            continue
        start_time = p.completion_time - p.burst_time
        # Calculate number of blocks to represent the process
        blocks = max(1, int(p.burst_time / time_scale))
        # Calculate starting position
        start_blocks = int(start_time / time_scale)
        # Create the bar
        bar = " " * start_blocks + "█" * blocks
        print(f"P{p.id:<2} |{bar}")

    # Print time axis
    time_marks = range(0, max_time + 1, max(1, max_time // 10))
    time_line = "   " + "".join(f"{t:^{max(1, max_time // 10)}}" for t in time_marks)
    print("-" * 80)
    print(time_line)
    print("   Time")

def run_scheduler(scheduler_type: str, processes: List[Process], params: dict):
    """Run the selected scheduler with given processes and parameters."""
    if not processes:
        print("No processes to schedule.")
        return None

    # Initialize a buffer for the scheduler output
    scheduler_output = io.StringIO()
    original_stdout = sys.stdout

    # Select and initialize scheduler
    scheduler_class = SCHEDULERS[scheduler_type]["class"]
    scheduler_name = SCHEDULERS[scheduler_type]["name"]

    print(f"\nRunning {scheduler_name} scheduler...")

    # Create a clean copy of params without the 'interactive' flag
    scheduler_params = {k: v for k, v in params.items() if k in SCHEDULERS[scheduler_type]["params"]}
    is_interactive = params.get("interactive", True)

    if scheduler_type in ["fcfs", "sjf", "priority"]:
        scheduler = scheduler_class(processes)
    else:
        scheduler = scheduler_class(processes, **scheduler_params)

    # Animation spinner
    animation_time = 2 if is_interactive else 1
    animation_spinner(animation_time)

    # Start capturing output for scheduler results
    print(f"\n{'='*80}")
    print(f"SCHEDULER RESULTS: {scheduler_name}".center(80))
    print(f"{'='*80}\n")

    # Switch to capturing to our buffer
    sys.stdout = OutputTee(original_stdout, scheduler_output)

    # Run scheduler
    completed_processes = scheduler.run()
    
    # Get performance metrics
    avg_waiting_time = sum(p.waiting_time for p in completed_processes) / len(completed_processes)
    avg_turnaround_time = sum(p.turnaround_time for p in completed_processes) / len(completed_processes)
    max_completion_time = max(p.completion_time for p in completed_processes)
    
    # Performance metrics dict
    metrics = {
        "avg_waiting_time": avg_waiting_time,
        "avg_turnaround_time": avg_turnaround_time,
        "max_completion_time": max_completion_time,
        "completed_processes": completed_processes
    }

    # Display process details
    print("\nProcess Details:")
    print("-" * 80)
    print(f"{'ID':<5} {'Arrival':<10} {'Burst':<10} {'Priority':<10} {'Wait':<10} {'Turnaround':<12} {'Completion':<12}")
    print("-" * 80)
    for p in sorted(completed_processes, key=lambda x: x.id):
        print(f"{p.id:<5} {p.arrival_time:<10} {p.burst_time:<10} {p.priority:<10} "
              f"{p.waiting_time:<10} {p.turnaround_time:<12} {p.completion_time:<12}")
    print("-" * 80)

    # Display scheduling results
    scheduler.print_results()

    # Switch back to original stdout for interactive mode
    if is_interactive:
        sys.stdout = original_stdout
        
        # Textual Gantt chart
        show_gantt = get_string_input("\nShow Gantt chart? (y/n): ").lower() == 'y'
        if show_gantt:
            sys.stdout = OutputTee(original_stdout, scheduler_output)
            scheduler.print_gantt_chart()
            sys.stdout = original_stdout

        # Execution log
        show_exec_log = get_string_input("\nShow execution log? (y/n): ").lower() == 'y'
        if show_exec_log:
            sys.stdout = OutputTee(original_stdout, scheduler_output)
            scheduler.print_execution_log()
            sys.stdout = original_stdout

        # Save completed schedule to CSV
        if get_string_input("\nSave completed schedule to CSV? (y/n): ").lower() == 'y':
            filename = get_string_input("Enter filename to save (without .csv extension): ") + ".csv"
            try:
                with open(filename, 'w') as f:
                    f.write("id,arrival_time,burst_time,priority,waiting_time,turnaround_time,completion_time\n")
                    for p in sorted(completed_processes, key=lambda x: x.id):
                        f.write(f"{p.id},{p.arrival_time},{p.burst_time},{p.priority},{p.waiting_time},{p.turnaround_time},{p.completion_time}\n")
                print(f"Successfully saved completed processes to {filename}")
            except Exception as e:
                print(f"Error saving file: {e}")

        # ASCII Gantt chart in terminal
        if get_string_input("\nShow ASCII Gantt Chart in terminal? (y/n): ").lower() == 'y':
            print_ascii_gantt_chart(completed_processes, scheduler_name)

        # Optional Matplotlib Gantt chart saved as PNG
        if get_string_input("\nSave Gantt Chart as PNG using matplotlib? (y/n): ").lower() == 'y':
            try:
                fig, ax = plt.subplots()
                for p in completed_processes:
                    if p.completion_time is not None:
                        start_time = p.completion_time - p.burst_time
                        ax.barh(f"P{p.id}", p.burst_time, left=start_time)
                ax.set_xlabel("Time")
                ax.set_title(f"Gantt Chart - {scheduler_name}")

                plot_filename = f"gantt_chart_{scheduler_type}.png"
                plt.savefig(plot_filename)
                plt.close()

                print(f"Gantt chart saved as {plot_filename}")

            except ImportError:
                print("matplotlib is not installed. Install it using 'pip install matplotlib'.")
            except Exception as e:
                print(f"Error generating plot: {e}")

        # Save scheduler output to a text file
        if get_string_input("\nSave scheduler output to a text file? (y/n): ").lower() == 'y':
            filename = get_string_input("Enter filename to save output (without .txt extension): ") + ".txt"
            try:
                with open(filename, 'w') as f:
                    f.write(scheduler_output.getvalue())
                print(f"Successfully saved scheduler output to {filename}")
            except Exception as e:
                print(f"Error saving file: {e}")

        input("\nPress Enter to continue...")
    else:
        sys.stdout = original_stdout
    
    return metrics

def compare_all_schedulers(processes: List[Process]):
    """Run all scheduling algorithms and compare their performance metrics."""
    if not processes:
        print("No processes to schedule.")
        return
    
    print("\nComparing all scheduling algorithms with the current set of processes...")
    
    all_metrics = {}
    
    params_store = {}
    print("\nEnter parameters for schedulers (or press Enter for defaults):")
    
    time_quantum_input = get_string_input("Time quantum for Round Robin algorithms [default=2]: ")
    time_quantum = int(time_quantum_input) if time_quantum_input.strip() else 2
    
    aging_factor_input = get_string_input("Aging factor for Priority Round Robin [default=1]: ")
    aging_factor = int(aging_factor_input) if aging_factor_input.strip() else 1
    
    params_store["rr"] = {"time_quantum": time_quantum}
    params_store["rrp"] = {"time_quantum": time_quantum, "aging_factor": aging_factor}
    
    for scheduler_type, scheduler_info in SCHEDULERS.items():
        params = params_store.get(scheduler_type, {}).copy()
        params["interactive"] = False
        
        try:
            metrics = run_scheduler(scheduler_type, [p.copy() for p in processes], params)
            if metrics:
                all_metrics[scheduler_type] = metrics
        except Exception as e:
            print(f"Error running {scheduler_info['name']}: {e}")
            continue
    
    clear_screen()
    print_header()
    print("\nPerformance Metrics Comparison")
    print("=" * 80)
    
    print(f"{'Algorithm':<20} {'Avg Wait Time':<15} {'Avg Turnaround':<15} {'Max Completion':<15}")
    print("-" * 80)
    
    for scheduler_type, metrics in all_metrics.items():
        name = SCHEDULERS[scheduler_type]["name"]
        print(f"{name:<20} {metrics['avg_waiting_time']:<15.2f} {metrics['avg_turnaround_time']:<15.2f} {metrics['max_completion_time']:<15}")
    
    print("-" * 80)
    
    if get_string_input("\nShow ASCII Gantt Charts for all schedulers? (y/n): ").lower() == 'y':
        for scheduler_type, metrics in all_metrics.items():
            print_ascii_gantt_chart(metrics["completed_processes"], SCHEDULERS[scheduler_type]["name"])
    
    if get_string_input("\nSave comparative Gantt Chart as PNG using matplotlib? (y/n): ").lower() == 'y':
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
                        ax.barh(f"P{p.id}", p.burst_time, left=start_time)
                
                ax.set_title(f"{name}")
                ax.set_xlabel("Time")
            
            plt.tight_layout()
            
            plot_filename = "gantt_comparison.png"
            plt.savefig(plot_filename)
            plt.close()
            
            print(f"Comparative Gantt chart saved as {plot_filename}")

        except ImportError:
            print("matplotlib is not installed. Install it using 'pip install matplotlib'.")
        except Exception as e:
            print(f"Error generating plot: {e}")
    
    if get_string_input("\nSave comparison results to CSV? (y/n): ").lower() == 'y':
        filename = get_string_input("Enter filename to save comparison (without .csv extension): ") + ".csv"
        try:
            with open(filename, 'w') as f:
                f.write("Algorithm,Average Waiting Time,Average Turnaround Time,Max Completion Time\n")
                for scheduler_type, metrics in all_metrics.items():
                    name = SCHEDULERS[scheduler_type]["name"]
                    f.write(f"{name},{metrics['avg_waiting_time']:.2f},{metrics['avg_turnaround_time']:.2f},{metrics['max_completion_time']}\n")
            print(f"Successfully saved comparison results to {filename}")
        except Exception as e:
            print(f"Error saving file: {e}")
    
    input("\nPress Enter to continue...")

def main():
    """Main application function."""
    processes = None

    while True:
        clear_screen()
        print_header()
        
        if processes:
            print(f"\nCurrent set: {len(processes)} processes loaded")
            if get_string_input("View loaded processes? (y/n): ").lower() == 'y':
                display_processes(processes)
        else:
            print("\nNo processes loaded.")
        
        print_menu()
        
        try:
            choice_input = get_string_input("Enter your choice: ")
            if choice_input.lower() in ['q', 'quit']:
                print("\nExiting program. Goodbye!")
                break
            
            choice = int(choice_input)
            
            if choice == len(SCHEDULERS) + 2:
                print("\nExiting program. Goodbye!")
                break
            
            if choice == len(SCHEDULERS) + 1:
                if not processes:
                    print("\nNo processes loaded. Please generate or input processes first.")
                    input("Press Enter to continue...")
                    continue
                    
                process_copies = [p.copy() for p in processes]
                compare_all_schedulers(process_copies)
                continue
            
            scheduler_type = list(SCHEDULERS.keys())[choice - 1]
            
            if not processes or get_string_input("Use current processes? (y/n): ").lower() != 'y':
                input_choice = process_input_options()
                
                if input_choice == 1:
                    processes = generate_random_processes()
                    if processes and get_string_input("Save these processes to file? (y/n): ").lower() == 'y':
                        save_processes_to_file(processes)
                elif input_choice == 2:
                    processes = enter_processes_manually()
                    if processes and get_string_input("Save these processes to file? (y/n): ").lower() == 'y':
                        save_processes_to_file(processes)
                elif input_choice == 3:
                    new_processes = load_processes_from_file()
                    if new_processes:
                        processes = new_processes
                elif input_choice == 4:
                    continue
            
            if not processes:
                print("No processes available. Please generate or input processes first.")
                input("Press Enter to continue...")
                continue
            
            params = get_scheduler_params(scheduler_type)
            params["interactive"] = True
            
            process_copies = [p.copy() for p in processes]
            run_scheduler(scheduler_type, process_copies, params)
            
            if get_string_input("\nWould you like to compare this algorithm with others? (y/n): ").lower() == 'y':
                process_copies = [p.copy() for p in processes]
                compare_all_schedulers(process_copies)
            
        except ValueError:
            print("\nInvalid input. Please enter a number or 'q' to quit.")
            input("Press Enter to continue...")
            continue
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            input("Press Enter to continue...")
            continue
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            import traceback
            traceback.print_exc()
            input("Press Enter to continue...")
            continue

if __name__ == "__main__":
    main()