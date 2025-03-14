import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
    n = len(tasks)
    response_times = [0] * n

    for i in range(n):
        response_times[i] = tasks[i].wcet  
        for j in range(i):
            response_times[i] += np.ceil(response_times[i] / tasks[j].period) * tasks[j].wcet
        if response_times[i] > tasks[i].deadline:
            return False, response_times
    return True, response_times

def simple_simulator(tasks):
    time = 0
    execution_history = []
    remaining_time = {task.name: 0 for task in tasks}  
    wcrt = {task.name: 0 for task in tasks} 
    task_completions = {task.name: 0 for task in tasks}  
    max_time = 50000  
    executed_tasks = set()
    
    while time < max_time:

        for task in tasks:
            if time % task.period == 0:
                remaining_time[task.name] = task.wcet  
                executed_tasks.add(task.name)         

        runnable_tasks = [task for task in tasks if remaining_time[task.name] > 0]
        if runnable_tasks:
            next_task = min(runnable_tasks, key=lambda x: x.priority)
            execution_history.append(next_task.name)
            remaining_time[next_task.name] -= 1
        else:
            execution_history.append("Idle")

        time += 1


        for task in tasks:
            if remaining_time[task.name] == 0 and time > task_completions[task.name]:
                response_time = task_completions[task.name] - (time - task.period)
                wcrt[task.name] = max(wcrt[task.name], response_time)
        
        if time > max([task.period for task in tasks]) * 2:
            break
    
    return execution_history, wcrt

def plot_gantt_chart(execution_history):
    fig, ax = plt.subplots(figsize=(10, 5))
    tasks = sorted(set(execution_history))
    task_positions = {task: i for i, task in enumerate(tasks)}
    
    for time, task in enumerate(execution_history):
        if task != "Idle":
            ax.broken_barh([(time, 1)], (task_positions[task], 0.8), facecolors='tab:blue')
    
    ax.set_xlabel('Time Units')
    ax.set_ylabel('Tasks')
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels(tasks)
    ax.set_title('Task Scheduling Timeline')
    ax.grid(True)
    plt.show()

def main(file_path):
    tasks = read_tasks_from_csv(file_path)
    print("Tasks Loaded:", tasks)
    
    is_schedulable, response_times = response_time_analysis(tasks)
    if is_schedulable:
        print("All tasks are schedulable.")
    else:
        print("Tasks are not schedulable. Response Times:", response_times)

    execution_history, wcrt = simple_simulator(tasks)
    print("Execution History (first 100):", execution_history[:100])  
    print("Worst-Case Response Times (WCRT):", wcrt)
    

    plot_gantt_chart(execution_history[:400])

if __name__ == "__main__":
    main("TC3.csv")