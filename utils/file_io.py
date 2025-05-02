# utils/file_io.py
import csv

def write_execution_csv(gantt_chart, filepath="static/csv/execution.csv"):
    with open(filepath, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'start', 'end'])
        writer.writeheader()
        for entry in gantt_chart:
            proc_id, start, end = entry  
            if proc_id == "IDLE":
                continue
            writer.writerow({
                'id': proc_id,
                'start': start,
                'end': end
            })
