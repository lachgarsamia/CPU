#!/usr/bin/env python3

import os
import sys
import random
import argparse
from typing import List, Dict, Type
import time

# Import the scheduling algorithms and Process class
from ProcessClass.process import Process
from Algorithms.FCFS import FCFSScheduler
from Algorithms.SJF import SJFScheduler
from Algorithms.PrioritySchedule import PriorityScheduler
from Algorithms.RR import RoundRobinScheduler
from Algorithms.RR_Priority import RoundRobinPriorityScheduler

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
        "class": RoundRobinPriorityScheduler,
        "params": ["time_quantum", "aging_factor"],
        "description": "Preemptive scheduler combining priority with Round Robin. Higher priority processes are scheduled first."
    }
}

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
    print(f"{len(SCHEDULERS) + 1}. Exit")
    print("-" * 50)

def get_int_input(prompt: str, min_val: int = None, max_val: int = None) -> int:
    """Get integer input from user with validation."""
    while True:
        try:
            value = int(input(prompt))
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid integer.")

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
    use_seed = input("Use random seed for reproducibility? (y/n): ").lower() == 'y'
    
    seed = None
    if use_seed:
        seed = get_int_input("Enter seed value: ")
    
    min_burst = get_int_input("Enter minimum burst time: ", 1)
    max_burst = get_int_input("Enter maximum burst time: ", min_burst)
    
    min_priority = get_int_input("Enter minimum priority (smaller value = higher priority): ", 1)
    max_priority = get_int_input("Enter maximum priority: ", min_priority)
    
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
    filename = input("Enter the CSV file path: ")
    
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
    
    filename = input("Enter filename to save processes (CSV): ")
    
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

def run_scheduler(scheduler_type: str, processes: List[Process], params: dict):
    """Run the selected scheduler with given processes and parameters."""
    if not processes:
        print("No processes to schedule.")
        return
    
    # Create a copy of the processes to avoid modifying the original list
    scheduler_class = SCHEDULERS[scheduler_type]["class"]
    scheduler_name = SCHEDULERS[scheduler_type]["name"]
    
    print(f"\nRunning {scheduler_name} scheduler...")
    
    # Create and run the scheduler with appropriate parameters
    if scheduler_type in ["fcfs", "sjf", "priority"]:
        scheduler = scheduler_class(processes)
    else:
        scheduler = scheduler_class(processes, **params)
    
    # Show animation while "processing"
    animation_spinner(1.5)
    
    # Run the scheduler
    completed_processes = scheduler.run()
    
    # Display results
    scheduler.print_results()
    
    # Ask if user wants to see Gantt chart
    if input("\nShow Gantt chart? (y/n): ").lower() == 'y':
        scheduler.print_gantt_chart()
    
    # Ask if user wants to see execution log
    if input("\nShow execution log? (y/n): ").lower() == 'y':
        scheduler.print_execution_log()
    
    # Return to continue
    input("\nPress Enter to continue...")

def main():
    """Main application function."""
    processes = None
    
    while True:
        clear_screen()
        print_header()
        
        if processes:
            print(f"\nCurrent set: {len(processes)} processes loaded")
            if input("View loaded processes? (y/n): ").lower() == 'y':
                display_processes(processes)
        else:
            print("\nNo processes loaded.")
        
        print_menu()
        
        try:
            choice = get_int_input("Enter your choice: ", 1, len(SCHEDULERS) + 1)
            
            # Exit option
            if choice == len(SCHEDULERS) + 1:
                print("\nExiting program. Goodbye!")
                break
            
            # Get the scheduler type from choice
            scheduler_type = list(SCHEDULERS.keys())[choice - 1]
            
            # If no processes are loaded or user wants to change them
            if not processes or input("Use current processes? (y/n): ").lower() != 'y':
                input_choice = process_input_options()
                
                if input_choice == 1:
                    processes = generate_random_processes()
                elif input_choice == 2:
                    processes = enter_processes_manually()
                elif input_choice == 3:
                    new_processes = load_processes_from_file()
                    if new_processes:
                        processes = new_processes
                elif input_choice == 4:
                    continue
                
                if processes and input("Save these processes to file? (y/n): ").lower() == 'y':
                    save_processes_to_file(processes)
            
            if not processes:
                print("No processes available. Please generate or input processes first.")
                input("Press Enter to continue...")
                continue
            
            # Get scheduler-specific parameters
            params = get_scheduler_params(scheduler_type)
            
            # Run the selected scheduler
            run_scheduler(scheduler_type, processes, params)
            
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            input("Press Enter to continue...")
            continue
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            input("Press Enter to continue...")
            continue

if __name__ == "__main__":
    main()