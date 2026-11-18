# SupeRR Selector Season 2 — Rajasthan Royals IPL 2027 Auction Analytics
> **Advanced Pressure-Performance Modeling, Empirical Bayes Shrinkage & Strategic Squad Gap Recruitment for Rajasthan Royals (RR)**  
> **Official Evaluation Status**: `READY TO FREEZE`  
> **Automated Regression Suite**: `18 / 18 Tests Passing (100%)`  
> **Target Franchise**: Rajasthan Royals (RR) | **Purse**: ₹27.05 Crore | **Slots Available**: 6 (3 Overseas)

---

## 📌 Executive Summary & Pitch Overview

This repository houses the end-to-end data science architecture, empirical pressure models, statistical shrinkage algorithms, and tactical auction strategies developed for the **SupeRR Selector Season 2** competition.

Rather than relying on raw averages or static reputation, this framework models cricket performance under **Contextual Pressure (CPS)** across 200,999 ball-by-ball deliveries. It then directly connects these validated metrics to the confirmed **19-player roster of Rajasthan Royals for IPL 2027** to solve the franchise's exact tactical vacancies created by the release of **Shimron Hetmyer** and the death-bowling workload risk on **Jofra Archer**.

```
+---------------------------------------------------------------------------------------------------------+
|                                          PROJECT PIPELINE AT A GLANCE                                   |
+---------------------------------------------------------------------------------------------------------+
|  [200,999 Deliveries] ---> [Pre-Delivery CPS State] ---> [Phase Benchmarks] ---> [Empirical Bayes]     |
|                                                                                          |              |
|                                                                                          v              |
|  [RR Squad Strategy]  <--- [RR Squad-Fit Engine]   <--- [Four Universes]   <--- [Composite Scores]     |
+---------------------------------------------------------------------------------------------------------+
```

---

## 🏆 Final Validated Player Rankings (Universe D — Available Auction Candidates)

All player names strictly match the official Unstop competition submission dropdown strings.

### 🏏 Top 10 Batters Under Pressure
*Qualified at $N \ge 60$ balls faced under high pressure ($CPS \ge 5.0$), strictly adhering to MCC Laws 21 & 22 (no-balls count as balls faced; wides do not).*

| Rank | Player Name (Dropdown ID) | Country | Pressure Balls Faced | Observed Press SR | Shrunk Press SR ($K=72$) | Career SR | Death SR | Reliability Score (0–100) | Primary Tactical Role |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 🥇 **#1** | **`Daryl Mitchell`** | New Zealand | 75 | **188.00** | **160.84** | 145.04 | 172.31 | **84.88** | Spin/Pace Middle Finisher (No. 4/5) |
| 🥈 **#2** | **`Matthew Wade`** | Australia | 80 | **178.75** | **156.87** | 138.64 | 172.25 | **84.44** | Wicketkeeper Death Finisher (No. 6/7) |
| 🥉 **#3** | **`Sikandar Raza`** | Zimbabwe | 65 | **193.85** | **161.63** | 135.53 | 197.30 | **83.14** | High-Impact All-Rounder (No. 5/6) |
| 🏅 **#4** | **`Shimron Hetmyer`** | West Indies | 109 | **149.54** | **142.78** | 151.65 | 168.17 | **75.69** | Proven Left-Hand Death Finisher |
| 🏅 **#5** | **`Gareth Delany`** | Ireland | 88 | **169.32** | **152.77** | 129.05 | 167.53 | **74.58** | Power-Hitting Floater / Finisher |
| 🏅 **#6** | **`Mohammad Nabi`** | Afghanistan | 63 | **133.33** | **132.92** | 130.02 | 171.43 | **69.54** | Veteran Spin-Bowling Anchor |
| 🏅 **#7** | **`Mark Adair`** | Ireland | 93 | **136.56** | **134.81** | 139.71 | 158.89 | **66.06** | Bowling All-Rounder / No. 8 Hitter |
| 🏅 **#8** | **`Barry McCarthy`** | Ireland | 77 | **137.66** | **135.19** | 122.32 | 136.00 | **60.94** | Lower-Order Boundary Striker |
| 🏅 **#9** | **`Ryan Burl`** | Zimbabwe | 86 | **117.44** | **124.33** | 120.82 | 149.08 | **42.09** | Left-Hand Stabilizer |
| 🏅 **#10** | **`Chamika Karunaratne`** | Sri Lanka | 86 | **127.91** | **130.03** | 101.97 | 117.46 | **41.40** | Seam-Bowling All-Rounder |

---

### 🎯 Top 10 Bowlers Under Pressure
*Qualified at $N \ge 60$ legal pressure deliveries ($CPS \ge 5.0$), accounting strictly for bowler-charged runs (byes, leg-byes, and penalty runs excluded).*

| Rank | Player Name (Dropdown ID) | Country | Pressure Legal Balls | Observed Press Econ | Shrunk Press Econ ($K=82$) | Pressure Wickets | Death Econ | Reliability Score (0–100) | Primary Tactical Role |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 🥇 **#1** | **`Maheesh Theekshana`** | Sri Lanka | 200 | **7.41** | **7.65** | 9 | 8.85 | **78.05** | Powerplay & Death Mystery Spinner |
| 🥈 **#2** | **`Richard Ngarava`** | Zimbabwe | 68 | **6.79** | **7.59** | 5 | 8.89 | **77.49** | Hostile Left-Arm Express Pace |
| 🥉 **#3** | **`FazalHaq Farooqi`** | Afghanistan | 137 | **7.18** | **7.58** | 11 | 9.04 | **76.65** | Left-Arm Swing & Death Yorker Specialist |
| 🏅 **#4** | **`Tim Southee`** | New Zealand | 126 | **7.14** | **7.58** | 11 | 9.60 | **75.78** | Experienced Fast-Medium Death Leader |
| 🏅 **#5** | **`Ravichandran Ashwin`** | India | 117 | **6.97** | **7.50** | 9 | 8.86 | **74.23** | Tactical Defensive Off-Spin Anchor |
| 🏅 **#6** | **`Matheesha Pathirana`** | Sri Lanka | 243 | **7.60** | **7.77** | **23** | 8.52 | **73.01** | Elite Slinger Death Wicket-Taker |
| 🏅 **#7** | **`Adam Zampa`** | Australia | 132 | **7.45** | **7.76** | 10 | 8.78 | **72.43** | Wicket-Taking Middle-Overs Leg-Spin |
| 🏅 **#8** | **`Wanindu Hasaranga`** | Sri Lanka | 159 | **7.96** | **8.06** | 16 | 9.77 | **71.62** | Attacking Wrist-Spin & Lower-Order Bat |
| 🏅 **#9** | **`Gerald Coetzee`** | South Africa | 65 | **6.74** | **7.58** | 6 | 9.78 | **70.32** | Express Enforcer (145+ km/h) |
| 🏅 **#10** | **`Barry McCarthy`** | Ireland | 72 | **7.50** | **7.89** | 6 | 9.87 | **67.88** | Heavy-Ball Seam Depth |

---

## 👑 Rajasthan Royals (IPL 2027) Squad Analysis & Strategy

### 1. Confirmed Squad (19 Players)
- **Batters / Wicketkeepers (8)**: Yashasvi Jaiswal, Vaibhav Sooryavanshi, Dhruv Jurel, Riyan Parag, Aman Rao Perala, Shubham Dubey, Lhuan-dre Pretorius (OS), Donovan Ferreira (OS).
- **All-Rounders (2)**: Ravindra Jadeja, Dasun Shanaka (OS).
- **Pace Bowlers (7)**: Jofra Archer (OS), Mohammed Shami (*Traded in from LSG*), Nandre Burger (OS), Sandeep Sharma, Brijesh Sharma, Sushant Mishra, Yash Raj Punja.
- **Spin Bowlers (2)**: Ravi Bishnoi, Manimaran Siddharth (*Traded in from LSG*).
- **Confirmed Outgoing Trade**: Sam Curran traded to LSG.
- **Released Players (9)**: Shimron Hetmyer, Tushar Deshpande, Adam Milne, Kuldeep Sen, Yudhvir Singh, Kwena Maphaka, Vignesh Puthur, Ravi Singh, Emanjot Singh Chahal.

### 2. Biggest Squad Strengths & Critical Gaps
- **Strength 1 (World-Class Powerplay)**: Shami (6.65 Press Econ) + Archer (7.07 Press Econ) + Burger + Sandeep.
- **Strength 2 (Impenetrable Spin Choke)**: Bishnoi (124 wkts) + Jadeja (7.87 Econ) lock down overs 7–15.
- **Strength 3 (Youthful Core)**: Jaiswal, Parag, Jurel anchor the top 4.
- **Gap 1 (The Hetmyer Vacancy — #1 Need)**: Releasing Shimron Hetmyer leaves zero proven left-handed death finishers. Retained options (Ferreira, Dubey) are untested across a full IPL playoff campaign.
- **Gap 2 (Death Bowling Fragility — Mandatory Need)**: Jofra Archer is workload-managed. Sandeep Sharma conceded 10.25 RPO under pressure, and Shami is primarily a new-ball pacer. RR requires a dedicated overseas death partner.
- **Gap 3 (Indian Middle Depth)**: High cliff after Parag/Jurel down to uncapped domestic players.

---

### 3. Recommended Auction Allocation (Scenario C — Dual-Pillar Strategy)
*Allocating 6 slots and ₹27.05 Crore budget buffer-safely:*

```
+---------------------------------------------------------------------------------------------------------+
|                                RECOMMENDED RR AUCTION COMBINATION (6 SLOTS)                             |
+-----------------------------+----------+-----------------------+---------------------+------------------+
| TARGET PLAYER               | OVERSEAS | TACTICAL ROLE         | TARGET BUDGET BAND  | PURPOSE          |
+-----------------------------+----------+-----------------------+---------------------+------------------+
| 1. FazalHaq Farooqi         | Yes (1/3)| Left-Arm Death Pacer  | ₹7.50 – 9.00 Cr     | Solves Archer gap|
| 2. Daryl Mitchell / Hetmyer | Yes (2/3)| Marquee No. 5 Finisher| ₹8.00 – 9.50 Cr     | Solves Hetmyer gap|
| 3. Mahipal Lomror           | No (Ind) | Indian No. 6 Power Bat| ₹4.00 – 5.00 Cr     | Solves Ind depth |
| 4. Umran Malik / D. Chahar  | No (Ind) | Indian Pace Backup    | ₹2.00 – 3.00 Cr     | Hedges Shami age |
| 5. Shamar Springer / Raza   | Yes (3/3)| Seam All-Round Backup | ₹1.00 – 1.50 Cr     | Squad balance    |
| 6. Domestic Indian WK / Bat | No (Ind) | Bench Keeper (Base)   | ₹0.30 – 0.50 Cr     | Roster insurance |
+-----------------------------+----------+-----------------------+---------------------+------------------+
| TOTAL: 6 Players (3 OS, 3 Ind) | Total Estimated Spend: ~₹24.00 – 26.50 Cr | Purse Buffer: ~₹0.55 – 3.05 Cr |
+---------------------------------------------------------------------------------------------------------+
```

---

## 🔬 Core Mathematical Methodology

### 1. Pre-Delivery Match Context Index ($CPS$)
To eliminate outcome bias, match context is calculated immediately **before** ball $N$:
$$CPS = \min\left(10, \ (SPI + \text{CollapseAdjustment}) \times \text{MatchStakes}\right)$$

- **Chase Innings ($SPI_{\text{chase}}$)**:
  $$RateRatio = \text{clip}\left(\frac{RRR}{RemainingParRPO}, 0.2, 3.5\right)$$
  $$ResourcePressure = \left(\frac{5}{W_{\text{rem}}}\right)^{0.60}, \quad Urgency = 1 + 0.40\left(1 - \frac{B_{\text{rem}}}{B_{\text{total}}}\right)$$
  $$SPI_{\text{chase}} = \min\left(10, \ 2.80 \times RateRatio \times ResourcePressure \times Urgency\right)$$

- **First Innings ($SPI_{1\text{st}}$)**:
  Uses cumulative progressive benchmarks (Powerplay: 8.94 RPO, Middle: 8.59 RPO, Death: 10.94 RPO):
  $$DeficitRate = \frac{(ExpectedCumulativeScore - CumulativeRuns) \times 6}{k_{\text{legal}}}$$
  $$SPI_{1\text{st}} = \min\left(10, \ 0.90 \times \text{clip}(2.5 + 0.5 \times DeficitRate, 0.5, 6.0) \times \left(\frac{5}{W_{\text{rem}}}\right)^{0.45} \times \left[1 + 0.30\left(1 - \frac{B_{\text{rem}}}{B_{\text{total}}}\right)\right]\right)$$

- **Pre-Delivery Collapse Trigger**: Fires if $\ge 3$ wickets fell in the preceding 18 legal deliveries, adding $+1.20$ points to SPI.

### 2. Empirical Bayes Statistical Shrinkage
To prevent small-sample noise from dominating rankings:
$$\theta_{\text{shrunk}} = \frac{n_i \cdot \hat{\theta}_i + K \cdot \mu_0}{n_i + K}, \quad \text{where } K = \frac{\sigma^2}{\tau^2}$$
- **Batting**: $K_{\text{bat}} = 72.0$, Population Prior $\mu_{0, \text{bat}} = 132.55$ SR.
- **Bowling**: $K_{\text{bowl}} = 82.0$, Population Prior $\mu_{0, \text{bowl}} = 8.65$ Econ.

---

## 📁 Repository Directory Structure

```text
├── README.md                                  <- Master executive documentation (this file)
├── .gitignore                                 <- Clean ignore rules (excludes raw 41MB dumps)
│
├── rankings/                                  <- Final validated player ranking tables
│   ├── CORRECTED_FINAL_BATTER_TOP10.csv       <- Verified Top 10 Batters (Unstop strings)
│   ├── CORRECTED_FINAL_BOWLER_TOP10.csv       <- Verified Top 10 Bowlers (Unstop strings)
│   ├── RR_SQUAD_FIT_RANKINGS.csv              <- Complete player pool ranked by RR Squad Fit
│   ├── BATTER_BALLS_FACED_RECONCILIATION.csv  <- MCC Laws 21/22 balls-faced reconciliation
│   ├── SHRINKAGE_ALTERNATIVE_ESTIMATES.csv    <- Empirical Bayes K comparisons & variance
│   ├── CORRECTED_THRESHOLD_COUNTS.csv         <- Universe D player counts (60, 90, 120, 180b)
│   └── ILLEGAL_DELIVERY_RECONCILIATION.csv    <- Exact 200,999 delivery reconciliation table
│
├── squad_data/                                <- Rajasthan Royals squad & auction assets
│   ├── RR_CONFIRMED_SQUAD_2027.csv            <- 19 confirmed RR squad members & skill profiles
│   ├── RR_RELEASED_AND_TRADED_PLAYERS.csv     <- 9 releases + 3 trades (Shami, Siddharth, Curran)
│   ├── RR_ROLE_REQUIREMENTS.csv               <- 6 distinct auction requirement definitions
│   └── RR_AUCTION_SHORTLIST.csv               <- 16 shortlisted targets across 8 buckets
│
├── reports/                                   <- Deep technical and tactical reports
│   ├── RR_FINAL_RECRUITMENT_RECOMMENDATIONS.md<- Answers to 10 strategic decision questions
│   ├── RR_AUCTION_SCENARIOS.md                <- Detailed 6-slot Scenarios A, B, and C
│   ├── RR_SQUAD_GAP_ANALYSIS.md               <- Priority matrix for Hetmyer & Archer vacancies
│   ├── RR_SQUAD_ROLE_ANALYSIS.md              <- Full 19-man roster operational evaluation
│   ├── FINAL_FOUR_ISSUE_AUDIT.md              <- Audit resolving the final four audit items
│   ├── DATA_QUALITY_REPORT.md                 <- Extras, bowler runs, and wicket accounting audit
│   ├── PRESSURE_MODEL_VALIDATION.md           <- Unit tests for SPI, par, and pre-delivery timing
│   └── SHRINKAGE_VALIDATION.md                <- Mathematical proof of shrinkage convergence
│
└── src/                                       <- Production Python codebase
    ├── pipeline_v3.py                         <- Core data processing and feature engine
    ├── run_validation_tests.py                <- 18-test automated regression verification suite
    ├── resolve_final_four_issues.py           <- Audit reconciliation execution script
    └── build_rr_auction_analysis.py           <- RR squad fit scoring and auction engine
```

---

## ⚡ How to Replicate & Verify

### 1. Requirements
- Python 3.10+
- `pandas`, `numpy`, `pyarrow`

### 2. Run Automated Regression Test Suite (18 Tests)
To verify all mathematical formulas, bowler wicket credits, and delivery reconciliations:
```bash
python src/run_validation_tests.py
```
*Expected Output: `VALIDATION SUITE COMPLETE: 18/18 PASSED (100%)`.*

### 3. Re-Generate RR Squad Fit Rankings
```bash
python src/build_rr_auction_analysis.py
```

---
*Developed for SupeRR Selector Season 2 — Rajasthan Royals Analytics Challenge.*
