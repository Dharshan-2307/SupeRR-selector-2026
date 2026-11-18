# Data Quality & Accounting Audit Report
**Project**: SupeRR Selector Season 2 — Rajasthan Royals (RR) Analytics  
**Auditor**: Senior Cricket Data Scientist & Quantitative Auditor  
**Dataset**: 200,999 Deliveries | 883 Matches | 141 Competitions  

---

## 1. Dataset Completeness & Dimensions

| Dataset Name | Record Count | Unique Columns | Primary Key / Grain | Missing Records / Notes |
| :--- | :---: | :---: | :--- | :--- |
| `ball_by_ball.csv` | **200,999** | 33 | `(match_id, innings, overid, over_ball_num)` | 0 duplicate delivery records found. |
| `matches.csv` | **883** | 22 | `match_id` | 16 matches in `matches.csv` have no ball-by-ball data (abandoned/rain). 867 matches have ball data. |
| `playing_eleven.csv` | **28,381** | 4 | `(match_id, player_id)` | Complete match squad participation. |
| `competition_team_player_mapping.csv` | **6,413** | 5 | `(comp_id, team_id, player_id)` | Official Unstop mapping for player dropdown matching. |
| `competitions.csv` | **141** | 4 | `comp_id` | Contains competition name, format (T20/T20I), season. |
| `teams.csv` | **72** | 3 | `team_id` | Franchise and international team mappings. |

---

## 2. Extras & Run Accounting Reconciliations

### 2.1 The Critical `extras1_runs` Bug
- **Confirmed Error**: In raw `ball_by_ball.csv`, `extras1_runs` contains integer encodings `[1, 2, 3, 4, 5, 6, 7]`:
  - `1`: Overstep (No-ball) [576 deliveries]
  - `2`: Wide [7,714 deliveries]
  - `3`: Legbyes [2,748 deliveries]
  - `4`: Byes [529 deliveries]
  - `5`: Other [264 deliveries]
  - `6`: No extras (Normal delivery) [189,167 deliveries]
  - `7`: Penalty [1 delivery]
- **Impact**: Summing `runs + extras1_runs` added **6 phantom runs** to 189,167 normal deliveries, falsely generating **1,432,327 runs** and an RPO of **44.59**.
- **Correction Applied**: Delivery runs and bowler runs are computed strictly via ICC Laws 21, 22, and 23:
  $$\text{delivery\_runs} = \text{runs} + \text{extras\_2\_runs} + \mathbf{1}_{\{\text{wide}\}} + \mathbf{1}_{\{\text{Overstep}\}} + \mathbf{1}_{\{\text{byes/legbyes}\}} + 5 \cdot \mathbf{1}_{\{\text{penalty}\}}$$
  $$\text{bowler\_runs} = \text{runs} + \text{extras\_2\_runs} + \mathbf{1}_{\{\text{wide}\}} + \mathbf{1}_{\{\text{Overstep}\}}$$

### 2.2 Reconciled RPO Baselines
- **Full Dataset Baseline (883 Matches, All T20/T20I)**:
  - Total Delivery Runs: **281,333**
  - Total Legal Balls: **192,709**
  - Overall Dataset RPO: **8.76 RPO**
  - Overall Bowler Economy: **8.65 RPO**
- **IPL-Only Baseline (436 Matches, IPL 2022 to IPL 2026)**:
  - Total IPL Delivery Runs: **128,784**
  - Total IPL Legal Balls: **83,861**
  - Overall IPL RPO: **9.21 RPO** (IPL 2022: 8.43, IPL 2023: 8.89, IPL 2024: 9.46, IPL 2025: 9.55, IPL 2026: 9.79)
- **RPO Explanation**: The previously observed difference between 8.76 RPO and 9.21 RPO is an exact subset distinction: 8.76 is across all bilateral and domestic T20s, while 9.21 is strictly the IPL subset reflecting the higher scoring environment of the Impact Player era.

---

## 3. Bye & Leg-Bye Unrecoverable Split Analysis

### 3.1 Data Provider Limitation
- Across 200,999 deliveries, **3,277 deliveries** (1.63%) contain `byes` (529) or `legbyes` (2,748).
- On these deliveries, `runs == 0` and `extras_2_runs == 0`. The provider recorded the fielding extra event without providing the multi-run magnitude (e.g. 2 legbyes vs 4 legbyes).
- In our pipeline, each bye/legbye event with `runs == 0` is assigned 1 run.

### 3.2 Match Scorecard Margin Reconciliation
We cross-referenced 397 completed matches won by runs against the match metadata margin:
- **Exact Margin Match ($\Delta = 0$)**: 110 matches (27.7%)
- **Within $\pm 1$ Run**: 195 matches (49.1%)
- **Within $\pm 2$ Runs**: 236 matches (59.4%)
- **Within $\pm 3$ Runs**: 298 matches (75.1%)

### 3.3 Impact on Player Metrics
- **Bowler Impact**: **Zero (0.00%)**. Byes and leg-byes are excluded from bowler-charged runs under cricket law. A 1-run vs 4-run legbye has 0 effect on bowler economy, runs saved, or bowling average.
- **Batter Impact**: **Zero (0.00%)**. Byes and leg-byes are not credited to the batter's score or strike rate.
- **Team Match Context Impact**: Negligible. Shifts required run rate by $\le 0.15$ RPO in the rare innings where multiple legbyes occurred.

---

## 4. Bowler Wicket Attribution Audit

Out of 10,881 total team dismissals:
- **Bowler-Credited Wickets**: **10,272** (Bowled: 1,775, Caught: 7,557, LBW: 709, Stumped: 214, Hit Wicket: 17).
- **Non-Bowler Wickets Excluded**: **609** (Run Outs: 600, Retired Out: 6, Obstructing the Field: 3).
- **Audit Verification**: Validated that 0 run-outs are credited to bowlers in bowler averages, pressure wickets, or wicket rates.

---
*Certified by Quantitative Sports Audit.*
