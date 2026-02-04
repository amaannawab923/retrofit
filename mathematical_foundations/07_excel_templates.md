# Excel Templates for Warehouse Robotics Simulation
## Ready-to-Use Formulas and Templates

---

## 1. Node Definition Sheet

### Structure
| Column | Header | Description |
|--------|--------|-------------|
| A | Node_ID | Unique identifier (N01, N02, etc.) |
| B | X_Coord | X position in meters |
| C | Y_Coord | Y position in meters |
| D | Zone_Type | Receiving, Storage, Shipping |
| E | Description | Node description |

### Sample Data
```
| A     | B | C  | D         | E           |
|-------|---|----|-----------| ------------|
| N01   | 0 | 20 | Receiving | Dock Door 1 |
| N02   | 10| 20 | Receiving | Dock Door 2 |
| N03   | 20| 20 | Receiving | Dock Door 3 |
| N04   | 30| 20 | Receiving | Dock Door 4 |
| N05   | 0 | 10 | Storage   | Aisle A     |
| N06   | 10| 10 | Storage   | Aisle B     |
| N07   | 20| 10 | Storage   | Aisle C     |
| N08   | 30| 10 | Storage   | Aisle D     |
| N09   | 0 | 0  | Shipping  | Outbound 1  |
| N10   | 10| 0  | Shipping  | Outbound 2  |
| N11   | 20| 0  | Shipping  | Outbound 3  |
| N12   | 30| 0  | Shipping  | Outbound 4  |
```

---

## 2. Distance Matrix Sheet

### Manhattan Distance Formula
For cell at row i, column j (where row 1 and column A are headers):

```excel
=ABS(INDEX(Nodes!$B$2:$B$13,ROW()-1) - INDEX(Nodes!$B$2:$B$13,COLUMN()-1)) +
 ABS(INDEX(Nodes!$C$2:$C$13,ROW()-1) - INDEX(Nodes!$C$2:$C$13,COLUMN()-1))
```

### Euclidean Distance Formula
```excel
=SQRT(
  (INDEX(Nodes!$B$2:$B$13,ROW()-1) - INDEX(Nodes!$B$2:$B$13,COLUMN()-1))^2 +
  (INDEX(Nodes!$C$2:$C$13,ROW()-1) - INDEX(Nodes!$C$2:$C$13,COLUMN()-1))^2
)
```

### Weighted Distance (with Zone Weights)
Assuming zone weights in a lookup table:

```excel
=Manhattan!B2 * (VLOOKUP(INDEX(Nodes!$D$2:$D$13,ROW()-1),ZoneWeights!$A$2:$B$4,2,FALSE) +
                 VLOOKUP(INDEX(Nodes!$D$2:$D$13,COLUMN()-1),ZoneWeights!$A$2:$B$4,2,FALSE)) / 2
```

### Zone Weights Reference Table
```
| A         | B      |
|-----------|--------|
| Zone_Type | Weight |
| Receiving | 1.2    |
| Storage   | 1.0    |
| Shipping  | 1.3    |
```

---

## 3. Travel Time Calculation Sheet

### Column Structure
| Col | Header | Formula |
|-----|--------|---------|
| A | From_Node | (input) |
| B | To_Node | (input) |
| C | Distance | =VLOOKUP(A2,Manhattan!$A:$M,MATCH(B2,Manhattan!$1:$1,0),FALSE) |
| D | Num_Turns | (input) |
| E | Queue_Wait | (input) |
| F | Cruise_Speed | =Parameters!$B$2 |
| G | Acceleration | =Parameters!$B$3 |
| H | Turn_Time | =Parameters!$B$4 |
| I | D_Accel | =(F2^2)/(2*G2) |
| J | Full_Profile | =IF(C2>=2*I2,TRUE,FALSE) |
| K | T_Accel | =IF(J2,F2/G2,SQRT(G2*C2)/G2) |
| L | T_Cruise | =IF(J2,(C2-2*I2)/F2,0) |
| M | T_Decel | =K2 |
| N | T_Turns | =D2*H2 |
| O | Total_Time | =K2+L2+M2+N2+E2 |

### Summary Formula
```excel
Total_Travel_Time = T_Accel + T_Cruise + T_Decel + T_Turns + Queue_Wait
```

Expanded:
```excel
=IF(Distance >= 2*(Speed^2)/(2*Accel),
    Speed/Accel + (Distance - Speed^2/Accel)/Speed + Speed/Accel + Turns*TurnTime + Queue,
    2*SQRT(Accel*Distance)/Accel + Turns*TurnTime + Queue
)
```

---

## 4. Parameters Sheet

### Structure
| A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|
| Parameter | Value | Unit | Min | Max | Valid | Notes |

### AGV Parameters
```excel
| Parameter       | Value | Unit   | Min  | Max  | Valid                     |
|-----------------|-------|--------|------|------|---------------------------|
| AGV_Count       | 5     | count  | 1    | 50   | =AND(B2>=D2,B2<=E2)       |
| Cruise_Speed    | 1.5   | m/s    | 0.5  | 3.0  | =AND(B3>=D3,B3<=E3)       |
| Acceleration    | 0.5   | m/s^2  | 0.2  | 1.0  | =AND(B4>=D4,B4<=E4)       |
| Turn_Delay      | 2.0   | s      | 0.5  | 5.0  | =AND(B5>=D5,B5<=E5)       |
| AGV_Length      | 1.2   | m      | 0.8  | 2.5  | =AND(B6>=D6,B6<=E6)       |
| AGV_Width       | 0.8   | m      | 0.5  | 1.5  | =AND(B7>=D7,B7<=E7)       |
| Safety_Buffer   | 0.5   | m      | 0.3  | 1.0  | =AND(B8>=D8,B8<=E8)       |
```

### Battery Parameters
```excel
| Parameter           | Value | Unit  | Min | Max | Valid                     |
|---------------------|-------|-------|-----|-----|---------------------------|
| Battery_Capacity    | 100   | kWh   | 20  | 200 | =AND(B12>=D12,B12<=E12)   |
| Low_Threshold_bl    | 20    | %     | 10  | 30  | =AND(B13>=D13,B13<=E13)   |
| High_Threshold_bh   | 95    | %     | 85  | 100 | =AND(B14>=D14,B14<=E14)   |
| Discharge_Idle      | 0.5   | %/hr  | 0.1 | 1.0 | =AND(B15>=D15,B15<=E15)   |
| Discharge_Moving    | 2.0   | %/hr  | 1.0 | 5.0 | =AND(B16>=D16,B16<=E16)   |
| Discharge_Loaded    | 3.5   | %/hr  | 2.0 | 8.0 | =AND(B17>=D17,B17<=E17)   |
| Charging_Rate       | 10    | %/hr  | 5   | 50  | =AND(B18>=D18,B18<=E18)   |
```

### Validation Summary
```excel
All_Valid = =AND(F2:F25)
```

---

## 5. Constraint Checking Sheet

### Aisle Width Constraint
```
W_aisle >= W_agv + 2 * d_safety + clearance (unidirectional)
W_aisle >= 2 * W_agv + 3 * d_safety (bidirectional)
```

```excel
| A                 | B        | C                                              |
|-------------------|----------|------------------------------------------------|
| Aisle_Width       | 2.5      | (from Parameters)                              |
| AGV_Width         | 0.8      | (from Parameters)                              |
| Safety_Buffer     | 0.5      | (from Parameters)                              |
| Sensor_Clearance  | 0.2      |                                                |
| Is_Bidirectional  | FALSE    |                                                |
| Min_Width_Uni     | =B2+2*B3+B4 |                                             |
| Min_Width_Bi      | =2*B2+3*B3 |                                              |
| Required_Width    | =IF(B5,B7,B6) |                                           |
| Margin            | =B1-B8   |                                                |
| PASS/FAIL         | =IF(B9>=0,"PASS","FAIL: Need "&ABS(B9)&"m more") |
```

### Floor Load Constraint
```
P_dynamic = (M_agv + M_payload) * g * (1 + a/g) / A_contact
P_dynamic <= P_floor_max
```

```excel
| A                  | B        | C                                       |
|--------------------|----------|-----------------------------------------|
| AGV_Mass           | 200      | kg                                      |
| Payload_Mass       | 500      | kg                                      |
| Wheel_Contact_Area | 0.01     | m^2 per wheel                           |
| Num_Wheels         | 4        |                                         |
| Acceleration       | 0.5      | m/s^2                                   |
| Floor_Capacity     | 50000    | Pa                                      |
| g                  | 9.81     | m/s^2                                   |
| Total_Mass         | =B1+B2   |                                         |
| Total_Contact      | =B3*B4   |                                         |
| Static_Pressure    | =B8*B7/B9 |                                        |
| Dynamic_Factor     | =1+B5/B7 |                                         |
| Dynamic_Pressure   | =B10*B11 |                                         |
| Utilization_%      | =B12/B6*100 |                                       |
| PASS/FAIL          | =IF(B12<=B6,"PASS","FAIL: Overload by "&(B12-B6)&" Pa") |
```

### Battery Feasibility Check
```
available = B_current - bl_k
required = (d_task * r_loaded + d_charger * r_moving) / (speed * 3600)
feasible = required <= available
```

```excel
| A                   | B        | C                                     |
|---------------------|----------|---------------------------------------|
| Current_Battery_%   | 50       |                                       |
| Low_Threshold_bl    | 20       | %                                     |
| Task_Distance       | 100      | m                                     |
| Distance_to_Charger | 30       | m                                     |
| Speed               | 1.5      | m/s                                   |
| Discharge_Loaded    | 3.5      | %/hr                                  |
| Discharge_Moving    | 2.0      | %/hr                                  |
| Available_Charge    | =B1-B2   | %                                     |
| Task_Time_hr        | =B3/(B5*3600) |                                   |
| Charger_Time_hr     | =B4/(B5*3600) |                                   |
| Task_Consumption    | =B9*B6   | %                                     |
| Charger_Consumption | =B10*B7  | %                                     |
| Total_Required      | =B11+B12 | %                                     |
| Remaining_After     | =B8-B13  | %                                     |
| FEASIBLE            | =IF(B14>=0,"PROCEED","CHARGE FIRST")  |
```

---

## 6. Performance Metrics Sheet

### Throughput Calculation
```excel
| A               | B                                          |
|-----------------|-------------------------------------------|
| Tasks_Completed | =COUNTA(TaskLog!A:A)-1                    |
| Period_Hours    | =(MAX(TaskLog!C:C)-MIN(TaskLog!B:B))/3600 |
| Hourly_Throughput | =B1/B2                                  |
| AGV_Count       | =Parameters!$B$2                          |
| Per_AGV_Throughput | =B3/B4                                 |
```

### Utilization Calculation
```excel
| A                    | B                                            |
|----------------------|---------------------------------------------|
| Total_Time           | =SUM(StateLog!D:D)                          |
| Travel_Loaded_Time   | =SUMIF(StateLog!B:B,"traveling_loaded",StateLog!D:D) |
| Travel_Empty_Time    | =SUMIF(StateLog!B:B,"traveling_empty",StateLog!D:D)  |
| Pick_Time            | =SUMIF(StateLog!B:B,"picking",StateLog!D:D)  |
| Drop_Time            | =SUMIF(StateLog!B:B,"dropping",StateLog!D:D) |
| Idle_Time            | =SUMIF(StateLog!B:B,"idle",StateLog!D:D)     |
| Wait_Time            | =SUMIF(StateLog!B:B,"waiting",StateLog!D:D)  |
| Charge_Time          | =SUMIF(StateLog!B:B,"charging",StateLog!D:D) |
| Productive_Util      | =(B2+B4+B5)/B1                              |
| Operational_Util     | =(B2+B3+B4+B5)/B1                           |
| Idle_Percentage      | =(B6+B7)/B1*100                             |
```

### Distance Metrics
```excel
| A                    | B                                     |
|----------------------|---------------------------------------|
| Total_Distance       | =SUM(TaskLog!E:E)                     |
| Loaded_Distance      | =SUMIF(TaskLog!F:F,"loaded",TaskLog!E:E) |
| Empty_Distance       | =B1-B2                                |
| Num_Tasks            | =COUNTA(TaskLog!A:A)-1                |
| Avg_Distance_Task    | =B1/B4                                |
| Empty_Travel_Ratio   | =B3/B1                                |
```

### Conflict Metrics
```excel
| A                    | B                                     |
|----------------------|---------------------------------------|
| Total_Conflicts      | =COUNTA(ConflictLog!A:A)-1            |
| Period_Hours         | =Metrics!$B$2                         |
| Conflict_Frequency   | =B1/B2                                |
| Total_Tasks          | =Metrics!$B$1                         |
| Conflicts_Per_Task   | =B1/B4                                |
| Avg_Resolution_Time  | =AVERAGE(ConflictLog!D:D)             |
| Max_Resolution_Time  | =MAX(ConflictLog!D:D)                 |
```

---

## 7. Optimization Objective Sheet

### Weight Configuration
```excel
| A          | B     | C                    |
|------------|-------|----------------------|
| Alpha_1    | 0.35  | Travel weight        |
| Alpha_2    | 0.30  | Time weight          |
| Alpha_3    | 0.20  | Energy weight        |
| Alpha_4    | 0.15  | Conflict weight      |
| Sum_Check  | =SUM(B1:B4) | Must equal 1.0  |
| Valid      | =IF(B5=1,"OK","ERROR: Weights must sum to 1") |
```

### Cost Coefficients
```excel
| A                | B      | C           |
|------------------|--------|-------------|
| Cost_Per_Meter   | 0.01   | $/m         |
| Cost_Per_Second  | 0.005  | $/s         |
| Cost_Per_Battery | 0.10   | $/%         |
| Cost_Per_Conflict| 5.00   | $/conflict  |
```

### Objective Calculation (per AGV row)
```excel
| A    | B        | C          | D         | E           | F         | G            |
|------|----------|------------|-----------|-------------|-----------|--------------|
| AGV  | Distance | TravelTime | WaitTime  | ServiceTime | BattUsed  | Conflicts    |
| AGV1 | 150      | 120        | 15        | 30          | 5.2       | 2            |
| AGV2 | 180      | 150        | 8         | 30          | 6.1       | 1            |

Z_Travel (H2) = =B2*Costs!$B$1
Z_Time (I2)   = =(C2+D2+E2)*Costs!$B$2
Z_Energy (J2) = =F2*Costs!$B$3
Z_Conflict (K2) = =G2*Costs!$B$4
Z_Total (L2)  = =Weights!$B$1*H2 + Weights!$B$2*I2 + Weights!$B$3*J2 + Weights!$B$4*K2
```

### Summary Objective
```excel
Total_Objective = =SUM(L2:L10)
```

---

## 8. Scenario Analysis Template

### Weight Sensitivity Matrix
```excel
| A              | B       | C       | D       | E       | F           |
|----------------|---------|---------|---------|---------|-------------|
| Scenario       | Alpha_1 | Alpha_2 | Alpha_3 | Alpha_4 | Total_Cost  |
| Distance Focus | 0.70    | 0.20    | 0.10    | 0.00    | =CALC...    |
| Time Focus     | 0.10    | 0.60    | 0.10    | 0.20    | =CALC...    |
| Balanced       | 0.25    | 0.25    | 0.25    | 0.25    | =CALC...    |
| Safety Focus   | 0.20    | 0.20    | 0.10    | 0.50    | =CALC...    |
| Energy Focus   | 0.20    | 0.20    | 0.50    | 0.10    | =CALC...    |
| Legacy Retrofit| 0.30    | 0.25    | 0.15    | 0.30    | =CALC...    |
```

### Total Cost Formula for Each Scenario
```excel
=SUMPRODUCT(B2:E2, RawCosts!$H$2:$K$2)
```

Where RawCosts contains unweighted component costs.

---

## 9. Data Validation Rules

### Parameter Validation
```excel
Data Validation for Speed (B3):
- Allow: Decimal
- Between: 0.5 and 3.0
- Input Message: "Enter cruise speed between 0.5 and 3.0 m/s"
- Error Alert: "Speed must be between 0.5 and 3.0 m/s"
```

### Zone Type Validation
```excel
Data Validation for Zone column:
- Allow: List
- Source: Receiving,Storage,Shipping
```

### Node ID Validation
```excel
Data Validation for Node references:
- Allow: List
- Source: =Nodes!$A$2:$A$13
```

---

## 10. Conditional Formatting Rules

### Constraint Status
```
PASS (green): =LEFT(B10,4)="PASS"
FAIL (red): =LEFT(B10,4)="FAIL"
```

### Utilization Levels
```
Good (green): >=0.75
Warning (yellow): >=0.50 AND <0.75
Critical (red): <0.50
```

### Conflict Frequency
```
Good (green): <=5
Warning (yellow): >5 AND <=15
Critical (red): >15
```

---

## Quick Reference: Key Formulas

| Metric | Formula |
|--------|---------|
| Manhattan Distance | `=ABS(X1-X2)+ABS(Y1-Y2)` |
| Euclidean Distance | `=SQRT((X1-X2)^2+(Y1-Y2)^2)` |
| Travel Time | `=D/V + N*T_turn + T_accel + T_decel + T_queue` |
| Throughput | `=Tasks/Hours` |
| Utilization | `=Active_Time/Total_Time` |
| Battery Range | `=(B_current-B_low)/(Rate/Speed)` |
| Objective | `=alpha1*Z_travel + alpha2*Z_time + alpha3*Z_energy + alpha4*Z_conflict` |
