# Gate Allocation Problem (GAP)

### Interval

The data provided includes daily flight information. The time interval between the landing of a prior flight and the
departure of the subsequent flight operated by the same aircraft is considered as the gate occupancy interval. Thus, we
need to transform the flight data into intervals for gate occupancy.

To maximize the utilization of gates closer to the terminal, we segment the gate occupancy intervals for long-staying
aircraft (those with gate occupancy times greater than one hour). After the previous flight lands, a 20-minute interval
is reserved for post-flight services, following which the aircraft is towed to a remote gate. A 20-minute interval for
pre-flight services is again reserved before the next flight takes off. These two 20-minute segments constitute the gate
occupancy intervals to be calculated.

*For a specific aircraft*:

- If the first flight of the day departs from Tianjin Airport, the interval for consideration is **30 minutes before
  departure to 10 minutes before departure**.
- If the last flight of the day lands at Tianjin Airport, the interval for consideration is **10 minutes after landing
  to 30 minutes after landing**.
- For situations where a previous flight lands at Tianjin Airport and a subsequent flight departs from the same airport:
    - If the gate occupancy interval is **greater than** 1 hour, then the intervals **10 minutes after the prior
      flight's landing to 30 minutes after**, and **30 minutes before the subsequent flight's departure to 10 minutes
      before**, are the intervals to be calculated.
    - If the gate occupancy interval is **less than 1 hour**, then **10 minutes after the prior flight's landing to 10
      minutes before the subsequent flight's departure** is the interval to be calculated.

### Optimization

#### Variables：

Interval

#### Constraints：

- Accommodate various gate restrictions for different airlines and wingspans (soft constraint for airlines, meaning all
  airlines can use remote gates but at a high cost).
- Each interval must have exactly one gate allocated.
- Each gate can only be occupied by one interval at a time.
- Dependent gates (e.g., 414/414R/414L; if gate 414 is occupied, neither 414R nor 414L can be occupied by other
  intervals).

#### Objectives：

- Initial Allocation: Prefer closer gates and minimize taxi time.
- Re-allocation: Minimize changes to gate assignments while still preferring closer gates and minimizing taxi time.

### Iteration

Given the discrepancies between the estimated and actual take-off and landing times, initial calculations are based on
estimated times. Subsequently, every **15 minutes**, the actual take-off and landing times for the upcoming **60 minutes
** are updated. Additionally, the gate assignments for intervals in the next **30 minutes** remain the same as those
last saved.



---

:grey_exclamation:*not be used in this branch*

###    * :-1: ~~Local Search~~ *

~~*Reduce the number of intervals that cannot be allocated.*~~



---

### update in 2023/9/15

#### change the parking interval of each flight

A regarder dans données : dt = min(ATOT - ALDT) pour le même avion ?

- ~~Si dt <= 30 : on prend Taxi_T = 5, Gate_T = 10~~

- Si 40 <= dt : on prend Taxi_T = 5, Gate_T = 15

A l'instant t :
LDT = TLDT si t + 1h < ALDT ; ALDT sinon
TOT0 = TTOT si t + 1h < ATOT ; ATOT sinon

:collision:il est possible que TOT0 < LDT => TOT = max(TOT0, LDT + 40m)

Règles

- Si même avion :
    - Si TOT - LDT < 1h
        - ARRDEP même parking sur LDT + 5 -> TOT - 5
    - Sinon
        - ARR : LDT + 5 -> LDT + 5 + Gate_T
        - DEP : TOT - 5 - Gate_T -> TOT - 5

---

### update in 2023/9/24

#### :question: question

- :heavy_check_mark:extend those intervals which are less than 40 mins to 40 mins
    - but when we meet the situation like TLDT - ATOT less than 40 mins and ALDT - ATOT more than 60 mins,
      will it cause the problem that the fixed intervals will be changed ?

    - :bulb:maybe not, the new interval was covered by the old interval which was longer. and the interval will not
      be fixed before the TLDT change to ATOT.
- ignore the departure set and focus on the arriving set
    - but if there is actual time less than 30 mins, it will cause the problem that we miss the departure set forever.

---

### update in 2023/9/28

#### fix the stupid bug related to pass-by-value and pass-by-reference.:upside_down_face:

*~~Shameful!!!~~* :clown_face:

- **getinterval.py function: actual_target**
- This function used pass by reference for `data`. AND the `data` was changed.

#### fix the bug in variable.py

i used to delete all of the interval that has a flight who can not be detected (the actual time is later than one hour later, the target time is ealier than recent time)

now i only delete interval when the undetectable one is at the begin side of the interval 

when it is at the end side of the interval, i change the interval information.

#### fix the bug in outputdata.py
the code in function new_data.py used to rearch the right place in `data` was wrong

---

### update in 2023/10/23

#### refactor the code

---

### update in 2024/01/04

#### increase flight in pair

---

### update in 2024/01/11

[//]: # ()
[//]: # (- 保留Target时间，机型)

[//]: # (- 对于所有到达航班 实际降落时间是否会引起报道冲突 &#40;根据飞机机型加滑行时间 &#40;1.5/2 min&#41;&#41; （如果ALDT后延 其他所有时间同样后延） )

[//]: # (- 最大延误时间是多少)

### the new rules
- keep the target time and aircraft type
- for all arriving flights, will the actual landing time cause a reporting conflict (according to the aircraft type plus
  taxi time (1.5/2 min)) (if ALDT is postponed, all other times are postponed in the same way)
- what is the maximum delay time