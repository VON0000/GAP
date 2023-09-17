# Gate Allocation Problem (GAP)

### Interval

The data provided includes daily flight information. The time interval between the landing of a prior flight and the departure of the subsequent flight operated by the same aircraft is considered as the gate occupancy interval. Thus, we need to transform the flight data into intervals for gate occupancy.

To maximize the utilization of gates closer to the terminal, we segment the gate occupancy intervals for long-staying aircraft (those with gate occupancy times greater than one hour). After the previous flight lands, a 20-minute interval is reserved for post-flight services, following which the aircraft is towed to a remote gate. A 20-minute interval for pre-flight services is again reserved before the next flight takes off. These two 20-minute segments constitute the gate occupancy intervals to be calculated.

*For a specific aircraft*:

- If the first flight of the day departs from Tianjin Airport, the interval for consideration is **30 minutes before departure to 10 minutes before departure**.
- If the last flight of the day lands at Tianjin Airport, the interval for consideration is **10 minutes after landing to 30 minutes after landing**.
- For situations where a previous flight lands at Tianjin Airport and a subsequent flight departs from the same airport:
  - If the gate occupancy interval is **greater than** 1 hour, then the intervals **10 minutes after the prior flight's landing to 30 minutes after**, and **30 minutes before the subsequent flight's departure to 10 minutes before**, are the intervals to be calculated.
  - If the gate occupancy interval is **less than 1 hour**, then **10 minutes after the prior flight's landing to 10 minutes before the subsequent flight's departure** is the interval to be calculated.





### Optimization

#### Variables：

Interval

#### Constraints：

- Accommodate various gate restrictions for different airlines and wingspans (soft constraint for airlines, meaning all airlines can use remote gates but at a high cost).
- Each interval must have exactly one gate allocated.
- Each gate can only be occupied by one interval at a time.
- Dependent gates (e.g., 414/414R/414L; if gate 414 is occupied, neither 414R nor 414L can be occupied by other intervals).

#### Objectives：

- Initial Allocation: Prefer closer gates and minimize taxi time.
- Re-allocation: Minimize changes to gate assignments while still preferring closer gates and minimizing taxi time.



### Iteration

Given the discrepancies between the estimated and actual take-off and landing times, initial calculations are based on estimated times. Subsequently, every **15 minutes**, the actual take-off and landing times for the upcoming **60 minutes** are updated. Additionally, the gate assignments for intervals in the next **30 minutes** remain the same as those last saved.





*not be used in this branch*

* ### * Local Search*

*Reduce the number of intervals that cannot be allocated.*



---

### update in 2023/9/15

#### change the parking interval of each flight

A regarder dans données : dt = min(ATOT - ALDT) pour le même avion ?

- Si dt <= 30 : on prend Taxi_T = 5, Gate_T = 10

- Si 40 <= dt : on prend Taxi_T = 5, Gate_T = 15

 A l'instant t :
 LDT = TLDT si t + 1h < ALDT ; ALDT sinon
 TOT0 = TTOT si t + 1h < ATOT ; ATOT sinon

:collision:il est possible que TOT0 < LDT => TOT = max(TOT0, LDT + 30m)

 Règles

- Si même avion :
  - Si TOT - LDT < 1h
    - ARRDEP même parking sur LDT + 5 -> TOT - 5
  - Sinon
    - ARR : LDT + 5      -> LDT + 5 + Gate_T
    - DEP : TOT - 5 - Gate_T -> TOT - 5
