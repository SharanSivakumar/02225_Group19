import csv
import random

component_ids = [
    "Camera_Sensor", "Image_Processor", "Bitmap_Processor", "Lidar_Sensor",
    "Control_Unit", "GPS_Sensor", "Communication_Unit", "Proximity_Sensor",
    "Radar_Sensor", "Sonar_Sensor", "Laser_Sensor", "Infrared_Sensor",
    "Ultraviolet_Sensor", "Thermal_Sensor", "Pressure_Sensor", "Humidity_Sensor",
    "Temperature_Sensor", "Light_Sensor", "Sound_Sensor", "Vibration_Sensor",
    "Motion_Sensor", "Acceleration_Sensor", "Gyroscope_Sensor", "Magnetometer_Sensor",
    "Compass_Sensor", "Altimeter_Sensor", "Barometer_Sensor", "Hygrometer_Sensor",
    "Anemometer_Sensor", "Rain_Gauge_Sensor", "Snow_Gauge_Sensor", "Thermometer_Sensor",
    "Pyrometer_Sensor", "Photometer_Sensor"
]

def generate_test_case(num_cores, num_components):
    """Generates test cases for architecture.csv and budgets.csv."""

    # Generate architecture.csv data
    architectures = []
    for i in range(1, num_cores + 1):
        core_id = f"Core_{i}"
        speed_factor = round(random.uniform(0.5, 1.5), 2)  # Speed factor between 0.5 and 1.5
        scheduler = random.choice(["EDF", "RM"])
        architectures.append({"core_id": core_id, "speed_factor": speed_factor, "scheduler": scheduler})

    # Generate budgets.csv data
    budgets = []
    num_components = min(num_components, len(component_ids))  # Ensure num_components doesn't exceed the length of component_ids
    selected_components = component_ids[:num_components]
    priority_counter = 1
    for component_id in selected_components:
        num_repeats = random.randint(1, 5)  # Randomly select the number of repeats for each component
        for _ in range(num_repeats):
            scheduler = random.choice(["EDF", "RM"])
            budget = random.randint(1, 10)
            period = random.randint(10, 50)
            core_id = random.choice([arch["core_id"] for arch in architectures])
            priority = priority_counter if scheduler == "RM" else ""  # Only RM components have priority
            budgets.append({
                "component_id": component_id,
                "scheduler": scheduler,
                "budget": budget,
                "period": period,
                "core_id": core_id,
                "priority": priority,
            })
            if scheduler == "RM":
                priority_counter += 1
                if priority_counter > 4:
                    priority_counter = 1

    return architectures, budgets

def generate_tasks(budgets, num_tasks):
    """Generates tasks.csv data based on available components, with periodic/sporadic logic."""
    tasks = []
    priority_counter = 1
    for i in range(1, num_tasks + 1):
        task_name = f"Task_{i}"
        task_type = random.choice(["periodic", "sporadic"])
        wcet = random.randint(1, 8)
        if task_type == "periodic":
            period = random.randint(20, 100)
            min_inter_arrival = ""
        else:
            period = ""
            min_inter_arrival = random.randint(50, 200)
        component_id = random.choice(budgets)["component_id"]
        scheduler = next((budget["scheduler"] for budget in budgets if budget["component_id"] == component_id), None)
        priority = priority_counter if scheduler == "RM" else ""
        tasks.append({
            "task_name": task_name,
            "task_type": task_type,
            "wcet": wcet,
            "period": period,
            "min_inter_arrival": min_inter_arrival,
            "component_id": component_id,
            "priority": priority,
        })
        if scheduler == "RM":
            priority_counter += 1
            if priority_counter > 4:
                priority_counter = 1
    return tasks

def write_csv(filename, data, fieldnames):
    """Writes data to a CSV file."""
    with open(filename, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    num_cores = int(input("Enter the number of cores: "))
    num_components = int(input("Enter the number of components (up to {}): ".format(len(component_ids))))
    num_tasks = int(input("Enter the number of tasks: "))

    architectures, budgets = generate_test_case(num_cores, num_components)
    tasks = generate_tasks(budgets, num_tasks)

    write_csv("architecture.csv", architectures, ["core_id", "speed_factor", "scheduler"])
    write_csv(
        "budgets.csv", budgets, ["component_id", "scheduler", "budget", "period", "core_id", "priority"]
    )
    tasks_fieldnames = ["task_name", "task_type", "wcet", "period", "min_inter_arrival", "component_id", "priority"]
    write_csv("tasks.csv", tasks, tasks_fieldnames)

    print("Test cases generated successfully!")
