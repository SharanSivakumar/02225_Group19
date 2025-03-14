import pandas as pd
import numpy as np

class Task:
    def __init__(self, name, wcet, bcet, priority, deadline, period):
        self.name = name
        self.wcet = wcet   # Worst-case execution time
        self.bcet = bcet   # Best-case execution time
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
    # Sort tasks by priority (lower number means higher priority)
    tasks.sort(key=lambda x: x.priority)
    return tasks

def response_time_analysis(tasks):
    n = len(tasks)
    response_times = [0] * n

    for i in range(n):
        response_times[i] = tasks[i].wcet  # Initial response time is WCET
        for j in range(i):
            response_times[i] += np.ceil(response_times[i] / tasks[j].period) * tasks[j].wcet
        if response_times[i] > tasks[i].deadline:
            return False, response_times
    return True, response_times

def simple_simulator(tasks, simulation_time):
    time = 0
    execution_history = []
    remaining_time = {task.name: task.wcet for task in tasks}
    wcrt = {task.name: 0 for task in tasks}  # Dictionary to keep track of worst-case response times
    task_completions = {task.name: 0 for task in tasks}  # Task completion time tracking

    while time < simulation_time:
        # Determine the highest priority task that is ready to run
        runnable_tasks = [task for task in tasks if time % task.period == 0 or remaining_time[task.name] < task.wcet]
        if runnable_tasks:
            # Select the highest priority task
            next_task = min(runnable_tasks, key=lambda x: x.priority)
            if remaining_time[next_task.name] > 0:
                execution_history.append(next_task.name)
                remaining_time[next_task.name] -= 1
            else:
                execution_history.append("Idle")
        else:
            execution_history.append("Idle")

        # Increment time
        time += 1

        # Reset remaining time for periodic tasks at each period boundary
        for task in tasks:
            if time % task.period == 0:
                # Log completion time for WCRT calculation
                task_completions[task.name] = time  # Update completion time
                remaining_time[task.name] = task.wcet  # Reset remaining time for periodic tasks

        # Condition to calculate WCRT
        for task in tasks:
            if remaining_time[task.name] == 0 and time > task_completions[task.name]:
                response_time = task_completions[task.name] - (time - task.period)
                # Update the worst-case response time
                wcrt[task.name] = max(wcrt[task.name], response_time)

    return execution_history, wcrt

def main(file_path, simulation_time=20):
    tasks = read_tasks_from_csv(file_path)
    print("Tasks Loaded:", tasks)
    
    is_schedulable, response_times = response_time_analysis(tasks)
    if is_schedulable:
        print("All tasks are schedulable.")
    else:
        print("Tasks are not schedulable. Response Times:", response_times)

    execution_history, wcrt = simple_simulator(tasks, simulation_time)
    print("Execution History:", execution_history)
    print("Worst-Case Response Times (WCRT):", wcrt)

if __name__ == "__main__":
    main(r"C:\Users\shara\Downloads\exercise-TC3 - Copy.csv", simulation_time=20)