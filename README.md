# 02225_Group19

This project implements a fixed-priority preemptive scheduler using Rate Monotonic Scheduling (RMS).

## Files

- `main.py` — Main script for loading input, running RTA and simulation, and displaying results.
- `Test_Case_Generator/` — Folder containing input CSV files with task sets and Custom Test Case Generator.
- `Output` - Folder containing the  `solution.csv` along with the `Analysis Log`.



## How to Run project


Run the tool via a CLI where the Input path to the directory containg all three files architecture,csv, budgets,csv and task.csv in :

```bash
python main.py "./Test_Case_Generator/<file name>"
```

After execution the ./Output directoty will contain the `solution.csv` along with the `Analysis Log`.

## Test Case Generator :

This Python script generates synthetic test data for systems with multiple cores, components, and tasks, outputting the data into `architecture.csv`, `budgets.csv`, and `tasks.csv`. Useful for testing scheduling algorithms and system performance.

Files Generated :

  `architecture.csv`: Core architecture details (ID, speed factor, scheduler).
  `budgets.csv`: Component details (ID, scheduler, budget, period, assigned core, priority).
  `tasks.csv`: Task details (name, WCET, period, assigned component, priority).

Requirements :

  Python 3.x
 `csv`, `random` libraries (standard Python)

Usage :

1.  Save the script (`test_case_generator.py`).
2.  Run: `python test_case_generator.py`
3.  Enter the number of cores, components, and tasks when prompted.

Input Parameters :

  Cores: Number of processing cores.
  Components: Number of system components (from predefined list).
  Tasks: Number of tasks to generate.

Details :

The script generates random values for system parameters:
  Cores have a speed factor (0.5-1.5) and scheduler (EDF/RM).
  Components are selected from a predefined list, with a random number of instances (1-5) each. They have a budget, period, assigned core, and priority (if RM).
  Tasks have a WCET, period, assigned component, and priority (if the component's scheduler is RM).

CSV File Formats :

  `architecture.csv`: `core_id`, `speed_factor`, `scheduler`
  `budgets.csv`: `component_id`, `scheduler`, `budget`, `period`, `core_id`, `priority`
  `tasks.csv`: `task_name`, `wcet`, `period`, `component_id`, `priority`

Notes :

  Modify the `component_ids` list in the script to customize component types.
  Priority values increment from 1 to 5 and loop.
