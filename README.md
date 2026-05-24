# Parameter tuning
Parametrus keiciame:
- PSO (musu) algoritmui [PSO/gnbg_iii_competition_harness.py](PSO/gnbg_iii_competition_harness.py#146)
- DE (pavyzdiniam) algoritmui [DE/gnbg_iii_competition_harness.py](DE/gnbg_iii_competition_harness.py#149)  
### Pavyzdys nustatytu parametru:  
```py
    # Algorithm parameters (cia keiciam)
    AlgorithmParams = {}
    AlgorithmParams['PopulationSize'] = 50
    AlgorithmParams['InertiaWeight'] = 0.729
    AlgorithmParams['C1'] = 1.49445
    AlgorithmParams['C2'] = 1.49445
    AlgorithmParams['VmaxFactor'] = 0.2
```
## Run
Paleisti:
```bash
cd PSO # arba DE
pip install -r requirements.txt
python3 gnbg_iii_competition_harness.py
```

### Po kiekvieno paleidimo issaugoti nukopijuoti GNBG_III_Detailed_Results_PSO.csv faila i [PSO/run_results/](PSO/run_results/) folderi!!!

## Parametru konfiguracijos PSO (keisti faile)
```py
# Current (Default - balanced)
AlgorithmParams = {}
AlgorithmParams['PopulationSize'] = 50
AlgorithmParams['InertiaWeight'] = 0.729
AlgorithmParams['C1'] = 1.49445
AlgorithmParams['C2'] = 1.49445
AlgorithmParams['VmaxFactor'] = 0.2

# 1. Exploration-focused (larger pop, higher inertia)
AlgorithmParams = {}
AlgorithmParams['PopulationSize'] = 100
AlgorithmParams['InertiaWeight'] = 0.9
AlgorithmParams['C1'] = 1.5
AlgorithmParams['C2'] = 1.0
AlgorithmParams['VmaxFactor'] = 0.3

# 2. Exploitation-focused (smaller pop, lower inertia)
AlgorithmParams = {}
AlgorithmParams['PopulationSize'] = 30
AlgorithmParams['InertiaWeight'] = 0.4
AlgorithmParams['C1'] = 2.0
AlgorithmParams['C2'] = 2.0
AlgorithmParams['VmaxFactor'] = 0.1

# 3. Social-emphasis (C2 > C1, follow best more)
AlgorithmParams = {}
AlgorithmParams['PopulationSize'] = 50
AlgorithmParams['InertiaWeight'] = 0.7
AlgorithmParams['C1'] = 1.0
AlgorithmParams['C2'] = 2.0
AlgorithmParams['VmaxFactor'] = 0.2

# 4. Cognitive-emphasis (C1 > C2, trust own memory)
AlgorithmParams = {}
AlgorithmParams['PopulationSize'] = 50
AlgorithmParams['InertiaWeight'] = 0.7
AlgorithmParams['C1'] = 2.0
AlgorithmParams['C2'] = 1.0
AlgorithmParams['VmaxFactor'] = 0.2

# 5. High-velocity (aggressive search)
AlgorithmParams = {}
AlgorithmParams['PopulationSize'] = 20
AlgorithmParams['InertiaWeight'] = 0.95
AlgorithmParams['C1'] = 1.0
AlgorithmParams['C2'] = 1.0
AlgorithmParams['VmaxFactor'] = 0.5

# 6. Conservative (small steps, thorough)
AlgorithmParams = {}
AlgorithmParams['PopulationSize'] = 75
AlgorithmParams['InertiaWeight'] = 0.5
AlgorithmParams['C1'] = 1.5
AlgorithmParams['C2'] = 1.5
AlgorithmParams['VmaxFactor'] = 0.05

# 7. Super Exploration-focused (larger pop, higher inertia)
AlgorithmParams = {}
AlgorithmParams['PopulationSize'] = 150
AlgorithmParams['InertiaWeight'] = 0.85
AlgorithmParams['C1'] = 1.5
AlgorithmParams['C2'] = 1.0
AlgorithmParams['VmaxFactor'] = 0.3
```