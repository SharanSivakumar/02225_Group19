import json, math
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


def load_system_model(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    cores = {cid: Core(cid, cdata["speed"]) for cid, cdata in data["cores"].items()}

    tasks = {}
    for tid, t in data["tasks"].items():
        tasks[tid] = Task(tid, t["wcet"], t["bcet"], t["deadline"], t["period"], t["priority"])

    components = {}
    for comp_id, comp_data in data["components"].items():
        comp = Component(comp_id, comp_data["core"], comp_data["scheduling"], comp_data["bdr"])
        for tid in comp_data["tasks"]:
            comp.add_task(tasks[tid])
        components[comp_id] = comp
        cores[comp_data["core"]].add_component(comp)

    return {
        "cores": cores,
        "components": components,
        "tasks": tasks
    }

def plot_dbf_sbf(component, dbf_func, alpha, delta, max_time=100):
    times = np.arange(0, max_time, 1)
    dbf_vals = []
    sbf_vals = []

    for t in times:
        if component.scheduling == "EDF":
            dbf = dbf_func(component.tasks, t)
        else:  # FPS
            dbf = max(dbf_func(component.tasks, t, τ) for τ in component.tasks)
        sbf = max(0, alpha * (t - delta))
        dbf_vals.append(dbf)
        sbf_vals.append(sbf)

    plt.figure(figsize=(8, 4))
    plt.plot(times, dbf_vals, label="DBF", color='blue')
    plt.plot(times, sbf_vals, label="SBF", color='green')
    plt.title(f"DBF vs SBF for {component.name} ({component.scheduling})")
    plt.xlabel("Time")
    plt.ylabel("Cumulative Resource Demand / Supply")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_gantt_chart(execution_log):
    fig, ax = plt.subplots(figsize=(12, 5))

    cores = list(execution_log[0].keys())
    core_positions = {core: i for i, core in enumerate(cores)}

    for t, tick in enumerate(execution_log):
        for core, task in tick.items():
            if task != "Idle":
                ax.broken_barh([(t, 1)], (core_positions[core], 0.9), facecolors='#0eede2')
                ax.text(t + 0.1, core_positions[core] + 0.3, task, fontsize=7)

    ax.set_yticks(list(core_positions.values()))
    ax.set_yticklabels(cores)
    ax.set_xlabel("Time")
    ax.set_title("Gantt Chart: Core Execution Timeline")
    ax.grid(True)
    plt.tight_layout()
    plt.show()

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
    sim_time = lcm(all_periods) if max_time is None else max_time
    print(f"Simulating up to time = {sim_time} units")


    execution_log = []
    response_times = defaultdict(list)
    released_tasks = defaultdict(list)
    task_state = {}

    for time in range(sim_time):
        tick_log = {}

        for core in cores.values():
            core_speed = core.speed
            selected_task = None
            min_priority = float("inf")
            earliest_deadline = float("inf")

            for comp in core.components:
                if time < comp.bdr_delta:
                    continue  
                
                allocated_ticks = int(math.floor(comp.bdr_alpha * (time - comp.bdr_delta + 1)))

                active_tasks = []
                for task in comp.tasks:
                    if time % task.period == 0:
                        released_tasks[task.name].append(time)
                        task_state[task.name] = {"remaining": task.wcet, "start": None}

                    if task.name in task_state and task_state[task.name]["remaining"] > 0:
                        active_tasks.append(task)

                if not active_tasks:
                    continue

                if comp.scheduling == "FPS":
                    active_tasks.sort(key=lambda t: t.priority)
                elif comp.scheduling == "EDF":
                    active_tasks.sort(key=lambda t: time + t.deadline - (time % t.period))

                task = active_tasks[0]
                task_state[task.name]["remaining"] -= core_speed  
                if task_state[task.name]["start"] is None:
                    task_state[task.name]["start"] = time

                selected_task = task
                break  

            tick_log[core.name] = selected_task.name if selected_task else "Idle"

    
            if selected_task and task_state[selected_task.name]["remaining"] <= 0:
                release = released_tasks[selected_task.name].pop(0)
                start = task_state[selected_task.name]["start"]
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
    best_alpha, best_delta = None, None

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
    system = load_system_model("input/system_config.json")

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
    execution_log, _ = run_simulation(system)
    plot_gantt_chart(execution_log)
    
    
if __name__ == "__main__":
    main()
