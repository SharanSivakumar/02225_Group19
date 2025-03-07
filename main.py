import csv
from typing import List

class Task:
    def __init__(self, name, period, wcet, deadline, priority):
        self.name = name
        self.period = period
        self.wcet = wcet
        self.deadline = deadline
        self.priority = priority  
        self.next_release = 0 

    def __repr__(self):
        return f"Task({self.name}, Period={self.period}, WCET={self.wcet}, Deadline={self.deadline})"

class Core:
    def __init__(self, core_id, scheduling_policy):
        self.core_id = core_id
        self.scheduling_policy = scheduling_policy 
        self.task_queue = [] 
        self.current_time = 0

    def schedule_task(self, task: Task):
        pass  #Empty for Now!

    def run(self):
        pass  #Empty for Now ;)

class ADASSimulator:
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.tasks: List[Task] = []
        self.load_configuration()

    def load_configuration(self):
        pass  #Empty for Now!

    def run_simulation(self):
        pass  #Empty for Now ;)

if __name__ == "__main__":
    input_csv = "CSV from the TEST CASE Generator"
    simulator = ADASSimulator(input_csv)
    simulator.run_simulation()
