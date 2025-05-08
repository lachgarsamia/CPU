# cpu_scheduler_gui.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import os
from ProcessClass.process import Process
from schedulers.FCFS import FCFSScheduler
from schedulers.SJF import SJFScheduler
from schedulers.PrioritySchedule import PriorityScheduler
from schedulers.RR import RoundRobinScheduler
from schedulers.RR_Priority import PriorityRoundRobinScheduler

SCHEDULERS = {
    "FCFS": {"class": FCFSScheduler, "params": []},
    "SJF": {"class": SJFScheduler, "params": []},
    "Priority": {"class": PriorityScheduler, "params": []},
    "Round Robin": {"class": RoundRobinScheduler, "params": ["time_quantum"]},
    "RR with Priority": {"class": PriorityRoundRobinScheduler, "params": ["time_quantum", "aging_factor"]},
}

class CPUSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduler Simulator")

        self.processes = []

        self.scheduler_var = tk.StringVar(value="FCFS")
        self.time_quantum_var = tk.StringVar()
        self.aging_factor_var = tk.StringVar()

        self.build_gui()

    def build_gui(self):
        control_frame = ttk.Frame(self.root)
        control_frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(control_frame, text="Scheduler:").pack(side='left')
        scheduler_menu = ttk.Combobox(control_frame, textvariable=self.scheduler_var, values=list(SCHEDULERS.keys()), state="readonly")
        scheduler_menu.pack(side='left', padx=5)
        scheduler_menu.bind("<<ComboboxSelected>>", self.update_param_fields)

        self.time_quantum_entry = ttk.Entry(control_frame, textvariable=self.time_quantum_var)
        self.aging_factor_entry = ttk.Entry(control_frame, textvariable=self.aging_factor_var)
        ttk.Label(control_frame, text="Quantum:").pack(side='left', padx=5)
        self.time_quantum_entry.pack(side='left', padx=2)
        ttk.Label(control_frame, text="Aging:").pack(side='left', padx=5)
        self.aging_factor_entry.pack(side='left', padx=2)

        ttk.Button(control_frame, text="Load CSV", command=self.load_csv).pack(side='right')
        ttk.Button(control_frame, text="Run", command=self.run_scheduler).pack(side='right', padx=5)

        self.tree = ttk.Treeview(self.root, columns=("ID", "Arrival", "Burst", "Priority", "Waiting", "Turnaround", "Completion"), show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(padx=10, pady=5, fill='x')

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def update_param_fields(self, event=None):
        scheduler = self.scheduler_var.get()
        self.time_quantum_entry.configure(state='normal' if "time_quantum" in SCHEDULERS[scheduler]["params"] else 'disabled')
        self.aging_factor_entry.configure(state='normal' if "aging_factor" in SCHEDULERS[scheduler]["params"] else 'disabled')

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not path: return
        try:
            self.processes = []
            with open(path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.processes.append(Process(
                        id=int(row['id']),
                        burst_time=int(row['burst_time']),
                        priority=int(row['priority']),
                        arrival_time=int(row['arrival_time'])
                    ))
            messagebox.showinfo("Loaded", f"Loaded {len(self.processes)} processes from {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {e}")

    def run_scheduler(self):
        if not self.processes:
            messagebox.showerror("No Data", "Please load processes first.")
            return

        scheduler_name = self.scheduler_var.get()
        SchedulerClass = SCHEDULERS[scheduler_name]['class']
        kwargs = {}

        if 'time_quantum' in SCHEDULERS[scheduler_name]['params']:
            try:
                kwargs['time_quantum'] = int(self.time_quantum_var.get())
            except ValueError:
                messagebox.showerror("Invalid Input", "Time Quantum must be an integer")
                return

        if 'aging_factor' in SCHEDULERS[scheduler_name]['params']:
            try:
                kwargs['aging_factor'] = int(self.aging_factor_var.get())
            except ValueError:
                messagebox.showerror("Invalid Input", "Aging Factor must be an integer")
                return

        scheduler = SchedulerClass(self.processes.copy(), **kwargs)
        completed = scheduler.run()

        for row in self.tree.get_children():
            self.tree.delete(row)
        for p in completed:
            self.tree.insert('', 'end', values=(p.id, p.arrival_time, p.burst_time, p.priority, p.waiting_time, p.turnaround_time, p.completion_time))

        self.ax.clear()
        for p in completed:
            start = p.completion_time - p.burst_time
            self.ax.barh(f"P{p.id}", p.burst_time, left=start)
        self.ax.set_xlabel("Time")
        self.ax.set_title(f"Gantt Chart - {scheduler_name}")
        self.canvas.draw()

if __name__ == '__main__':
    root = tk.Tk()
    app = CPUSchedulerGUI(root)
    root.mainloop()