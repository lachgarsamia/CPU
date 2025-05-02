# Process Scheduling Simulator

A Python-based process scheduling simulator supporting multiple scheduling algorithms: 
- FCFS, 
- SJF, 
- Priority Scheduling, 
- Round Robin, 
- Priority + Round Robin.

This repository provides two ways to interact with the simulator:

* **`main.py`**: A terminal-based CLI version.
* **`app.py`**: A Flask-powered web application with a UI for interactive visualization.

---

## Project Structure

```
.
├── main.py             # Terminal-based interface
├── app.py              # Flask web app (UI-based)
├── static/             # Static files (CSS, JS, images)
│   ├── css/            # CSS Styling
|       └── style.css
│   ├── csv/            # CSV related to the plots and informations in the UI
│       ├── execution.csv
│       ├── process_table.csv
│       ├── result.csv
│       ├── SpecialFile.csv
│       └── system.txt
│   ├── img             # Images that show how both aproaches run
│       ├── Main        # Terminal images
│       └── App         # UI images
│   └── js/             # JavaScript code related to the functionalities of UI
│       ├── csvTable.js
│       ├── inputSection.js
│       ├── piechart.js
│       └── timeline.js
├── templates/          # HTML templates for Flask UI
│   ├── index.html
│   └── reset.html
├── system/             # Helper functions of UI
│   ├── system.py
├── schedulers/          # Contains algorithm implementations
│   ├── FCFS.py
│   ├── SJF.py
│   ├── PrioritySchedule.py
│   ├── RR.py
│   ├── RR_Priority.py
│   └── README.md
├── ProcessClass/       # Process implementation
│   ├── process.py/
│   └── input.py/
├── utils/              # Helper modules (e.g., Gantt chart plotting)
│   └── file_io.py
├── test_processes.csv  # Test processes
├── testing.ipynb       # Notebook with run examples, and edge case testing (algorithms with some edge cases that test the robustness of the code)         
└── README.md           # This file
```

---

## Features

* Simulates common CPU scheduling algorithms:

  * First-Come, First-Served (FCFS)
  * Shortest Job First (SJF)
  * Priority Scheduling
  * Round Robin (RR)
  * Priority + Round Robin (Hybrid)
* Gantt chart visualization of process execution
* Support for:
  * Manual process input
  * Random process generation
  * CSV upload (terminal-based only)
  * Session-based state tracking

---

##  Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/MTheCreator/OS-Assign-1-CC
cd OS-Assign-1-CC
```

### 2. Install Dependencies

It's recommended to use a virtual environment.

```bash
conda env create -f environment.yml

conda activate OS-ASSIGN_1
```

---

##  Run the Terminal Version

```bash
python main.py
```

Follow the prompts to choose an algorithm and enter process data via the command line.

---

##  Run the Web App (UI)

```bash
python app.py
```

The app will run on [http://127.0.0.1:8080](http://127.0.0.1:8080). Open it in your browser to start simulating!

---

## 📊 Sample Visual Output

* Gantt charts are automatically generated to represent the execution order of processes.
* Charts are saved/exported for reports or assignments.

---

## 📌 Notes

* The web app uses Flask sessions for temporary storage and `Matplotlib` for visualization.
* The scheduler logic is decoupled for reuse in both the CLI and UI.
* This tool is ideal for Operating Systems coursework or scheduling research.

* To test the `main.py` with a `csv` entry, we kept an example of processes in `test_processes.csv`, else you can just run the code and generate / enter manually the processes and then save them in a `csv` for later use. You can also save all outputs (log of scheduling, gant charts, …)

---
## About:
This project comes in the context of an assignment for the class of Operating Systems @UM6P - College of Computing, where we get our hands on exercise of implementing the most famous scheduling algorithms in order to see first-hand how they work, far from the theory.

Project done by:
- Mounia BADDOU (github: @MTheCreator): Mounia.BADDOU@um6p.ma
- Samia LACHGAR (github: @lachgarsamia): Samia.LACHGAR@um6p.ma
- Supervised by: Prof. Youssef IRAQI, UM6P-CC

Academic Year: 2024 / 2025, Mohammed VI Polytechnic University, College of Computing.