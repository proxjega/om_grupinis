# run_algorithm_template.py
import numpy as np
from scipy.spatial.distance import pdist
import fitness


def _to_scalar(value):
    return float(np.asarray(value).squeeze())


def _get_optimum_value(GNBG):
    if 'OptimumValue' in GNBG:
        return _to_scalar(GNBG['OptimumValue'])
    return None


def runAlgorithmTemplate(GNBG, params):
    """
    GNBG-III compatible algorithm template with Particle Swarm Optimization (PSO).

    This function is called by the GNBG competition harness.

    INPUT:
        GNBG   - benchmark structure loaded from F*_*.mat
        params - dictionary with algorithm parameters

    OUTPUT:
        BestHistory
        BestValue
        BestPosition
        GNBG
        AcceptanceReachPoint
        Extra
    """

    # --------------------------------------------------------------
    # 1. Basic information
    # --------------------------------------------------------------
    D = int(_to_scalar(GNBG['Dimension']))
    MaxEvals = int(_to_scalar(GNBG['MaxEvals']))

    LB = np.asarray(GNBG['MinCoordinate'], dtype=float).flatten()
    UB = np.asarray(GNBG['MaxCoordinate'], dtype=float).flatten()

    if LB.size == 1:
        LB = LB.item() * np.ones(D)

    if UB.size == 1:
        UB = UB.item() * np.ones(D)

    LB = LB.reshape(-1)
    UB = UB.reshape(-1)

    # --------------------------------------------------------------
    # 2. PSO parameters
    # --------------------------------------------------------------
    NP = int(params.get('PopulationSize', 50))

    # PSO parameters:
    # w  - inertia weight
    # c1 - cognitive coefficient
    # c2 - social coefficient
    # VmaxFactor - maximum velocity as a fraction of search range
    w = params.get('InertiaWeight', params.get('w', 0.729))
    c1 = params.get('C1', params.get('c1', 1.49445))
    c2 = params.get('C2', params.get('c2', 1.49445))
    VmaxFactor = params.get('VmaxFactor', params.get('vmax_factor', 0.2))

    NP = max(2, min(NP, MaxEvals))

    # --------------------------------------------------------------
    # 3. Initial swarm
    # --------------------------------------------------------------
    X = LB + (UB - LB) * np.random.rand(NP, D)

    search_range = UB - LB
    Vmax = VmaxFactor * search_range

    # Initial velocities
    V = -Vmax + 2.0 * Vmax * np.random.rand(NP, D)

    # Best-history buffer
    BestHistory = np.full(MaxEvals, np.inf)

    # Diversity sampling schedule
    divSampleFEs = np.round(np.linspace(1, MaxEvals, 50)).astype(int)
    divIndex = 0
    DiversityHistory = np.full(50, np.nan)

    # Improvement / stagnation counters
    ImprovementCount = 0
    StagnationCount = 0
    currentStagnation = 0

    if 'FE' not in GNBG or GNBG['FE'] is None:
        GNBG['FE'] = 0

    prevFE = int(GNBG['FE'])

    # --------------------------------------------------------------
    # 4. Initial evaluation
    # --------------------------------------------------------------
    fitVals, GNBG = fitness.fitness(X, GNBG)
    fitVals = np.asarray(fitVals, dtype=float).reshape(-1)

    # Personal bests
    Pbest = X.copy()
    PbestFitness = fitVals.copy()

    bestID = int(np.argmin(PbestFitness))
    BestValue = float(PbestFitness[bestID])
    BestPosition = Pbest[bestID, :].copy()

    newFE = int(GNBG['FE'])
    BestHistory[prevFE:newFE] = BestValue
    prevFE = newFE

    lastBest = BestValue

    # --------------------------------------------------------------
    # 5. Main PSO loop
    # --------------------------------------------------------------
    while int(GNBG['FE']) < MaxEvals:
        currentFE = int(GNBG['FE'])
        remaining = MaxEvals - currentFE

        # Do not exceed the evaluation budget
        batchSize = min(NP, remaining)
        active = np.arange(batchSize)

        oldFE = int(GNBG['FE'])

        # ----------------------------------------------------------
        # 5.1 Velocity update
        # ----------------------------------------------------------
        r1 = np.random.rand(batchSize, D)
        r2 = np.random.rand(batchSize, D)

        V[active, :] = (
            w * V[active, :]
            + c1 * r1 * (Pbest[active, :] - X[active, :])
            + c2 * r2 * (BestPosition - X[active, :])
        )

        # Limit velocities
        V[active, :] = np.maximum(V[active, :], -Vmax)
        V[active, :] = np.minimum(V[active, :], Vmax)

        # ----------------------------------------------------------
        # 5.2 Position update
        # ----------------------------------------------------------
        X[active, :] = X[active, :] + V[active, :]

        # Boundary handling by clipping
        X[active, :] = np.maximum(X[active, :], LB)
        X[active, :] = np.minimum(X[active, :], UB)

        # ----------------------------------------------------------
        # 5.3 Evaluate new positions
        # ----------------------------------------------------------
        newFitness, GNBG = fitness.fitness(X[active, :], GNBG)
        newFitness = np.asarray(newFitness, dtype=float).reshape(-1)

        newFE = int(GNBG['FE'])

        # ----------------------------------------------------------
        # 5.4 Update personal bests
        # ----------------------------------------------------------
        improved = newFitness < PbestFitness[active]

        if np.any(improved):
            improvedIDs = active[improved]
            Pbest[improvedIDs, :] = X[improvedIDs, :]
            PbestFitness[improvedIDs] = newFitness[improved]

        # Store current fitness values for diagnostics
        fitVals[active] = newFitness

        # ----------------------------------------------------------
        # 5.5 Update global best
        # ----------------------------------------------------------
        currBestID = int(np.argmin(PbestFitness))
        currBestValue = float(PbestFitness[currBestID])

        if currBestValue < BestValue:
            BestValue = currBestValue
            BestPosition = Pbest[currBestID, :].copy()

        # ----------------------------------------------------------
        # 5.6 Update BestHistory
        # ----------------------------------------------------------
        BestHistory[oldFE:newFE] = BestValue
        prevFE = newFE

        # ----------------------------------------------------------
        # 5.7 Improvement and stagnation tracking
        # ----------------------------------------------------------
        if lastBest != 0:
            relImprovement = (lastBest - BestValue) / abs(lastBest)
        else:
            relImprovement = 0

        if relImprovement > 0.01:
            ImprovementCount += 1
            lastBest = BestValue
            currentStagnation = 0
        else:
            currentStagnation += 1

        if currentStagnation > 100:
            StagnationCount += 1
            currentStagnation = 0

        # ----------------------------------------------------------
        # 5.8 Diversity snapshots
        # ----------------------------------------------------------
        while divIndex < len(divSampleFEs) and int(GNBG['FE']) >= divSampleFEs[divIndex]:
            if NP > 1:
                DiversityHistory[divIndex] = np.mean(pdist(X))
            else:
                DiversityHistory[divIndex] = 0

            divIndex += 1

        # ----------------------------------------------------------
        # 5.9 Optional early stopping
        # ----------------------------------------------------------
        optimum_value = _get_optimum_value(GNBG)

        if optimum_value is not None:
            if abs(BestValue - optimum_value) <= 1e-12:
                if newFE < MaxEvals:
                    BestHistory[newFE:MaxEvals] = BestValue

                GNBG['FE'] = MaxEvals
                break

        if int(GNBG['FE']) >= MaxEvals:
            break

    # --------------------------------------------------------------
    # 6. Finalise BestHistory
    # --------------------------------------------------------------
    finite_mask = np.isfinite(BestHistory)

    if np.any(finite_mask):
        lastFilled = np.where(finite_mask)[0][-1]

        if lastFilled < MaxEvals - 1:
            BestHistory[lastFilled + 1:] = BestValue
    else:
        BestHistory[:] = BestValue

    # --------------------------------------------------------------
    # 7. Acceptance reach point
    # --------------------------------------------------------------
    AcceptanceReachPoint = np.inf
    optimum_value = _get_optimum_value(GNBG)

    if optimum_value is not None:
        err = np.abs(BestHistory - optimum_value)
        idx = np.where(err <= 1e-8)[0]

        if len(idx) > 0:
            AcceptanceReachPoint = idx[0] + 1

    # --------------------------------------------------------------
    # 8. Extra diagnostics
    # --------------------------------------------------------------
    Extra = {}
    Extra['Algorithm'] = 'Particle Swarm Optimization'
    Extra['PopulationSize'] = NP
    Extra['InertiaWeight'] = w
    Extra['C1'] = c1
    Extra['C2'] = c2
    Extra['VmaxFactor'] = VmaxFactor
    Extra['DiversityHistory'] = DiversityHistory
    Extra['ImprovementCount'] = ImprovementCount
    Extra['StagnationPeriods'] = StagnationCount

    return BestHistory, BestValue, BestPosition, GNBG, AcceptanceReachPoint, Extra