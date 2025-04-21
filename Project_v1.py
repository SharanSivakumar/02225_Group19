import csv
from math import gcd, ceil, floor
from functools import reduce
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np

class Task:
    def __init__(self, name, wcet, bcet, deadline, period, priority):
        self.name = name
        self.wcet = wcet
        self.bcet = bcet
        self.deadline = deadline
        self.period = period
        self.priority = priority

    def utilization(self):
        return self.wcet / self.period

    def __repr__(self):
        return f"Task({self.name}, WCET={self.wcet}, Period={self.period}, Deadline={self.deadline}, Priority={self.priority})"


class Component:
    def __init__(self, name, core_name, scheduling, bdr_params):
        self.name = name
        self.core_name = core_name
        self.scheduling = scheduling  
        self.bdr_alpha = bdr_params.get("alpha", 1.0)
        self.bdr_delta = bdr_params.get("delta", 0)
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def __repr__(self):
        return f"Component({self.name}, Core={self.core_name}, Scheduling={self.scheduling}, Tasks={len(self.tasks)})"


class Core:
    def __init__(self, name, speed):
        self.name = name
        self.speed = speed
        self.components = []

    def add_component(self, component):
        self.components.append(component)

    def __repr__(self):
        return f"Core({self.name}, Speed={self.speed}, Components={len(self.components)})"


def load_system_model_from_csv(task_file, arch_file, budget_file):
    cores = {}
    with open(arch_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            core_id = row["core_id"]
            speed = float(row["speed_factor"])
            cores[core_id] = Core(core_id, speed)

    components = {}
    with open(budget_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            comp_id = row["component_id"]
            core_id = row["core_id"]
            scheduler = row["scheduler"]
            budget = float(row["budget"])
            period = float(row["period"])
            alpha = budget / period
            delta = 0  #DELTA VALUES HAVE TO BE Checked Important! We should do this before the final version is decided!
            comp = Component(comp_id, core_id, scheduler, {"alpha": alpha, "delta": delta})
            components[comp_id] = comp
            cores[core_id].add_component(comp)
    tasks = {}
    with open(task_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            task_name = row["task_name"]
            wcet = float(row["wcet"])
            bcet = float(row["bcet"]) if "bcet" in row and row["bcet"] else wcet
            deadline = float(row["deadline"]) if "deadline" in row and row["deadline"] else float(row["period"])
            period = float(row["period"])
            priority = int(row["priority"]) if row["priority"] else 0
            comp_id = row["component_id"]

            task = Task(task_name, wcet, bcet, deadline, period, priority)
            tasks[task_name] = task
            components[comp_id].add_task(task)

    return {
        "cores": cores,
        "components": components,
        "tasks": tasks
    }

def export_solution_csv(system, response_times, filename=".\Output\solution.csv"):
    task_results = []
    
    for task in system["tasks"].values():
        rts = response_times.get(task.name, [])
        avg_rt = round(sum(rts)/len(rts), 2) if rts else 0.0
        max_rt = round(max(rts), 2) if rts else 0.0
        schedulable = 1 if rts and max_rt <= task.deadline else 0
        comp_id = next(comp.name for comp in system["components"].values() if task in comp.tasks)

        task_results.append({
            "task_name": task.name,
            "component_id": comp_id,
            "task_schedulable": schedulable,
            "avg_response_time": avg_rt,
            "max_response_time": max_rt
        })

    component_schedulable = {}
    for comp in system["components"].values():
        comp_tasks = [res for res in task_results if res["component_id"] == comp.name]
        all_schedulable = all(t["task_schedulable"] == 1 for t in comp_tasks)
        component_schedulable[comp.name] = 1 if all_schedulable else 0

    with open(filename, mode='w', newline='') as csvfile:
        fieldnames = [
            "task_name", "component_id", "task_schedulable",
            "avg_response_time", "max_response_time", "component_schedulable"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in task_results:
            row["component_schedulable"] = component_schedulable[row["component_id"]]
            writer.writerow(row)

    print(f"\n Exported results to '{filename}'")

def lcm(numbers):
    return reduce(lambda x, y: (x * y) // gcd(int(x), int(y)), numbers)

def half_half_transform(alpha, delta):
    P = max(1, ceil(delta / alpha))  
    Csupply = ceil(alpha * P / 2)
    Tsupply = floor(P / 2)
    return Csupply, Tsupply

def run_simulation(system, max_time=None):
    cores = system["cores"]
    all_periods = [task.period for task in system["tasks"].values()]
    sim_time = int(lcm(all_periods)) if max_time is None else int(max_time)
    print(f"Simulating up to time = {sim_time} units")

    execution_log = []
    response_times = defaultdict(list)
    released_tasks = defaultdict(list)
    task_state = {}

    for time in range(sim_time):
        tick_log = {}

        for core in cores.values():
            core_speed = core.speed
            active_candidates = []
            for comp in core.components:
                if time < comp.bdr_delta:
                    continue

                for task in comp.tasks:
                    if time % task.period == 0:
                        released_tasks[task.name].append(time)
                        task_state[task.name] = {"remaining": task.wcet, "start": None}
                        
                    if task.name in task_state and task_state[task.name]["remaining"] > 0:
                        active_candidates.append((task, comp))

            if not active_candidates:
                tick_log[core.name] = "Idle"
                continue

            if core.components[0].scheduling == "FPS":
                active_candidates.sort(key=lambda x: x[0].priority)
            elif core.components[0].scheduling == "EDF":
                active_candidates.sort(key=lambda x: time + x[0].deadline - (time % x[0].period))

            selected_task, selected_comp = active_candidates[0]
            task_state[selected_task.name]["remaining"] -= core_speed
            if task_state[selected_task.name]["start"] is None:
                task_state[selected_task.name]["start"] = time

            tick_log[core.name] = selected_task.name

            if task_state[selected_task.name]["remaining"] <= 0:
                release = released_tasks[selected_task.name].pop(0)
                rt = time - release + 1
                response_times[selected_task.name].append(rt)
                del task_state[selected_task.name]

        execution_log.append(tick_log)

    print("\n--- SIMULATION RESULTS ---")
    for task in system["tasks"].values():
        rts = response_times[task.name]
        if rts:
            print(f"{task.name}: Avg RT = {sum(rts)/len(rts):.2f}, Max RT = {max(rts)}")
        else:
            print(f"{task.name}: Not executed")

    print("\n--- WORST-CASE RESPONSE TIMES (WCRT) ---")
    for task in system["tasks"].values():
        rts = response_times[task.name]
        if rts:
            wcrt = max(rts)
            print(f"{task.name}: WCRT = {wcrt}  |  Deadline = {task.deadline}  =>  {'✓' if wcrt <= task.deadline else '✗'}")
        else:
            print(f"{task.name}: No RT recorded")

    print("\n--- RESOURCE UTILIZATION PER COMPONENT ---")
    total_sim_time = sim_time
    for core in cores.values():
        for comp in core.components:
            comp_exec_time = sum(
                1 for tick in execution_log for cname, tname in tick.items() 
                if cname == core.name and any(t.name == tname for t in comp.tasks)
            )
            utilization = comp_exec_time / total_sim_time
            print(f"Component {comp.name} on {core.name}: Utilization = {utilization:.2f}")

    return execution_log, response_times


def dbf_edf(tasks, t):
    return sum(floor((t + task.period - task.deadline) / task.period) * task.wcet for task in tasks)

def dbf_fps(tasks, t, current_task):
    hp_tasks = [τ for τ in tasks if τ.priority < current_task.priority]
    return sum(ceil(t / τ.period) * τ.wcet for τ in hp_tasks) + current_task.wcet

def sbf_bdr(alpha, delta, t):
    return max(0, alpha * (t - delta))

def find_min_bdr_params(tasks, scheduling, max_time=100):
    for delta in range(0, max_time + 1):
        for alpha in np.linspace(0.1, 1.0, 100):
            ok = True
            for t in range(1, max_time + 1):
                if scheduling == "EDF":
                    dbf = dbf_edf(tasks, t)
                else:
                    dbf = max(dbf_fps(tasks, t, τ) for τ in tasks)
                sbf = sbf_bdr(alpha, delta, t)
                if sbf < dbf:
                    ok = False
                    break
            if ok:
                return round(alpha, 3), delta
    return None, None

def run_analysis(system):
    print("\n--- STATIC SCHEDULABILITY ANALYSIS ---")
    for comp in system["components"].values():
        print(f"\nComponent {comp.name} on Core {comp.core_name} using {comp.scheduling}")
        alpha, delta = find_min_bdr_params(comp.tasks, comp.scheduling)
        if alpha is None:
            print("No schedulable BDR interface found!")
        else:
            print(f"BDR Interface: α = {alpha}, ∆ = {delta}")
            Csupply, Tsupply = half_half_transform(alpha, delta)
            print(f"Supply Task: Csupply = {Csupply}, Tsupply = {Tsupply}")

def main():
    system = load_system_model_from_csv("input/tasks.csv", "input/architecture.csv", "input/budgets.csv")

    print("=== System Overview ===")
    for core in system["cores"].values():
        print(core)
        for comp in core.components:
            print("  ", comp)
            for task in comp.tasks:
                print("    ", task)

    print("\n--- Running Simulation ---")
    run_simulation(system)

    print("\n--- Running Static Analysis ---")
    run_analysis(system)

    execution_log, response_times = run_simulation(system)
    export_solution_csv(system, response_times)

if __name__ == "__main__":
    main()
