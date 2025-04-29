# CPU Scheduling Alorithms

### This part of the project hosts the implemetation of the various *CPU Scheduling Algorithms* commonly used within Operating Systems to manage the execution of processes. 
### Each algorithm determines the order in which the processes access the CPU for execution. The following algorithms are implemented:

1. First Come First Serve    -- FCFS.py
2. Shortest Job First        -- SJF.py
3. Priority Scheduling       -- PrioritySchedule.py
4. Round RObin               -- RR.py
5. Round Robin with Priority -- RR_Priority.py 

### Each of these algorithms is designed to solve process scheduling in different ways, depending on which process to choose first

---

## 1. First-Come, First-Serve (FCFS)
### Definition:
*FCFS* is the simplest scheduling algorithm. In FCFS processes are executed in the order of arrival at the ready queue: 

- Arrival Time is the only factor in scheduling
- The CPU is allocated to processes in the order of arrival
- The run of processes is *Non-Preemptive*

---

## 2. Shortest Job First (SJF)
### Definition:
*SJF* is a *Non-preemptive* scheduling algorithm that selects the process with the shortest burst time to execute next. The main idea is that the shortest processes should be executed first in order to minimize the overall waiting-time.

- Burst-time is the key factor in scheduling.
- If two processes have the same burst-time, we use *FCFS* to decide next

---

## 3. Priority Scheduling
### Definition:
*Priority Scheduling* assigns priority value to each process. The CPU is allocated to the process with the highest priority (lowest value). This could be done either preemptevely or non-preemtively, but in our case we chose to work *Non-Preeptive*

- The process with the highest priority (lowest numerical value of priority) is executed first
- If two processes have the same priority, we decide using *FCFS*

---

## 4. Round Robin (RR)
### Definition
*Round Robin* is a preemptive scheduling algorithm thet allows a fixed execution time for each process, called *quantum*, in a circular way.

- Each process is given a quantum 
- If a process does not complete within its quantum, it is preepted and placed at the end of the queue
- The scheduler picks the next process in line after the process before it is preempted

---

## 5. Round Robin with Priority
### Defintion
*RR with Priority* combines properties of both *Round Robin* with *Priority Scheduling*. This algorithm allocates CPU time in a RR manner, but each process has a priority value, thus when a higher priority process arrives while another one is executing, the current process xcan be preempted.

- *Time quantum* used, but the *priority* of the process is also used
- If two processes are ready to run at the same time, the one with the higher priority is given the CPU first
- Execution is done in a round robin fashion, but the order could be interrupted by a higher priority process arriving in the ready queue