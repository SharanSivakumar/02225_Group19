import json
import random
from string import ascii_uppercase


def generate_test_case(output_file, num_cores=2, tasks_per_component=2, num_components=2):
    # Core generation
    cores = {}
    for i in range(num_cores):
        core_id = f"Core{ascii_uppercase[i]}"
        cores[core_id] = {"speed": round(random.uniform(0.5, 2.0), 1)}

    # Task generation with temporal consistency
    tasks = {}
    task_counter = 1
    for _ in range(num_components * tasks_per_component):
        task_id = f"T{task_counter}"
        period = random.choice([5, 10, 20, 25, 50])
        deadline = random.randint(period // 2, period)  # Deadline ≤ Period
        wcet = random.randint(1, min(4, deadline // 2))
        bcet = random.randint(1, wcet)  # BCET ≤ WCET
        priority = random.randint(1, 3)

        tasks[task_id] = {
            "wcet": wcet,
            "bcet": bcet,
            "deadline": deadline,
            "period": period,
            "priority": priority
        }
        task_counter += 1

    # Component generation with valid scheduling parameters
    components = {}
    task_list = list(tasks.keys())
    core_ids = list(cores.keys())

    for comp_num in range(1, num_components + 1):
        comp_id = f"Comp{comp_num}"
        scheduling = random.choice(["EDF", "FPS"])

        components[comp_id] = {
            "core": random.choice(core_ids),
            "scheduling": scheduling,
            "bdr": {
                "alpha": round(random.uniform(0.3, 0.8), 1),
                "delta": random.randint(2, 5)
            },
            "tasks": random.sample(task_list, tasks_per_component)
        }
        # Remove assigned tasks from pool
        task_list = [t for t in task_list if t not in components[comp_id]["tasks"]]

    # Build final structure
    test_case = {
        "cores": cores,
        "tasks": tasks,
        "components": components
    }

    # Save to file
    with open(output_file, 'w') as f:
        json.dump(test_case, f, indent=2)

    print(f"Generated test case saved to {output_file}")


# Example usage:
generate_test_case("generated_test_case.json")
