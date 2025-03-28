import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from math import gcd
from functools import reduce

def lcm(numbers):
    return reduce(lambda x, y: (x * y) // gcd(x, y), numbers)

class Task:
    def __init__(self, name, wcet, bcet, priority, deadline, period):
        self.name = name
        self.wcet = wcet   
        self.bcet = bcet   
        self.priority = priority
        self.deadline = deadline
        self.period = period

    def __repr__(self):
        return f"{self.name}(WCET={self.wcet}, BCET={self.bcet}, Priority={self.priority})"

def read_tasks_from_csv(file_path):
    df = pd.read_csv(file_path)
    tasks = []
    for _, row in df.iterrows():
        task = Task(
            name=row['Task'],
            wcet=row['WCET'],
            bcet=row['BCET'],
            priority=row['Priority'],
            deadline=row['Deadline'],
            period=row['Period']
        )
        tasks.append(task)
    tasks.sort(key=lambda x: x.priority)
    return tasks

def response_time_analysis(tasks):
    response_times = {}
    schedulable = True

    for i, task in enumerate(tasks):
        R = task.wcet
        while True:
            interference = sum(
                np.ceil(R / tasks[j].period) * tasks[j].wcet
                for j in range(i)
            )
            R_next = task.wcet + interference

            if R_next > task.deadline:
                response_times[task.name] = R_next
                schedulable = False
                break  
            if R_next == R:
                break

            R = R_next
        if task.name not in response_times:
            response_times[task.name] = R

    return schedulable, response_times



def simple_simulator(tasks, max_time=500):
    time = 0
    execution_history = []
    remaining_time = {task.name: 0 for task in tasks}  
    wcrt = {task.name: 0 for task in tasks}  
    release_times = {task.name: [] for task in tasks}
    start_times = {}

    while time < max_time:
        for task in tasks:
            if time % task.period == 0:
                remaining_time[task.name] = task.wcet
                release_times[task.name].append(time)
                start_times[task.name] = time

        runnable_tasks = [task for task in tasks if remaining_time[task.name] > 0]
        if runnable_tasks:
            next_task = min(runnable_tasks, key=lambda x: x.priority)
            execution_history.append(next_task.name)
            remaining_time[next_task.name] -= 1
            if remaining_time[next_task.name] == 0:
                rt = time - start_times[next_task.name] + 1
                wcrt[next_task.name] = max(wcrt[next_task.name], rt)
        else:
            execution_history.append("Idle")

        time += 1

    return execution_history, wcrt

def plot_gantt_chart(execution_history):
    fig, ax = plt.subplots(figsize=(10, 5))
    tasks = sorted(set(execution_history))
    task_positions = {task: i for i, task in enumerate(tasks)}
    
    for time, task in enumerate(execution_history):
        if task != "Idle":
            ax.broken_barh([(time, 1)], (task_positions[task], 0.8), facecolors='#0eede2')
    
    ax.set_xlabel('Time Units')
    ax.set_ylabel('Tasks')
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels(tasks)
    ax.set_title('Task Scheduling Timeline')
    ax.grid(True)
    plt.show()

def get_hyperperiod(tasks):
    return lcm([task.period for task in tasks])

def get_total_utilization(tasks):
    return round(sum(task.wcet / task.period for task in tasks), 2)

def main(file_path):
    tasks = read_tasks_from_csv(file_path)
    hyperperiod = get_hyperperiod(tasks)
    utilization = get_total_utilization(tasks)
    print("TaskSet:")
    print(f"Hyperperiod = {hyperperiod}")
    print(f"CPU Worst Case Utilization = {utilization:.2f}")
    for task in tasks:
        task_util = round(task.wcet / task.period, 2)
        print(f"Task({task.name}, BCET={task.bcet}, WCET={task.wcet}, Period={task.period}, "
              f"Deadline={task.deadline}, Utilization={task_util:.2f} Core=0, "
              f"Priority={task.priority}, Type=TT, MIT=0, Server=None)")

    is_schedulable, response_times = response_time_analysis(tasks)

    print("\nResponse Time Analysis")
    print("  Scheduling Algorithm: RateMonotonic")
    print(f"  Schedulable: {'True' if is_schedulable else 'False'}")
    print(f"  Hyperperiod: {hyperperiod}")
    print(f"  Utilization: {utilization:.2f}")
    print("  Status: (✓=schedulable, ✗=not schedulable)\n")

    print(f"{'Task':<5} {'WCRT':>6} {'Deadline':>9}  {'Status'}")
    print(f"{'-'*5} {'-'*6} {'-'*9}  {'-'*6}")

    for task in tasks:
        rt = response_times[task.name]
        status = "✓" if rt <= task.deadline else "✗"
        print(f"{task.name:<5} {rt:>6} {task.deadline:>9}  {status}")

    print(f"{'-'*5} {'-'*6} {'-'*9}  {'-'*6}")

    
    print("\n--- Simulation (VSS) Results ---")
    execution_history, wcrt = simple_simulator(tasks, hyperperiod)
    print("Execution History (first 100):", execution_history[:100])
    print("Worst-Case Response Times (WCRT):")
    for task in tasks:
        print(f"{task.name}: {wcrt[task.name]}")
    plot_gantt_chart(execution_history[:1000])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please Provide the path to the Input Task list CSV file")
    else:
        file_path = sys.argv[1]
        main(file_path)
