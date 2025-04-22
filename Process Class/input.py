from process import Process
import random
import csv
import argparse
from typing import List, Optional, Tuple

class ProcessGenerator:
    """Utility class for generating and reading process data."""
    
    @staticmethod
    def generate_random_processes(
        num_processes: int,
        min_burst: int = 1,
        max_burst: int = 20,
        min_priority: int = 1, 
        max_priority: int = 10,
        min_arrival: int = 0,
        max_arrival: int = 100,
        arrival_pattern: str = "random"
    ) -> List[Process]:
        """
        Generate random processes with specified parameters.
        
        Args:
            num_processes: Number of processes to generate
            min_burst: Minimum burst time
            max_burst: Maximum burst time
            min_priority: Minimum priority value
            max_priority: Maximum priority value
            min_arrival: Minimum arrival time
            max_arrival: Maximum arrival time
            arrival_pattern: Pattern for arrival times ("random", "uniform", "burst", "grouped")
                - "random": Completely random arrival times
                - "uniform": Evenly distributed arrival times
                - "burst": Several processes arrive at once, then a gap
                - "grouped": Processes arrive in groups with similar priorities
        
        Returns:
            List of Process objects with random attributes within specified ranges
        """
        processes = []
        
        # Generate arrival times based on pattern
        arrival_times = []
        
        if arrival_pattern == "uniform":
            # Uniformly distributed arrivals
            if num_processes > 1:
                step = (max_arrival - min_arrival) / (num_processes - 1)
                arrival_times = [min_arrival + int(i * step) for i in range(num_processes)]
            else:
                arrival_times = [min_arrival]
        
        elif arrival_pattern == "burst":
            # Burst pattern: groups of processes arrive at the same time
            burst_points = [random.randint(min_arrival, max_arrival) for _ in range(num_processes // 3 + 1)]
            burst_points.sort()
            
            # Assign processes to burst points
            arrival_times = []
            for i in range(num_processes):
                burst_index = random.randint(0, len(burst_points) - 1)
                arrival_times.append(burst_points[burst_index])
        
        elif arrival_pattern == "grouped":
            # Processes with similar priorities arrive close together
            groups = {}
            for i in range(min_priority, max_priority + 1):
                groups[i] = random.randint(min_arrival, max_arrival)
            
            arrival_times = []
            for i in range(num_processes):
                priority = random.randint(min_priority, max_priority)
                base_arrival = groups[priority]
                # Processes with the same priority arrive within a small window
                arrival_times.append(base_arrival + random.randint(-5, 5))
                
                # Ensure arrival time is within bounds
                arrival_times[-1] = max(min_arrival, min(max_arrival, arrival_times[-1]))
        
        else:  # Default: random
            arrival_times = [random.randint(min_arrival, max_arrival) for _ in range(num_processes)]
        
        # Generate processes with random or pre-defined arrival times
        for i in range(num_processes):
            process_id = i + 1
            burst_time = random.randint(min_burst, max_burst)
            priority = random.randint(min_priority, max_priority)
            
            # Use the pre-generated arrival time if available, otherwise random
            if i < len(arrival_times):
                arrival_time = arrival_times[i]
            else:
                arrival_time = random.randint(min_arrival, max_arrival)
                
            process = Process(
                id=process_id,
                burst_time=burst_time,
                priority=priority,
                arrival_time=arrival_time
            )
            processes.append(process)
        
        return processes
    
    @staticmethod
    def save_processes_to_file(processes: List[Process], filename: str) -> None:
        """
        Save processes to a CSV file.
        
        Args:
            processes: List of Process objects to save
            filename: Name of the file to save to
        """
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(["id", "burst_time", "priority", "arrival_time"])
            
            # Write process data
            for process in processes:
                writer.writerow([process.id, process.burst_time, process.priority, process.arrival_time])
    
    @staticmethod
    def load_processes_from_file(filename: str) -> List[Process]:
        """
        Load processes from a CSV file.
        
        Args:
            filename: Name of the file to load from
            
        Returns:
            List of Process objects loaded from the file
        """
        processes = []
        
        try:
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                
                # Skip header
                next(reader, None)
                
                for row in reader:
                    if len(row) >= 4:  # Ensure we have all required fields
                        try:
                            process_id = int(row[0])
                            burst_time = int(row[1])
                            priority = int(row[2])
                            arrival_time = int(row[3])
                            
                            process = Process(
                                id=process_id,
                                burst_time=burst_time,
                                priority=priority,
                                arrival_time=arrival_time
                            )
                            processes.append(process)
                        except ValueError as e:
                            print(f"Error parsing row {row}: {e}")
                    else:
                        print(f"Skipping invalid row: {row}")
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except Exception as e:
            print(f"Error loading processes from file: {e}")
            
        return processes


def display_processes(processes: List[Process]) -> None:
    """Display a table of processes."""
    print("\n{:<5} {:<10} {:<10} {:<12}".format("ID", "Burst Time", "Priority", "Arrival Time"))
    print("-" * 40)
    for p in processes:
        print("{:<5} {:<10} {:<10} {:<12}".format(p.id, p.burst_time, p.priority, p.arrival_time))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate or load process data for CPU scheduling simulation")
    
    # Command-line arguments
    parser.add_argument("--generate", action="store_true", help="Generate random processes")
    parser.add_argument("--num", type=int, default=10, help="Number of processes to generate")
    parser.add_argument("--min-burst", type=int, default=1, help="Minimum burst time")
    parser.add_argument("--max-burst", type=int, default=20, help="Maximum burst time")
    parser.add_argument("--min-priority", type=int, default=1, help="Minimum priority")
    parser.add_argument("--max-priority", type=int, default=10, help="Maximum priority")
    parser.add_argument("--min-arrival", type=int, default=0, help="Minimum arrival time")
    parser.add_argument("--max-arrival", type=int, default=50, help="Maximum arrival time")
    parser.add_argument("--pattern", choices=["random", "uniform", "burst", "grouped"], 
                        default="random", help="Arrival time pattern")
    parser.add_argument("--save", type=str, help="Save generated processes to file")
    parser.add_argument("--load", type=str, help="Load processes from file")
    
    args = parser.parse_args()
    
    processes = []
    
    # Generate random processes
    if args.generate:
        processes = ProcessGenerator.generate_random_processes(
            num_processes=args.num,
            min_burst=args.min_burst,
            max_burst=args.max_burst,
            min_priority=args.min_priority,
            max_priority=args.max_priority,
            min_arrival=args.min_arrival,
            max_arrival=args.max_arrival,
            arrival_pattern=args.pattern
        )
        print(f"Generated {len(processes)} random processes with {args.pattern} arrival pattern.")
        
        # Display processes
        display_processes(processes)
        
        # Save to file if specified
        if args.save:
            ProcessGenerator.save_processes_to_file(processes, args.save)
            print(f"Saved processes to {args.save}")
    
    # Load processes from file
    elif args.load:
        processes = ProcessGenerator.load_processes_from_file(args.load)
        print(f"Loaded {len(processes)} processes from {args.load}")
        
        # Display processes
        display_processes(processes)
    
    # Example usage if no arguments provided
    else:
        print("No command specified. Running example usage:")
        
        # Example 1: Generate 5 random processes
        print("\nExample 1: Generating 5 random processes")
        random_processes = ProcessGenerator.generate_random_processes(
            num_processes=5,
            min_burst=2,
            max_burst=15,
            min_priority=1,
            max_priority=5,
            min_arrival=0,
            max_arrival=20
        )
        display_processes(random_processes)
        
        # Example 2: Generate processes with burst arrival pattern
        print("\nExample 2: Generating processes with 'burst' arrival pattern")
        burst_processes = ProcessGenerator.generate_random_processes(
            num_processes=8,
            arrival_pattern="burst"
        )
        display_processes(burst_processes)
        
        # Example 3: Save to file and load back
        print("\nExample 3: Saving processes to file and loading them back")
        temp_filename = "temp_processes.csv"
        ProcessGenerator.save_processes_to_file(burst_processes, temp_filename)
        print(f"Saved processes to {temp_filename}")
        
        loaded_processes = ProcessGenerator.load_processes_from_file(temp_filename)
        print(f"Loaded {len(loaded_processes)} processes from {temp_filename}")
        display_processes(loaded_processes)
        
        print("\nTo use command-line options, try:")
        print("  python process_generator.py --generate --num=10 --pattern=uniform --save=processes.csv")
        print("  python process_generator.py --load=processes.csv")