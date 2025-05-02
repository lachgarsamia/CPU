from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from schedulers.FCFS import FCFSScheduler
from schedulers.SJF import SJFScheduler
from schedulers.PrioritySchedule import PriorityScheduler
from schedulers.RR import RoundRobinScheduler
from schedulers.RR_Priority import PriorityRoundRobinScheduler
from ProcessClass.process import Process
from system.system import System
import os

app = Flask(__name__)
app.secret_key = 'secret_key'

SCHEDULER_MAP = {
    "FCFS": FCFSScheduler,
    "SJF": SJFScheduler,
    "Priority": PriorityScheduler,
    "Priority Scheduling": PriorityScheduler,
    "Round Robin": RoundRobinScheduler,
    "Priority Round Robin": PriorityRoundRobinScheduler,
}



def reset_page():
    for file_name in ["execution.csv", "process_table.csv", "result.csv", "SpecialFile.csv", "system.txt"]:
        with open(f"static/csv/{file_name}", "w") as f:
            f.truncate(0)

syst = None
algo = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global syst, algo
    if request.method == 'POST':
        action = request.form['action']
        if action == "randomProcesses":
            number_processes = int(request.form['numberProcesses'])
            max_burst = int(request.form['maxBurst'])
            min_burst = int(request.form['minBurst'])
            max_arrival_time = int(request.form['maxArrivalTime'])

            algo = request.form["dropdown"]
            print("Selected algorithm:", algo)

            processes = System.generate_processes("static/csv/process_table.csv", number_processes, max_burst,
                                                  min_burst, max_arrival_time)
            scheduler = None

            if algo in ["FCFS", "SJF", "Priority", "Priority Scheduling"]:
                scheduler = SCHEDULER_MAP[algo](processes)

            elif algo == "Round Robin":
                quantum = int(request.form.get("quantum", 1))  # ✅ FIX
                scheduler = SCHEDULER_MAP[algo](processes, time_quantum=quantum)

            elif algo == "Priority Round Robin":
                quantum = int(request.form.get("quantum", 1))  # ✅ FIX
                aging = int(request.form.get("aging", 1))      # ✅ FIX
                scheduler = SCHEDULER_MAP[algo](processes, time_quantum=quantum, aging_factor=aging)

            if scheduler:
                completed_processes = scheduler.run()
            else:
                return jsonify({'error': 'Invalid Scheduler selected'}), 400

            syst = System(processes)
            syst.save_processes_csv("static/csv/result.csv", completed_processes)
            syst.system_to_csv("static/csv/system.txt")
            with open("static/csv/system.txt", "a") as f:
                f.write("," + algo)

            session["total"] = len(completed_processes)
            return render_template('index.html', total=len(completed_processes))
    return render_template('index.html')


@app.route('/save_csv', methods=['POST'])
def save_csv():
    try:
        data = request.get_json()
        csvData = data['csvData']

        with open('static/csv/process_table.csv', 'w') as file:
            file.write(csvData)

        processes = System.load_from_csv('static/csv/process_table.csv')
        with open("static/csv/system.txt", "r") as file:
            lines = file.readlines()[0].split(",")
            algo = lines[-1].strip()

        syst = System.load_system_txt("static/csv/system.txt", processes)

        if algo in ["FCFS", "SJF", "Priority"]:
            scheduler = SCHEDULER_MAP[algo](processes)
        else:
            scheduler = SCHEDULER_MAP[algo](processes, time_quantum=syst.quantum, aging_factor=syst.context_switching)

        completed_processes = scheduler.run()
        syst.save_processes_csv("static/csv/result.csv", completed_processes)
        session["total"] = len(completed_processes)

        return redirect(url_for("index"))

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/reset', methods=['GET'])
def reset():
    reset_page()
    return render_template("reset.html")


if __name__ == '__main__':
    app.run(debug=True, port=8080)