# Pressure Model & CPS Validation Report
**Project**: SupeRR Selector Season 2 — Rajasthan Royals (RR) Analytics  
**Auditor**: Senior Cricket Data Scientist & Quantitative Auditor  
**Enriched Deliveries Evaluated**: 200,961 (Regular Innings 1 & 2)  

---

## 1. Pressure Distribution & Threshold Analysis

### 1.1 Verified Dataset Distribution (CPS $\ge 5.0$)
A critical audit requirement was validating whether CPS $\ge 5.0$ captured approximately 14% of deliveries.

**Actual Empirically Calculated Distribution (Pre-Delivery State)**:
- **Normal Pressure** ($\text{CPS} < 3.0$): **129,134 deliveries (64.26%)** across 867 matches (Mean CPS: 1.95)
- **Moderate Pressure** ($3.0 \le \text{CPS} < 5.0$): **51,211 deliveries (25.48%)** across 860 matches (Mean CPS: 3.75)
- **High Pressure** ($5.0 \le \text{CPS} < 7.5$): **11,014 deliveries (5.48%)** across 701 matches (Mean CPS: 5.93)
- **Extreme Pressure** ($7.5 \le \text{CPS} \le 10.0$): **9,602 deliveries (4.78%)** across 564 matches (Mean CPS: 9.45)

**Total High + Extreme Pressure ($\text{CPS} \ge 5.0$)**: **20,616 deliveries = 10.26% of the dataset**.

> **Audit Correction**: The earlier cited figure of ~14% was from an uncalibrated intermediate run (which yielded 13.86%). Under the strict pre-delivery timing where the outcome of delivery $N$ cannot leak into its own state, the verified empirical frequency of pressure contexts is **10.26%**. This confirms that the threshold isolates the top decile of high-leverage deliveries.

---

## 2. Pre-Delivery State Timing (Causal Integrity)

### 2.1 The Principle of Zero Outcome Leakage
In previous iterations, the outcome of delivery $N$ was added to cumulative totals before evaluating pressure, meaning:
- A batter hitting a six on delivery $N$ lowered the pressure assigned to delivery $N$.
- A bowler taking a wicket on delivery $N$ raised the pressure assigned to delivery $N$.

### 2.2 Rebuilt Causal Sequence
In `pipeline_v3.py`, match state is sampled **strictly prior to the delivery being bowled**:
$$\text{pre\_runs}_N = \sum_{i=1}^{N-1} \text{runs}_i, \quad \text{pre\_wickets}_N = \sum_{i=1}^{N-1} \text{wickets}_i, \quad \text{pre\_legal}_N = \sum_{i=1}^{N-1} \text{legal}_i$$
Delivery $N$ faces the pressure created by $N-1$. The outcome of $N$ updates the state exclusively for delivery $N+1$.

**Automated Test 5 Evidence**:
On match 13511, delivery $N$ (a wicket ball) had $\text{pre\_wickets} = 0$. On delivery $N+1$, $\text{pre\_wickets} = 1$. Zero leakage confirmed.

---

## 3. Second-Innings Remaining-Phase Weighted Par Verification

### 3.1 Mathematical Formula
$$\text{RemainingParRPO} = \frac{b_{PP} \cdot \frac{\text{RPO}_{PP}^{(2)}}{6} + b_{MID} \cdot \frac{\text{RPO}_{MID}^{(2)}}{6} + b_{DEATH} \cdot \frac{\text{RPO}_{DEATH}^{(2)}}{6}}{B_{\text{rem}}} \times 6$$
Where empirical IPL 2nd innings baselines are:
- $\text{RPO}_{PP}^{(2)} = 9.05$
- $\text{RPO}_{MID}^{(2)} = 8.74$
- $\text{RPO}_{DEATH}^{(2)} = 10.28$

### 3.2 Unit Test Evidence (Zero Accidental Division by 6)
- **Case 1 (30 balls in Death)**: Remaining Par = **10.28 RPO**
- **Case 2 (15 Middle, 15 Death)**: Remaining Par = **9.51 RPO**
- **Case 3 (30 Middle, 30 Death)**: Remaining Par = **9.51 RPO**
- **Case 4 (Shortened 10-over match at ball 20)**: Remaining Par = **8.86 RPO**
- **Case 5 (1 ball remaining, 5 needed)**: Remaining Par = **10.28 RPO**, SPI hits ceiling **10.00**.
- **Case 6 (All-out situation)**: $W_{\text{rem}} = 1$, SPI hits ceiling **10.00**.

---

## 4. First-Innings Progressive Cumulative Expected Score

### 4.1 Expected Score Accumulation
$$\text{ExpectedScore}(k) = \begin{cases}
k \times \frac{8.94}{6} & 0 \le k \le 36 \\
53.64 + (k - 36) \times \frac{8.59}{6} & 37 \le k \le 90 \\
130.95 + (k - 90) \times \frac{10.94}{6} & 91 \le k \le 120
\end{cases}$$

$$\text{DeficitRate} = \frac{(\text{ExpectedScore}(k) - \text{CumulativeRuns}) \times 6}{k} \quad (\text{safe } 0 \text{ at } k = 0)$$

$$\mathbf{\text{SPI}_{1st}} = \min\left(10.0,\; 0.90 \times \text{clip}(2.50 + 0.50 \cdot \text{DeficitRate}, 0.5, 6.0) \times \left(\frac{5}{W_{\text{rem}}}\right)^{0.45} \times \left[1 + 0.30 \left(1 - \frac{B_{\text{rem}}}{B_{\text{total}}}\right)\right]\right)$$

---

## 5. Collapse Detection & Match Stakes Audit

- **Pre-Delivery Rolling 18-Ball Window**: Evaluates preceding 18 legal deliveries. Detected **9,731 collapse deliveries across 716 matches**.
- **Bounded Adjustment**: Adds $+1.50$ to SPI. Total CPS is strictly capped at $10.0$.
- **Match Stakes Multiplier**:
  - Exactly **31 playoff/knockout matches** (`knock_out == 1` or stage in Qualifier, Eliminator, Semi-Final, Final) receive $1.30\times$.
  - League matches and non-knockout Super 4 matches receive $1.00\times$.

---
*Certified by Quantitative Sports Audit.*
