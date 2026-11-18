# Empirical Bayes Shrinkage & Reliability Validation Report
**Project**: SupeRR Selector Season 2 — Rajasthan Royals (RR) Analytics  
**Auditor**: Senior Cricket Data Scientist & Quantitative Auditor  

---

## 1. Statistical Derivation of Empirical Bayes Hyperparameters

In quantitative sports modeling, applying Empirical Bayes shrinkage prevents low-sample outliers from dominating rankings. The shrinkage weight is given by:

$$w_i = \frac{\tau^2}{\tau^2 + \frac{\sigma^2}{n_i}} = \frac{n_i}{n_i + \frac{\sigma^2}{\tau^2}} = \frac{n_i}{n_i + K}$$

Where:
- $\sigma^2$ is the delivery-level within-player sampling variance.
- $\tau^2$ is the cross-sectional between-player true skill variance across qualified players ($\ge 100$ legal balls).
- $K = \frac{\sigma^2}{\tau^2}$ is the shrinkage constant representing the sample size required for 50% weight on observed performance.

### 1.1 Batter Strike Rate Hyperparameters
- Within-player delivery run variance: $\sigma_{\text{ball}}^2 = 2.993$
- In Strike Rate units ($\times 100$): $\sigma_{\text{bat}}^2 = 10,000 \times 2.993 = \mathbf{29,933.9}$
- Between-player career SR variance ($\ge 100$ legal balls): $\tau_{\text{bat}}^2 = \mathbf{417.2}$
$$\mathbf{K_{\text{bat}}} = \frac{29,933.9}{417.2} = \mathbf{71.7 \approx 72\text{ legal balls}}$$

### 1.2 Bowler Economy Hyperparameters
- Bowler charged run variance per ball: $\sigma_{\text{ball}}^2 = 2.931$
- In Economy units ($\times 6$): $\sigma_{\text{bowl}}^2 = 36 \times 2.931 = \mathbf{105.5}$
- Between-player career economy variance ($\ge 100$ legal balls): $\tau_{\text{bowl}}^2 = \mathbf{1.28}$
$$\mathbf{K_{\text{bowl}}} = \frac{105.5}{1.28} = \mathbf{82.5 \approx 82\text{ legal balls}}$$

---

## 2. Prior Discrepancy & Population Reconciliation

### 2.1 The Two Priors Explained
- **Reported General Baseline**: In the initial report narrative, general T20 career baselines were stated ($\mu_{\text{SR}} \approx 145.0$, $\mu_{\text{Econ}} \approx 7.80$).
- **Actual Population Prior Used by Code**: In `pipeline_v3.py`, the shrinkage formula used the empirical mean of the actual pressure population ($\text{CPS} \ge 5.0$, $n \ge 30$):
  $$\mu_{\text{press SR}} = \mathbf{133.17\text{ SR}}$$
  $$\mu_{\text{press Econ}} = \mathbf{8.24\text{ Econ}}$$
- **Cricket Rationale**: In high-pressure contexts, league-wide batting strike rates drop by ~12 points (from 145.0 to 133.17) and bowling economies rise by ~0.44 RPO (from 7.80 to 8.24). Shrinking toward the pressure-environment mean ($133.17$ and $8.24$) is the theoretically correct choice because it represents the true expectation under pressure.

---

## 3. Top 10 Player Reconciliation Table

Exported for all 1,535 players in `shrinkage_audit.csv`:

| Player Name | Role | Sample ($n$) | Raw Rate | $K$ | Code Prior | Shrunk Metric (In File) | Narrative Prior | Shrunk w/ Narrative Prior | Discrepancy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Daryl Mitchell** | Batter | 74 | 190.5 SR | 71.7 | 133.17 | **162.3** | 145.0 | 168.1 | -5.8 SR |
| **Matthew Wade** | Batter | 79 | 181.0 SR | 71.7 | 133.17 | **158.2** | 145.0 | 163.9 | -5.7 SR |
| **Sikandar Raza** | Batter | 65 | 193.8 SR | 71.7 | 133.17 | **162.0** | 145.0 | 168.2 | -6.2 SR |
| **Shimron Hetmyer** | Batter | 108 | 150.9 SR | 71.7 | 133.17 | **143.8** | 145.0 | 148.5 | -4.7 SR |
| **Mahipal Lomror** | Batter | 31 | 254.8 SR | 71.7 | 133.17 | **169.9** | 145.0 | 178.2 | -8.3 SR |
| **Maheesh Theekshana**| Bowler | 200 | 7.41 Econ | 82.5 | 8.24 | **7.65** | 7.80 | 7.52 | +0.13 Econ|
| **Richard Ngarava** | Bowler | 68 | 6.79 Econ | 82.5 | 8.24 | **7.59** | 7.80 | 7.34 | +0.25 Econ|
| **FazalHaq Farooqi** | Bowler | 137 | 7.18 Econ | 82.5 | 8.24 | **7.58** | 7.80 | 7.41 | +0.17 Econ|
| **Tim Southee** | Bowler | 126 | 7.14 Econ | 82.5 | 8.24 | **7.58** | 7.80 | 7.40 | +0.18 Econ|
| **Matheesha Pathirana**| Bowler | 243 | 7.60 Econ | 82.5 | 8.24 | **7.77** | 7.80 | 7.65 | +0.12 Econ|

---

## 4. Confidence Tier Classifications

- **HIGH Confidence** ($\ge 120$ legal pressure balls): Standard error $\le 15.8$ SR points, $\le 0.94$ Econ points.
- **MEDIUM Confidence** ($60 - 119$ legal pressure balls): Standard error $15.9 - 22.3$ SR points, $0.95 - 1.32$ Econ points.
- **LOW Confidence** ($< 60$ legal pressure balls): Standard error $> 22.4$ SR points. Shrunk aggressively toward population mean.

---
*Certified by Quantitative Sports Audit.*
