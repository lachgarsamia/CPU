# Process Class Implementation

### The following module defines the `Process` class that models the behavior and characteristics of a process.
### It tracks essential properties like *burst time*, *priority*, *waiting time* and *state transitions* during the execution of processes.
### This class is implemented using Python's `dataclass` for simplicity.

---

## Attributes
#### Each `Process` object has the following attributes:
- `id: int`             -- Unique id for the process
- `burst_time: int`     -- Total CPU time needed to complete the process
- `priority: int`       -- Scheduling priority (lower val == higher priority)
- `arrival_time: int`   -- Time when the process arrives in the queue
- `waiting_time: int`   -- Total waiting time of the process
- `cpu_time_acquired: int`: -- Total CPU time the process has been given
- `turnaround_time: int`: -- Time between arrival and completion
- `last_running_time: int`: -- Last time the process was active
- `max_waiting_time: int`: -- Maximum waiting time between executions
- `age: int`            -- Aging counter for the process
- `remaining_time: int`: -- CPU time remaining for the process to end
- `completion_time: Optional[int]`: -- Time when the process finishes it's execution
- `response_time: Optional[int]`: -- Time from arrival to first CPU use
- `state: str`:          -- Current state of the process


## Key Methods:
### Special methods related to `@dataclass`:
- `__post_init__(self)`
   Initialize `remaining_time` to `burst_time` since the process didn't get any CPU time
- `__str__(self) -> str`
   Returns a brief, csv like string of core attributes
- `__repr__(self) -> str`
   Returns a detailed readable string showing key informations of the process (used mainly for error debugging)
- `__lt__(self, other) -> bool`
   Defines an order between processes, in our case the proceses are ordered first by priority, and if priorities are equal, we move to id (or arrival)

### Behavior Methods:
- `display(self) -> str`
   Returns a readdabel summary of the process' main characteristics
- `update_waiting_time(self, current_time: int) -> None`
   Updates the process' total waiting time based on the current simulation's time
- `execute(self, time_slice: int) -> int`
   Simulates the execution / running of the process for a given time slice and updates execution variables, returns by the end the time used
- `is_completed(self) -> bool`
   Checks if the process has finished it's execution

### Aging related Methods
- `reset_age(self) -> None`
   Resets the age counter to 0
- `increment_age(self, amount: int = 1) -> None`
   Increases the age counter by a sett ammount


---

### Note :
##### In this directory, we also have a *.py* file called `input.py` where we present some test cases to ensure that the `Process` class works perfectly. 
