from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Process:
    """
    Represents a process in a CPU scheduling simulation.
    
    Attributes:
        id (int): Unique process identifier.
        burst_time (int): Total CPU time required by the process.
        priority (int): Priority level of the process (lower value means higher priority).
        arrival_time (int): Time when the process enters the ready queue.
        waiting_time (int): Time spent waiting in the ready queue.
        cpu_time_acquired (int): Amount of CPU time the process has received so far.
        turnaround_time (int): Total time from arrival to completion.
        last_running_time (int): The last time the process was running on CPU.
        max_waiting_time (int): Maximum time the process has waited continuously.
        age (int): Age factor for aging mechanisms in scheduling algorithms.
        remaining_time (int): Remaining burst time to complete the process.
        completion_time (Optional[int]): Time when the process completes execution.
        response_time (Optional[int]): Time from arrival to first CPU allocation.
        state (str): Current state of the process (e.g., "READY", "RUNNING").
    """
    id: int
    burst_time: int
    priority: int
    arrival_time: int
    waiting_time: int = field(default=0)
    cpu_time_acquired: int = field(default=0)
    turnaround_time: int = field(default=0)
    last_running_time: int = field(default=0)
    max_waiting_time: int = field(default=0)
    age: int = field(default=0)
    remaining_time: int = field(init=False)
    completion_time: Optional[int] = field(default=None)
    response_time: Optional[int] = field(default=None)
    state: str = field(default="NEW")
    
    def __post_init__(self):
        self.remaining_time = self.burst_time
    
    def __str__(self) -> str:
        """Return a comma-separated string of process attributes."""
        return (f"{self.id},{self.burst_time},{self.priority},{self.arrival_time},"
                f"{self.turnaround_time},{self.cpu_time_acquired},{self.waiting_time}")
    
    def __repr__(self) -> str:
        """Return a detailed representation of the process."""
        return (f"Process(id={self.id}, burst_time={self.burst_time}, priority={self.priority}, "
                f"arrival_time={self.arrival_time}, state={self.state})")

    def display(self) -> str:
        """Return a readable string with process information."""
        return (f"Process {self.id}: burst_time={self.burst_time}, priority={self.priority}, "
                f"arrival_time={self.arrival_time}, waiting_time={self.waiting_time}, "
                f"turnaround_time={self.turnaround_time}, state={self.state}")
    
    def __lt__(self, other) -> bool:
        """
        Compare processes based on priority and ID for sorting.
        Lower priority value means higher scheduling priority.
        """
        if not isinstance(other, Process):
            return NotImplemented
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.id < other.id
    
    def update_waiting_time(self, current_time: int) -> None:
        """
        Update the waiting time of the process.
        
        Args:
            current_time (int): Current simulation time.
        """
        if self.state == "READY":
            wait_period = current_time - self.last_running_time
            self.waiting_time += wait_period
            self.max_waiting_time = max(self.max_waiting_time, wait_period)
    
    def execute(self, time_slice: int) -> int:
        """
        Execute the process for the given time slice.
        
        Args:
            time_slice (int): Amount of CPU time to allocate.
        
        Returns:
            int: Amount of time actually used (may be less than time_slice if process completes).
        """
        if self.remaining_time <= 0:
            return 0
            
        # Track first response if this is the first execution
        if self.cpu_time_acquired == 0 and self.response_time is None:
            # Response time would be calculated from arrival to first execution
            pass
            
        time_used = min(time_slice, self.remaining_time)
        self.cpu_time_acquired += time_used
        self.remaining_time -= time_used
        self.state = "RUNNING"
        
        return time_used
    
    def complete(self, current_time: int) -> None:
        """
        Mark the process as completed and calculate final metrics.
        
        Args:
            current_time (int): Current simulation time.
        """
        self.state = "COMPLETED"
        self.completion_time = current_time
        self.turnaround_time = current_time - self.arrival_time
        self.remaining_time = 0
    
    def is_completed(self) -> bool:
        """Check if the process has completed execution."""
        return self.remaining_time <= 0
    
    def reset_age(self) -> None:
        """Reset the age counter of the process."""
        self.age = 0
    
    def increment_age(self, amount: int = 1) -> None:
        """
        Increment the age of the process.
        
        Args:
            amount (int): Amount to increment the age by. Defaults to 1.
        """
        self.age += amount


    def copy(self):
        """Create a deep copy of the process object."""
        new_process = Process(
            id=self.id,
            burst_time=self.burst_time,
            priority=self.priority,
            arrival_time=self.arrival_time
        )
        
        # Copy other attributes if they exist
        if hasattr(self, 'waiting_time'):
            new_process.waiting_time = self.waiting_time
            
        if hasattr(self, 'turnaround_time'):
            new_process.turnaround_time = self.turnaround_time
            
        if hasattr(self, 'completion_time'):
            new_process.completion_time = self.completion_time
            
        if hasattr(self, 'response_time'):
            new_process.response_time = self.response_time
            
        if hasattr(self, 'remaining_time'):
            new_process.remaining_time = self.remaining_time
            
        return new_process