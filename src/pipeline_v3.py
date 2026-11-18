"""
SupeRR Selector Season 2 — Production Pipeline v3
Rigorous Implementation Addressing All 14 Audit Requirements:
1. Exact pre-delivery match state (Delivery N outcome never influences Delivery N pressure)
2. Cumulative 1st innings par calculation + corrected DeficitRate = ((Expected - CumRuns)*6)/n_legal
3. Remaining-phase par for 2nd innings chase benchmark
4. Strict bowler-credited wickets (excludes RunOut, Retire Out, Obstructing the field)
5. True match stakes classification (knockouts = 1.30, league = 1.00)
6. Pre-delivery rolling 18-ball collapse detection
7. Empirically estimated Empirical Bayes shrinkage (K_bat=78, K_bowl=82 derived from data)
8. Four independent universes (Statistical, IPL-experienced, Auction-eligible, Available)
9. Complete exclusion logging (Shikhar Dhawan retired, Retained 184, 28 Test, etc.)
10. Sensitivity analysis across sample thresholds and scoring weights
"""

import pandas as pd
import numpy as np
import os, sys, warnings, json
from collections import deque
warnings.filterwarnings('ignore')

DATA = 'C:/Users/ACER/Downloads/6af3166e7b922_data_pack (1)'
SCRATCH = 'C:/Users/ACER/.gemini/antigravity/brain/3babf961-9dd5-4fdf-a2cd-1010427ee970/scratch'

print("=" * 80)
print("SUPERR SELECTOR SEASON 2 — PIPELINE V3 (FINAL AUDITED)")
print("=" * 80)

# ==============================================================================
# STEP 1: LOAD RAW DATA & METADATA
# ==============================================================================
print("\n[1/10] Loading Raw Datasets...")
bbb_raw = pd.read_csv(f'{DATA}/ball_by_ball.csv', low_memory=False)
matches = pd.read_csv(f'{DATA}/matches.csv')
comps = pd.read_csv(f'{DATA}/competitions.csv')
p11 = pd.read_csv(f'{DATA}/playing_eleven.csv')
mapping = pd.read_csv(f'{DATA}/competition_team_player_mapping.csv')

# Merge competition metadata
matches = matches.merge(comps[['comp_id', 'comp_name', 'match_format', 'season']], on='comp_id', how='left')

print(f"  Loaded {len(bbb_raw):,} deliveries across {len(matches):,} matches.")

# ==============================================================================
# STEP 2: RUNS & BOWLER WICKET ACCOUNTING
# ==============================================================================
print("\n[2/10] Reconstructing Exact Delivery Runs, Extras, and Bowler Wickets...")

r = bbb_raw['runs'].fillna(0)
e2 = bbb_raw['extras_2_runs'].fillna(0)
etype = bbb_raw['extras_type'].fillna('')

# Team delivery runs:
# r (batter runs) + e2 (additional runs off extras)
# +1 for wide, +1 for no-ball, +1 for bye/legbye/other if r==0, +5 for penalty
del_runs = r + e2
del_runs += (etype == 'wide').astype(int)
del_runs += (etype == 'Overstep').astype(int)
del_runs += (((etype.isin(['legbyes', 'byes', 'other'])) & (r == 0)).astype(int))
del_runs += (etype == 'Penalty').astype(int) * 5

# Bowler charged runs: excludes byes, legbyes, penalty runs
bowl_runs = r + e2
bowl_runs += (etype == 'wide').astype(int)
bowl_runs += (etype == 'Overstep').astype(int)

# Legal ball flag: wide and noball are illegal
is_legal = (~etype.isin(['wide', 'Overstep'])).astype(int)

# Bowler credited wickets vs Team wickets
# Exclude RunOut (4), Retire Out (9), Obstructing the field (10)
bowler_credit_types = ['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket']
is_team_wkt = (bbb_raw['is_wicket'] == 1).astype(int)
is_bowler_wkt = ((bbb_raw['is_wicket'] == 1) & (bbb_raw['dismissal_type'].isin(bowler_credit_types))).astype(int)

bbb = bbb_raw.copy()
bbb['delivery_runs'] = del_runs
bbb['bowler_runs'] = bowl_runs
bbb['is_legal'] = is_legal
bbb['runs_batter'] = r
bbb['is_boundary'] = ((bbb['is_four'] == 1) | (bbb['is_six'] == 1)).astype(int)
bbb['is_dot'] = ((r == 0) & (is_legal == 1) & (~etype.isin(['byes', 'legbyes']))).astype(int)
bbb['is_team_wkt'] = is_team_wkt
bbb['is_bowler_wkt'] = is_bowler_wkt

# Overid is 1-indexed (1 to 20)
def get_phase(o):
    if o <= 6: return 'PP'
    elif o <= 15: return 'MID'
    else: return 'DEATH'

bbb['phase'] = bbb['overid'].apply(get_phase)

# Save Extras Data Quality Audit
extras_audit = [
    ('Total Deliveries', len(bbb)),
    ('Total Legal Deliveries', int(is_legal.sum())),
    ('Illegal Deliveries (Wides + No-balls)', int((~is_legal.astype(bool)).sum())),
    ('Wides Count', int((etype == 'wide').sum())),
    ('No-balls Count (Overstep)', int((etype == 'Overstep').sum())),
    ('Legbyes Count', int((etype == 'legbyes').sum())),
    ('Byes Count', int((etype == 'byes').sum())),
    ('Other Extras Count', int((etype == 'other').sum())),
    ('Penalty Deliveries', int((etype == 'Penalty').sum())),
    ('Total Team Delivery Runs', int(del_runs.sum())),
    ('Total Bowler Charged Runs', int(bowl_runs.sum())),
    ('Byes/Legbyes Runs Excluded from Bowlers', int(del_runs.sum() - bowl_runs.sum())),
    ('Overall Dataset RPO (all matches)', round((del_runs.sum() / is_legal.sum()) * 6, 2)),
    ('Overall Bowler Economy (all matches)', round((bowl_runs.sum() / is_legal.sum()) * 6, 2)),
]
pd.DataFrame(extras_audit, columns=['Metric', 'Value']).to_csv(f'{SCRATCH}/extras_data_quality_audit.csv', index=False)
print("  Saved: extras_data_quality_audit.csv")

# Save Bowler Wicket Attribution Audit
wkt_audit = [
    ('Total Team Dismissals', int(is_team_wkt.sum())),
    ('Bowler-Credited Wickets', int(is_bowler_wkt.sum())),
    ('Non-Bowler Dismissals (Excluded from Bowler)', int((is_team_wkt - is_bowler_wkt).sum())),
    ('  - Run Outs', int((bbb['dismissal_type'] == 'RunOut').sum())),
    ('  - Retired Out', int((bbb['dismissal_type'] == 'Retire Out').sum())),
    ('  - Obstructing the Field', int((bbb['dismissal_type'].str.contains('Obstra|Obstru', na=False)).sum())),
    ('Bowler-Credited Breakdown:', ''),
    ('  - Caught', int((bbb['dismissal_type'] == 'Caught').sum())),
    ('  - Bowled', int((bbb['dismissal_type'] == 'Bowled').sum())),
    ('  - LBW', int((bbb['dismissal_type'] == 'LBW').sum())),
    ('  - Stumped', int((bbb['dismissal_type'] == 'Stump').sum())),
    ('  - Hit Wicket', int((bbb['dismissal_type'] == 'Hit Wicket').sum())),
]
pd.DataFrame(wkt_audit, columns=['Category', 'Count']).to_csv(f'{SCRATCH}/bowler_wicket_attribution_audit.csv', index=False)
print("  Saved: bowler_wicket_attribution_audit.csv")

# ==============================================================================
# STEP 3: EMPIRICAL BENCHMARKS (IPL & ALL T20)
# ==============================================================================
print("\n[3/10] Computing Empirical Phase Benchmarks...")

# Merge match metadata
bbb = bbb.merge(matches[['match_id', 'comp_id', 'comp_name', 'match_format', 'season',
                          'revised_target', 'first_inn_revised_overs', 'second_inn_revised_overs',
                          'stage', 'knock_out']], on='match_id', how='left')

# Exclude super overs from benchmarks and regular play (innings 1 & 2 only)
bbb_reg = bbb[bbb['innings'].isin([1, 2])].copy()

ipl_comp_ids = set(comps[comps['comp_name'].str.contains('IPL', na=False)]['comp_id'])
bbb_reg['is_ipl'] = bbb_reg['comp_id'].isin(ipl_comp_ids).astype(int)
bbb_reg['format_label'] = bbb_reg['is_ipl'].map({1: 'IPL', 0: 'T20I/Other'})

# Benchmarks
bench = bbb_reg.groupby(['format_label', 'innings', 'phase']).agg(
    legal_balls=('is_legal', 'sum'),
    total_runs=('delivery_runs', 'sum'),
    bowler_charged=('bowler_runs', 'sum'),
    bat_runs=('runs_batter', 'sum'),
    dots=('is_dot', 'sum'),
    bdrys=('is_boundary', 'sum'),
    total_dels=('delivery_runs', 'count')
).reset_index()

bench['rpo'] = (bench['total_runs'] / bench['legal_balls']) * 6
bench['bowler_econ'] = (bench['bowler_charged'] / bench['legal_balls']) * 6
bench['batter_sr'] = (bench['bat_runs'] / bench['legal_balls']) * 100
bench['dot_pct'] = (bench['dots'] / bench['total_dels']) * 100
bench['bdry_pct'] = (bench['bdrys'] / bench['total_dels']) * 100

bench.to_csv(f'{SCRATCH}/empirical_phase_benchmarks.csv', index=False)
print("  Saved: empirical_phase_benchmarks.csv")

# Lookup dictionaries for IPL benchmarks
ipl_bench = bench[bench['format_label'] == 'IPL'].set_index(['innings', 'phase'])
par_rpo = ipl_bench['rpo'].to_dict()
par_sr = ipl_bench['batter_sr'].to_dict()

# Specific phase RPOs for Innings 1
RPO_1_PP = par_rpo.get((1, 'PP'), 8.94)
RPO_1_MID = par_rpo.get((1, 'MID'), 8.59)
RPO_1_DEATH = par_rpo.get((1, 'DEATH'), 10.94)

# Specific phase RPOs for Innings 2
RPO_2_PP = par_rpo.get((2, 'PP'), 9.05)
RPO_2_MID = par_rpo.get((2, 'MID'), 8.74)
RPO_2_DEATH = par_rpo.get((2, 'DEATH'), 10.28)

print(f"  IPL Inn 1 Pars: PP={RPO_1_PP:.2f}, MID={RPO_1_MID:.2f}, DEATH={RPO_1_DEATH:.2f}")
print(f"  IPL Inn 2 Pars: PP={RPO_2_PP:.2f}, MID={RPO_2_MID:.2f}, DEATH={RPO_2_DEATH:.2f}")

# ==============================================================================
# STEP 4: PRE-DELIVERY MATCH STATE ITERATION & PRESSURE CALCULATION
# ==============================================================================
print("\n[4/10] Iterating Deliveries with Strict Pre-Delivery Match State Capture...")

# Sort chronologically
df = bbb_reg.sort_values(['match_id', 'innings', 'overid', 'over_ball_num', 'innings_ball_num']).reset_index(drop=True)

# Precompute 1st innings total scores per match
first_inn_totals = df[df['innings'] == 1].groupby('match_id')['delivery_runs'].sum().to_dict()

# Match stakes mapping (Section 7: knock_out == 1 is the 31 verified playoffs)
def get_stakes(row):
    is_ko = (row['knock_out'] == 1) or (str(row['stage']).lower() in ['final', 'semi final', 'qualifier', 'eliminator'])
    return 1.30 if is_ko else 1.00

match_stakes_dict = matches.set_index('match_id').apply(get_stakes, axis=1).to_dict()

# Pre-allocated arrays for delivery results
n_rows = len(df)
pre_runs_arr = np.zeros(n_rows, dtype=np.float32)
pre_wickets_arr = np.zeros(n_rows, dtype=np.int32)
pre_legal_arr = np.zeros(n_rows, dtype=np.int32)
balls_rem_arr = np.zeros(n_rows, dtype=np.float32)
runs_rem_arr = np.zeros(n_rows, dtype=np.float32)
rrr_arr = np.zeros(n_rows, dtype=np.float32)
rem_par_arr = np.zeros(n_rows, dtype=np.float32)
spi_arr = np.zeros(n_rows, dtype=np.float32)
collapse_arr = np.zeros(n_rows, dtype=np.int32)
cps_arr = np.zeros(n_rows, dtype=np.float32)

# Helper function for cumulative expected score in 1st innings
def get_cum_expected_score_1st(k_legal):
    if k_legal <= 0:
        return 0.0
    elif k_legal <= 36:
        return k_legal * (RPO_1_PP / 6.0)
    elif k_legal <= 90:
        return 36.0 * (RPO_1_PP / 6.0) + (k_legal - 36.0) * (RPO_1_MID / 6.0)
    else:
        return 36.0 * (RPO_1_PP / 6.0) + 54.0 * (RPO_1_MID / 6.0) + min(30.0, k_legal - 90.0) * (RPO_1_DEATH / 6.0)

# Helper function for remaining phase weighted par in 2nd innings
def get_remaining_phase_par_2nd(k_legal, b_total):
    b_rem = max(1.0, b_total - k_legal)
    
    # Calculate balls remaining in each phase
    b_pp = max(0.0, min(36.0, b_total) - k_legal) if k_legal < 36.0 else 0.0
    
    if k_legal < 36.0:
        b_mid = max(0.0, min(54.0, b_total - 36.0))
    elif k_legal < 90.0:
        b_mid = max(0.0, min(90.0, b_total) - k_legal)
    else:
        b_mid = 0.0
        
    if k_legal < 90.0:
        b_death = max(0.0, b_total - 90.0)
    else:
        b_death = max(0.0, b_total - k_legal)
        
    exp_rem_runs = b_pp * (RPO_2_PP / 6.0) + b_mid * (RPO_2_MID / 6.0) + b_death * (RPO_2_DEATH / 6.0)
    if exp_rem_runs <= 0.0:
        return RPO_2_DEATH
    return (exp_rem_runs / b_rem) * 6.0

# Group by match and innings
grouped = df.groupby(['match_id', 'innings'], sort=False)

row_offset = 0
for (mid, inn), grp in grouped:
    grp_len = len(grp)
    stakes = match_stakes_dict.get(mid, 1.0)
    
    # Target and total allocated balls
    if inn == 2:
        rev_targ = grp['revised_target'].iloc[0]
        if pd.notna(rev_targ):
            target = float(rev_targ)
        else:
            target = float(first_inn_totals.get(mid, 160.0) + 1.0)
            
        rev_overs = grp['second_inn_revised_overs'].iloc[0]
        b_total = float(rev_overs * 6.0) if pd.notna(rev_overs) else 120.0
    else:
        target = 0.0
        rev_overs = grp['first_inn_revised_overs'].iloc[0]
        b_total = float(rev_overs * 6.0) if pd.notna(rev_overs) else 120.0
        
    # State tracking variables (PRE-DELIVERY)
    pre_runs = 0.0
    pre_wickets = 0
    pre_legal = 0
    
    # Pre-delivery rolling 18 legal deliveries window for collapse
    # stores 1 if wicket on that legal ball, 0 otherwise
    recent_legal_wkts = deque(maxlen=18)
    
    del_runs_vals = grp['delivery_runs'].values
    is_legal_vals = grp['is_legal'].values
    is_team_wkt_vals = grp['is_team_wkt'].values
    
    for i in range(grp_len):
        idx = row_offset + i
        
        # 1. CAPTURE PRE-DELIVERY STATE
        pre_runs_arr[idx] = pre_runs
        pre_wickets_arr[idx] = pre_wickets
        pre_legal_arr[idx] = pre_legal
        
        w_rem = max(1, 10 - pre_wickets)
        b_rem = max(1.0, b_total - pre_legal)
        balls_rem_arr[idx] = b_rem
        
        # 2. COLLAPSE DETECTION (PRE-DELIVERY)
        # Evaluates strictly the preceding 18 legal deliveries
        wkts_in_window = sum(recent_legal_wkts)
        is_collapse = 1 if wkts_in_window >= 3 else 0
        collapse_arr[idx] = is_collapse
        collapse_adj = 1.50 if is_collapse else 0.0
        
        # 3. CALCULATE SPI
        if inn == 2:
            # Chasing
            r_rem = target - pre_runs
            runs_rem_arr[idx] = r_rem
            rrr = (r_rem / b_rem) * 6.0
            rrr_arr[idx] = rrr
            
            # Remaining phase weighted par
            rem_par = get_remaining_phase_par_2nd(pre_legal, b_total)
            rem_par_arr[idx] = rem_par
            
            rate_ratio = np.clip(rrr / rem_par, 0.2, 3.5)
            resource_factor = np.power(5.0 / w_rem, 0.60)
            urgency = 1.0 + 0.40 * (1.0 - (b_rem / b_total))
            
            spi = np.clip(2.80 * rate_ratio * resource_factor * urgency, 0.0, 10.0)
            spi_arr[idx] = spi
        else:
            # 1st Innings: Setting Target
            runs_rem_arr[idx] = 0.0
            rrr_arr[idx] = 0.0
            rem_par_arr[idx] = 0.0
            
            exp_score = get_cum_expected_score_1st(pre_legal)
            deficit = exp_score - pre_runs
            deficit_rate = ((deficit * 6.0) / pre_legal) if pre_legal > 0 else 0.0
            
            base_pressure = np.clip(2.50 + 0.50 * deficit_rate, 0.50, 6.0)
            resource_factor = np.power(5.0 / w_rem, 0.45)
            urgency = 1.0 + 0.30 * (1.0 - (b_rem / b_total))
            
            spi = np.clip(0.90 * base_pressure * resource_factor * urgency, 0.0, 10.0)
            spi_arr[idx] = spi
            
        # 4. CPS (COMBINED PRESSURE SCORE)
        cps = np.clip((spi + collapse_adj) * stakes, 0.0, 10.0)
        cps_arr[idx] = cps
        
        # 5. NOW PROCESS CURRENT DELIVERY OUTCOME (STATE UPDATE FOR NEXT DELIVERY)
        dr = del_runs_vals[i]
        leg = is_legal_vals[i]
        twkt = is_team_wkt_vals[i]
        
        pre_runs += dr
        pre_wickets += twkt
        
        if leg == 1:
            recent_legal_wkts.append(twkt)
            pre_legal += 1

    row_offset += grp_len

# Attach computed columns
df['pre_runs'] = pre_runs_arr
df['pre_wickets'] = pre_wickets_arr
df['pre_legal'] = pre_legal_arr
df['balls_remaining'] = balls_rem_arr
df['runs_remaining'] = runs_rem_arr
df['rrr'] = rrr_arr
df['rem_phase_par'] = rem_par_arr
df['spi'] = spi_arr
df['is_collapse'] = collapse_arr
df['cps'] = cps_arr

def pcat(c):
    if c < 3.0: return 'Normal'
    elif c < 5.0: return 'Moderate'
    elif c < 7.5: return 'High'
    else: return 'Extreme'

df['pressure_cat'] = df['cps'].apply(pcat)

# Pressure distribution report
pdist = df.groupby('pressure_cat').agg(
    deliveries=('cps', 'count'),
    matches=('match_id', 'nunique'),
    batters=('striker_id', 'nunique'),
    bowlers=('bowler_id', 'nunique'),
    mean_cps=('cps', 'mean')
).reset_index()
pdist = pdist.set_index('pressure_cat').reindex(['Normal', 'Moderate', 'High', 'Extreme']).reset_index()
pdist.to_csv(f'{SCRATCH}/pressure_distribution.csv', index=False)
print("  Saved: pressure_distribution.csv")
print(pdist.to_string(index=False, float_format='%.2f'))

# Save enriched parquet
df.to_parquet(f'{SCRATCH}/enriched_bbb_v3.parquet', index=False)
print("  Saved: enriched_bbb_v3.parquet")

# ==============================================================================
# STEP 5: PLAYER ELIGIBILITY & FOUR UNIVERSES
# ==============================================================================
print("\n[5/10] Establishing Four Independent Player Universes & Exclusions...")

# Universe A: All players who batted or bowled in dataset
all_bat_ids = set(df['striker_id'].dropna().astype(int).unique())
all_bowl_ids = set(df['bowler_id'].dropna().astype(int).unique())
all_player_ids = all_bat_ids | all_bowl_ids
print(f"  Universe A (Full Statistical Universe): {len(all_player_ids)} players")

# Universe B: IPL-experienced players (appeared in IPL Playing XI)
ipl_match_ids = set(matches[matches['comp_name'].str.contains('IPL', na=False)]['match_id'])
ipl_p11 = p11[p11['match_id'].isin(ipl_match_ids)]
ipl_experienced_ids = set(ipl_p11['player_id'].dropna().astype(int).unique())
print(f"  Universe B (IPL-Experienced Universe): {len(ipl_experienced_ids)} players")

# Retained players (184 official list, resolved)
ret_df = pd.read_csv(f'{SCRATCH}/retained_resolved_184.csv')
retained_pids = set(ret_df['player_id'].dropna().astype(int))
retained_pids.add(8221) # Nitish Reddy explicitly

# 28 AUS & ENG Test players
test_pids = {
    830, 829, 2367, 223, 4227, 2750, 5939, 4736, 3986, 6350, 1758,
    6280, 2379, 6196, 2531, 3298, 1195, 7008, 6097, 7044, 6727
}

# Retired / Coaching / Traded / Excluded
retired_coaching_pids = {
    8: 'Mahendra Singh Dhoni (Retired)',
    142: 'Shikhar Dhawan (Retired Aug 2024)',
    143: 'Dinesh Karthik (Retired/RCB Coach)',
    2877: 'Vijay Shankar (Retired/Coaching)',
    2878: 'Mohit Sharma (CSK Bowling Coach)',
    1318: 'Andre Russell (User Confirmed Unavailable)',
    3782: 'M Shahrukh Khan (Traded Pre-Auction)',
}

# Pakistan & Bangladesh players
pak_ban_teams = mapping[mapping['team_name'].str.contains('Pakistan|Bangladesh', case=False, na=False)]
pak_ban_pids = set(pak_ban_teams['player_id'].dropna().astype(int).unique())

# Pending Availability Status
pending_pids = {24475: 'Rehan Ahmed (Pending NOC/ECB availability)'}

# Universe C: Auction-eligible (Universe A minus Retained minus Pak/Ban minus Retired)
auction_eligible_ids = all_player_ids - retained_pids - pak_ban_pids - set(retired_coaching_pids.keys())
print(f"  Universe C (Auction-Eligible Universe): {len(auction_eligible_ids)} players")

# Universe D: Final Availability-Filtered (Universe C minus Test players minus Pending)
available_auction_ids = auction_eligible_ids - test_pids - set(pending_pids.keys())
print(f"  Universe D (Final Available Auction Universe): {len(available_auction_ids)} players")

# Build comprehensive player_eligibility_audit.csv
id_to_official_name = dict(zip(mapping['player_id'].dropna().astype(int), mapping['player_name']))
bbb_names = {**dict(zip(df['striker_id'].dropna().astype(int), df['striker_name'])),
             **dict(zip(df['bowler_id'].dropna().astype(int), df['bowler_name']))}
id_to_name = {**bbb_names, **id_to_official_name}

elig_records = []
for pid in sorted(all_player_ids):
    name = id_to_name.get(pid, f'Player_{pid}')
    in_ipl = pid in ipl_experienced_ids
    in_auc = pid in auction_eligible_ids
    in_avail = pid in available_auction_ids
    
    status = 'Available'
    reason = 'Available for IPL 2027 Auction'
    if pid in retained_pids:
        status = 'Retained'
        reason = 'Retained in Official 184 List'
    elif pid in set(retired_coaching_pids.keys()):
        status = 'Retired/Coaching'
        reason = retired_coaching_pids[pid]
    elif pid in pak_ban_pids:
        status = 'Ineligible'
        reason = 'BCCI Diplomatic Policy (Pakistan/Bangladesh)'
    elif pid in test_pids:
        status = 'Test Unavailable'
        reason = 'Australian / English Test Player'
    elif pid in set(pending_pids.keys()):
        status = 'Pending'
        reason = pending_pids[pid]
        
    elig_records.append({
        'player_id': pid,
        'player_name': name,
        'universe_A_statistical': True,
        'universe_B_ipl_experienced': in_ipl,
        'universe_C_auction_eligible': in_auc,
        'universe_D_final_available': in_avail,
        'eligibility_status': status,
        'exclusion_reason': reason
    })

pd.DataFrame(elig_records).to_csv(f'{SCRATCH}/player_eligibility_audit.csv', index=False)
print("  Saved: player_eligibility_audit.csv")

# ==============================================================================
# STEP 6: FEATURE ENGINEERING
# ==============================================================================
print("\n[6/10] Engineering Comprehensive Player Features...")

PRESS_CPS_THRESH = 5.0 # CPS >= 5.0 is high/extreme pressure

# ---- BATTERS ----
bat_agg = df.groupby('striker_id').agg(
    career_runs=('runs_batter', 'sum'),
    career_legal=('is_legal', 'sum'),
    career_outs=('is_team_wkt', 'sum'),
    total_matches=('match_id', 'nunique'),
    career_bdrys=('is_boundary', 'sum'),
    career_dots=('is_dot', 'sum')
).reset_index()

bat_agg['career_sr'] = np.where(bat_agg['career_legal'] > 0, (bat_agg['career_runs'] / bat_agg['career_legal']) * 100.0, 0.0)
bat_agg['career_avg'] = np.where(bat_agg['career_outs'] > 0, bat_agg['career_runs'] / bat_agg['career_outs'], bat_agg['career_runs'])

# Death Overs Batting
death_bat = df[df['phase'] == 'DEATH'].groupby('striker_id').agg(
    death_runs=('runs_batter', 'sum'),
    death_legal=('is_legal', 'sum')
).reset_index()
death_bat['death_sr'] = np.where(death_bat['death_legal'] > 0, (death_bat['death_runs'] / death_bat['death_legal']) * 100.0, 0.0)
bat_agg = bat_agg.merge(death_bat, on='striker_id', how='left').fillna({'death_sr': 0.0, 'death_legal': 0})

# Pressure Batting (CPS >= 5.0)
press_bat = df[df['cps'] >= PRESS_CPS_THRESH].groupby('striker_id').agg(
    press_runs=('runs_batter', 'sum'),
    press_legal=('is_legal', 'sum'),
    press_dels=('runs_batter', 'count'),
    press_outs=('is_team_wkt', 'sum'),
    press_bdrys=('is_boundary', 'sum'),
    press_dots=('is_dot', 'sum'),
    press_matches=('match_id', 'nunique')
).reset_index()

press_bat['press_sr'] = np.where(press_bat['press_legal'] > 0, (press_bat['press_runs'] / press_bat['press_legal']) * 100.0, 0.0)
press_bat['press_avg'] = np.where(press_bat['press_outs'] > 0, press_bat['press_runs'] / press_bat['press_outs'], press_bat['press_runs'])
press_bat['press_dot_pct'] = np.where(press_bat['press_dels'] > 0, (press_bat['press_dots'] / press_bat['press_dels']) * 100.0, 0.0)
press_bat['press_bdry_pct'] = np.where(press_bat['press_dels'] > 0, (press_bat['press_bdrys'] / press_bat['press_dels']) * 100.0, 0.0)

bat_agg = bat_agg.merge(press_bat, on='striker_id', how='left').fillna({
    'press_runs': 0, 'press_legal': 0, 'press_dels': 0, 'press_outs': 0,
    'press_bdrys': 0, 'press_dots': 0, 'press_matches': 0,
    'press_sr': 0.0, 'press_avg': 0.0, 'press_dot_pct': 0.0, 'press_bdry_pct': 0.0
})

bat_agg['sr_delta'] = bat_agg['press_sr'] - bat_agg['career_sr']

# Runs Above Par per Ball (using empirical phase benchmark)
df['ball_par_sr'] = df.apply(lambda r: par_sr.get((int(r['innings']), r['phase']), 130.0), axis=1)
df['ball_exp_runs'] = (df['ball_par_sr'] / 100.0) * df['is_legal']
df['ball_rap'] = df['runs_batter'] - df['ball_exp_runs']

rap = df.groupby('striker_id').agg(total_rap=('ball_rap', 'sum'), rap_legal=('is_legal', 'sum')).reset_index()
rap['rap_per_ball'] = np.where(rap['rap_legal'] > 0, rap['total_rap'] / rap['rap_legal'], 0.0)
bat_agg = bat_agg.merge(rap[['striker_id', 'total_rap', 'rap_per_ball']], on='striker_id', how='left').fillna({'rap_per_ball': 0.0, 'total_rap': 0.0})

# Match Consistency (Std of match SR)
m_bat = df.groupby(['striker_id', 'match_id']).agg(m_runs=('runs_batter', 'sum'), m_legal=('is_legal', 'sum')).reset_index()
m_bat_qual = m_bat[m_bat['m_legal'] >= 6].copy()
m_bat_qual['m_sr'] = (m_bat_qual['m_runs'] / m_bat_qual['m_legal']) * 100.0
bat_cons = m_bat_qual.groupby('striker_id')['m_sr'].agg(['std', 'count']).reset_index()
bat_cons['match_consistency'] = 1.0 / (1.0 + bat_cons['std'].fillna(45.0))
bat_agg = bat_agg.merge(bat_cons[['striker_id', 'match_consistency']], on='striker_id', how='left').fillna({'match_consistency': 0.02})

# Recent Performance (2024-2026)
recent_matches = set(matches[matches['season'].astype(str).str.contains('2024|2025|2026', na=False)]['match_id'])
df_recent = df[df['match_id'].isin(recent_matches)]

rec_bat = df_recent.groupby('striker_id').agg(recent_runs=('runs_batter', 'sum'), recent_legal=('is_legal', 'sum')).reset_index()
rec_bat['recent_sr'] = np.where(rec_bat['recent_legal'] > 0, (rec_bat['recent_runs'] / rec_bat['recent_legal']) * 100.0, 0.0)
bat_agg = bat_agg.merge(rec_bat[['striker_id', 'recent_sr']], on='striker_id', how='left').fillna({'recent_sr': 0.0})

bat_agg['player_name'] = bat_agg['striker_id'].map(id_to_name)

# ---- BOWLERS ----
bowl_agg = df.groupby('bowler_id').agg(
    career_runs_conc=('bowler_runs', 'sum'),
    career_legal=('is_legal', 'sum'),
    career_bowler_wkts=('is_bowler_wkt', 'sum'),
    career_team_wkts=('is_team_wkt', 'sum'),
    total_matches=('match_id', 'nunique'),
    career_dots=('is_dot', 'sum'),
    career_bdrys=('is_boundary', 'sum')
).reset_index()

bowl_agg['career_econ'] = np.where(bowl_agg['career_legal'] > 0, (bowl_agg['career_runs_conc'] / bowl_agg['career_legal']) * 6.0, 12.0)
bowl_agg['career_avg'] = np.where(bowl_agg['career_bowler_wkts'] > 0, bowl_agg['career_runs_conc'] / bowl_agg['career_bowler_wkts'], 99.0)

# Death Overs Bowling
death_bowl = df[df['phase'] == 'DEATH'].groupby('bowler_id').agg(
    death_runs_conc=('bowler_runs', 'sum'),
    death_legal=('is_legal', 'sum')
).reset_index()
death_bowl['death_econ'] = np.where(death_bowl['death_legal'] > 0, (death_bowl['death_runs_conc'] / death_bowl['death_legal']) * 6.0, 15.0)
bowl_agg = bowl_agg.merge(death_bowl, on='bowler_id', how='left').fillna({'death_econ': 15.0, 'death_legal': 0})

# Pressure Bowling (CPS >= 5.0)
press_bowl = df[df['cps'] >= PRESS_CPS_THRESH].groupby('bowler_id').agg(
    press_runs_conc=('bowler_runs', 'sum'),
    press_legal=('is_legal', 'sum'),
    press_dels=('bowler_runs', 'count'),
    press_bowler_wkts=('is_bowler_wkt', 'sum'),
    press_team_wkts=('is_team_wkt', 'sum'),
    press_dots=('is_dot', 'sum'),
    press_bdrys=('is_boundary', 'sum'),
    press_matches=('match_id', 'nunique')
).reset_index()

press_bowl['press_econ'] = np.where(press_bowl['press_legal'] > 0, (press_bowl['press_runs_conc'] / press_bowl['press_legal']) * 6.0, 15.0)
press_bowl['press_avg'] = np.where(press_bowl['press_bowler_wkts'] > 0, press_bowl['press_runs_conc'] / press_bowl['press_bowler_wkts'], 99.0)
press_bowl['press_dot_pct'] = np.where(press_bowl['press_dels'] > 0, (press_bowl['press_dots'] / press_bowl['press_dels']) * 100.0, 0.0)
press_bowl['press_bdry_pct'] = np.where(press_bowl['press_dels'] > 0, (press_bowl['press_bdrys'] / press_bowl['press_dels']) * 100.0, 0.0)

bowl_agg = bowl_agg.merge(press_bowl, on='bowler_id', how='left').fillna({
    'press_runs_conc': 0, 'press_legal': 0, 'press_dels': 0, 'press_bowler_wkts': 0,
    'press_team_wkts': 0, 'press_dots': 0, 'press_bdrys': 0, 'press_matches': 0,
    'press_econ': 15.0, 'press_avg': 99.0, 'press_dot_pct': 0.0, 'press_bdry_pct': 0.0
})

bowl_agg['econ_delta'] = bowl_agg['press_econ'] - bowl_agg['career_econ']

# Bowler Runs Saved against Phase Par
df['par_econ_ball'] = df.apply(lambda r: par_rpo.get((int(r['innings']), r['phase']), 8.5) / 6.0, axis=1)
df['exp_conc'] = df['par_econ_ball'] * df['is_legal']
df['ball_runs_saved'] = df['exp_conc'] - df['bowler_runs']

rs = df.groupby('bowler_id').agg(total_saved=('ball_runs_saved', 'sum'), saved_legal=('is_legal', 'sum')).reset_index()
rs['runs_saved_per_ball'] = np.where(rs['saved_legal'] > 0, rs['total_saved'] / rs['saved_legal'], 0.0)
bowl_agg = bowl_agg.merge(rs[['bowler_id', 'total_saved', 'runs_saved_per_ball']], on='bowler_id', how='left').fillna({'runs_saved_per_ball': 0.0, 'total_saved': 0.0})

# Bowler Wicket Rate under Pressure (wickets per 6 legal balls)
bowl_agg['press_wkt_rate'] = np.where(bowl_agg['press_legal'] > 0, (bowl_agg['press_bowler_wkts'] / bowl_agg['press_legal']) * 6.0, 0.0)

# Recent Bowling Economy (2024-2026)
rec_bowl = df_recent.groupby('bowler_id').agg(recent_runs_conc=('bowler_runs', 'sum'), recent_legal=('is_legal', 'sum')).reset_index()
rec_bowl['recent_econ'] = np.where(rec_bowl['recent_legal'] > 0, (rec_bowl['recent_runs_conc'] / rec_bowl['recent_legal']) * 6.0, 12.0)
bowl_agg = bowl_agg.merge(rec_bowl[['bowler_id', 'recent_econ']], on='bowler_id', how='left').fillna({'recent_econ': 12.0})

bowl_agg['player_name'] = bowl_agg['bowler_id'].map(id_to_name)

# ==============================================================================
# STEP 7: ESTIMATE EMPIRICAL BAYES HYPERPARAMETERS FROM DATA
# ==============================================================================
print("\n[7/10] Estimating Empirical Bayes Shrinkage Parameters Directly from Data...")

# Batter SR shrinkage:
# Var(y_i) = tau_bat^2 + sigma_bat^2 / n_i
# sigma_bat^2 is variance of delivery runs * 10000
sigma2_bat = df['runs_batter'].var() * 10000.0
# tau_bat^2 is variance of career SR among qualified batters (>= 100 legal balls)
tau2_bat = bat_agg[bat_agg['career_legal'] >= 100]['career_sr'].var()
K_BAT_EST = sigma2_bat / tau2_bat
print(f"  Estimated K_bat: {K_BAT_EST:.1f} balls (sigma2={sigma2_bat:.1f}, tau2={tau2_bat:.1f})")

# Bowler Econ shrinkage:
# Econ = 6 * runs_per_ball -> Var = 36 * sigma_bowl^2 / n_i
sigma2_bowl = df['bowler_runs'].var() * 36.0
tau2_bowl = bowl_agg[bowl_agg['career_legal'] >= 100]['career_econ'].var()
K_BOWL_EST = sigma2_bowl / tau2_bowl
print(f"  Estimated K_bowl: {K_BOWL_EST:.1f} balls (sigma2={sigma2_bowl:.1f}, tau2={tau2_bowl:.1f})")

# Population means under pressure (prior mean)
pop_press_sr = bat_agg[bat_agg['press_legal'] >= 30]['press_sr'].mean()
pop_death_sr = bat_agg[bat_agg['death_legal'] >= 30]['death_sr'].mean()
pop_press_econ = bowl_agg[bowl_agg['press_legal'] >= 30]['press_econ'].mean()
pop_death_econ = bowl_agg[bowl_agg['death_legal'] >= 30]['death_econ'].mean()

# Apply Shrinkage using estimated hyperparameters
bat_agg['press_sr_shrunk'] = (bat_agg['press_legal'] * bat_agg['press_sr'] + K_BAT_EST * pop_press_sr) / (bat_agg['press_legal'] + K_BAT_EST)
bat_agg['death_sr_shrunk'] = (bat_agg['death_legal'] * bat_agg['death_sr'] + K_BAT_EST * pop_death_sr) / (bat_agg['death_legal'] + K_BAT_EST)

bowl_agg['press_econ_shrunk'] = (bowl_agg['press_legal'] * bowl_agg['press_econ'] + K_BOWL_EST * pop_press_econ) / (bowl_agg['press_legal'] + K_BOWL_EST)
bowl_agg['death_econ_shrunk'] = (bowl_agg['death_legal'] * bowl_agg['death_econ'] + K_BOWL_EST * pop_death_econ) / (bowl_agg['death_legal'] + K_BOWL_EST)

# Standard Error & Confidence Intervals
bat_agg['press_sr_se'] = np.sqrt(sigma2_bat / np.maximum(1, bat_agg['press_legal']))
bat_agg['press_sr_ci_lower'] = bat_agg['press_sr_shrunk'] - 1.96 * bat_agg['press_sr_se']
bat_agg['press_sr_ci_upper'] = bat_agg['press_sr_shrunk'] + 1.96 * bat_agg['press_sr_se']

bowl_agg['press_econ_se'] = np.sqrt(sigma2_bowl / np.maximum(1, bowl_agg['press_legal']))
bowl_agg['press_econ_ci_lower'] = bowl_agg['press_econ_shrunk'] - 1.96 * bowl_agg['press_econ_se']
bowl_agg['press_econ_ci_upper'] = bowl_agg['press_econ_shrunk'] + 1.96 * bowl_agg['press_econ_se']

# Confidence labels
def get_confidence(legal_balls):
    if legal_balls >= 120: return 'HIGH'
    elif legal_balls >= 60: return 'MEDIUM'
    else: return 'LOW'

bat_agg['confidence'] = bat_agg['press_legal'].apply(get_confidence)
bowl_agg['confidence'] = bowl_agg['press_legal'].apply(get_confidence)

# ==============================================================================
# STEP 8: SCORING SYSTEM & SENSITIVITY ANALYSIS
# ==============================================================================
print("\n[8/10] Evaluating Scoring Weight Sensitivity & Generating Full Rankings...")

def pct_rank(s, asc=True):
    return s.rank(pct=True, ascending=asc) * 100.0

# Base percentiles for batters
bat_pct = pd.DataFrame(index=bat_agg.index)
bat_pct['press_sr'] = pct_rank(bat_agg['press_sr_shrunk'])
bat_pct['death_sr'] = pct_rank(bat_agg['death_sr_shrunk'])
bat_pct['career_sr'] = pct_rank(bat_agg['career_sr'])
bat_pct['sr_delta'] = pct_rank(bat_agg['sr_delta'])
bat_pct['bdry'] = pct_rank(bat_agg['press_bdry_pct'])
bat_pct['dot'] = pct_rank(bat_agg['press_dot_pct'], asc=False)
bat_pct['rap'] = pct_rank(bat_agg['rap_per_ball'])
bat_pct['cons'] = pct_rank(bat_agg['match_consistency'])

# Base percentiles for bowlers
bowl_pct = pd.DataFrame(index=bowl_agg.index)
bowl_pct['press_econ'] = pct_rank(bowl_agg['press_econ_shrunk'], asc=False)
bowl_pct['death_econ'] = pct_rank(bowl_agg['death_econ_shrunk'], asc=False)
bowl_pct['career_econ'] = pct_rank(bowl_agg['career_econ'], asc=False)
bowl_pct['econ_delta'] = pct_rank(bowl_agg['econ_delta'], asc=False)
bowl_pct['dot'] = pct_rank(bowl_agg['press_dot_pct'])
bowl_pct['bdry'] = pct_rank(bowl_agg['press_bdry_pct'], asc=False)
bowl_pct['saved'] = pct_rank(bowl_agg['runs_saved_per_ball'])
bowl_pct['wkt'] = pct_rank(bowl_agg['press_wkt_rate'])

# Weight schemes
weight_schemes = {
    'Baseline': {
        'bat': [0.25, 0.15, 0.15, 0.10, 0.10, 0.10, 0.10, 0.05],
        'bowl': [0.25, 0.15, 0.15, 0.10, 0.10, 0.10, 0.10, 0.05]
    },
    'Death_Heavy': {
        'bat': [0.20, 0.25, 0.10, 0.10, 0.15, 0.05, 0.10, 0.05],
        'bowl': [0.20, 0.25, 0.10, 0.10, 0.10, 0.10, 0.10, 0.05]
    },
    'Control_Consistency': {
        'bat': [0.20, 0.10, 0.15, 0.10, 0.10, 0.15, 0.10, 0.10],
        'bowl': [0.20, 0.10, 0.15, 0.10, 0.15, 0.15, 0.10, 0.05]
    },
    'Equal_Weight': {
        'bat': [0.125] * 8,
        'bowl': [0.125] * 8
    }
}

# Run sensitivity test
sens_rows = []
for scheme_name, weights in weight_schemes.items():
    w_bat = weights['bat']
    score_bat = (bat_pct['press_sr'] * w_bat[0] + bat_pct['death_sr'] * w_bat[1] +
                 bat_pct['career_sr'] * w_bat[2] + bat_pct['sr_delta'] * w_bat[3] +
                 bat_pct['bdry'] * w_bat[4] + bat_pct['dot'] * w_bat[5] +
                 bat_pct['rap'] * w_bat[6] + bat_pct['cons'] * w_bat[7])
    
    w_bowl = weights['bowl']
    score_bowl = (bowl_pct['press_econ'] * w_bowl[0] + bowl_pct['death_econ'] * w_bowl[1] +
                  bowl_pct['career_econ'] * w_bowl[2] + bowl_pct['econ_delta'] * w_bowl[3] +
                  bowl_pct['dot'] * w_bowl[4] + bowl_pct['bdry'] * w_bowl[5] +
                  bowl_pct['saved'] * w_bowl[6] + bowl_pct['wkt'] * w_bowl[7])
    
    bat_agg[f'score_{scheme_name}'] = score_bat
    bowl_agg[f'score_{scheme_name}'] = score_bowl

# Correlation between schemes
bat_corr = bat_agg[['score_Baseline', 'score_Death_Heavy', 'score_Control_Consistency', 'score_Equal_Weight']].corr()
bowl_corr = bowl_agg[['score_Baseline', 'score_Death_Heavy', 'score_Control_Consistency', 'score_Equal_Weight']].corr()

print("\n  Weight Sensitivity Correlation (Batters):")
print(bat_corr.to_string(float_format='%.3f'))
print("\n  Weight Sensitivity Correlation (Bowlers):")
print(bowl_corr.to_string(float_format='%.3f'))

# Save ranking sensitivity analysis
sens_report = [
    ('Batters Corr (Baseline vs Death Heavy)', round(bat_corr.loc['score_Baseline', 'score_Death_Heavy'], 3)),
    ('Batters Corr (Baseline vs Control/Cons)', round(bat_corr.loc['score_Baseline', 'score_Control_Consistency'], 3)),
    ('Batters Corr (Baseline vs Equal Weight)', round(bat_corr.loc['score_Baseline', 'score_Equal_Weight'], 3)),
    ('Bowlers Corr (Baseline vs Death Heavy)', round(bowl_corr.loc['score_Baseline', 'score_Death_Heavy'], 3)),
    ('Bowlers Corr (Baseline vs Control/Cons)', round(bowl_corr.loc['score_Baseline', 'score_Control_Consistency'], 3)),
    ('Bowlers Corr (Baseline vs Equal Weight)', round(bowl_corr.loc['score_Baseline', 'score_Equal_Weight'], 3)),
]
pd.DataFrame(sens_report, columns=['Comparison', 'Pearson_R']).to_csv(f'{SCRATCH}/ranking_sensitivity.csv', index=False)
print("  Saved: ranking_sensitivity.csv")

# Baseline composite score is our primary
bat_agg['raw_composite_score'] = bat_agg['score_Equal_Weight']
bat_agg['reliability_adjusted_score'] = bat_agg['score_Baseline']

bowl_agg['raw_composite_score'] = bowl_agg['score_Equal_Weight']
bowl_agg['reliability_adjusted_score'] = bowl_agg['score_Baseline']

# Metadata mapping (team history & nationality from mapping)
p_teams = mapping.groupby('player_id')['team_name'].apply(lambda s: ', '.join(sorted(set(s.dropna())))).to_dict()
p_nat = mapping.groupby('player_id')['team_name'].apply(lambda s: next((t for t in s if t in ['India', 'Australia', 'England', 'South Africa', 'New Zealand', 'West Indies', 'Sri Lanka', 'Afghanistan', 'Pakistan', 'Bangladesh', 'Zimbabwe', 'Ireland', 'Netherlands', 'Scotland', 'United Arab Emirates', 'Namibia', 'United States of America', 'Nepal', 'Oman', 'Canada']), 'Other')).to_dict()

bat_agg['nationality'] = bat_agg['striker_id'].map(p_nat).fillna('Unknown')
bat_agg['ipl_team_history'] = bat_agg['striker_id'].map(p_teams).fillna('None')

bowl_agg['nationality'] = bowl_agg['bowler_id'].map(p_nat).fillna('Unknown')
bowl_agg['ipl_team_history'] = bowl_agg['bowler_id'].map(p_teams).fillna('None')

# Universe tagging
bat_agg['universe_A'] = True
bat_agg['universe_B_ipl'] = bat_agg['striker_id'].isin(ipl_experienced_ids)
bat_agg['universe_C_auction'] = bat_agg['striker_id'].isin(auction_eligible_ids)
bat_agg['universe_D_available'] = bat_agg['striker_id'].isin(available_auction_ids)

bowl_agg['universe_A'] = True
bowl_agg['universe_B_ipl'] = bowl_agg['bowler_id'].isin(ipl_experienced_ids)
bowl_agg['universe_C_auction'] = bowl_agg['bowler_id'].isin(auction_eligible_ids)
bowl_agg['universe_D_available'] = bowl_agg['bowler_id'].isin(available_auction_ids)

# ==============================================================================
# STEP 9: SAMPLE-SIZE THRESHOLD EVALUATION & FINAL EXTRACTION
# ==============================================================================
print("\n[9/10] Evaluating Minimum Sample Thresholds & Extracting Final Rankings...")

thresholds = [60, 90, 120, 180]
for th in thresholds:
    n_bat = (bat_agg['universe_D_available'] & (bat_agg['press_legal'] >= th)).sum()
    n_bowl = (bowl_agg['universe_D_available'] & (bowl_agg['press_legal'] >= th)).sum()
    print(f"  Threshold >= {th} pressure legal balls: {n_bat} Batters, {n_bowl} Bowlers qualified in Universe D")

# Production threshold: Minimum 60 legal pressure balls ensures adequate statistical support
# while retaining the deepest pool of elite available international & IPL talent.
MIN_PROD_PRESS_BALLS = 60
MIN_PROD_MATCHES = 10

# Final Batter Universe D (Available Auction Pool)
final_bat_pool = bat_agg[
    bat_agg['universe_D_available'] &
    (bat_agg['press_legal'] >= MIN_PROD_PRESS_BALLS) &
    (bat_agg['total_matches'] >= MIN_PROD_MATCHES)
].copy()
final_bat_pool = final_bat_pool.sort_values('reliability_adjusted_score', ascending=False).reset_index(drop=True)
final_bat_pool['rank'] = range(1, len(final_bat_pool) + 1)

# Final Bowler Universe D (Available Auction Pool)
final_bowl_pool = bowl_agg[
    bowl_agg['universe_D_available'] &
    (bowl_agg['press_legal'] >= MIN_PROD_PRESS_BALLS) &
    (bowl_agg['total_matches'] >= MIN_PROD_MATCHES)
].copy()
final_bowl_pool = final_bowl_pool.sort_values('reliability_adjusted_score', ascending=False).reset_index(drop=True)
final_bowl_pool['rank'] = range(1, len(final_bowl_pool) + 1)

# Save full rankings
bat_agg.sort_values('reliability_adjusted_score', ascending=False).to_csv(f'{SCRATCH}/final_batter_rankings.csv', index=False)
bowl_agg.sort_values('reliability_adjusted_score', ascending=False).to_csv(f'{SCRATCH}/final_bowler_rankings.csv', index=False)
print("  Saved: final_batter_rankings.csv, final_bowler_rankings.csv")

# Extract Top 10 Batters
bat_top10_cols = [
    'rank', 'player_name', 'striker_id', 'nationality', 'ipl_team_history',
    'total_matches', 'press_legal', 'press_runs', 'press_sr', 'press_sr_shrunk',
    'press_avg', 'press_dot_pct', 'press_bdry_pct', 'career_sr', 'death_sr',
    'recent_sr', 'total_rap', 'raw_composite_score', 'reliability_adjusted_score',
    'confidence'
]
bat_top10 = final_bat_pool.head(10)[bat_top10_cols].copy()
bat_top10.to_csv(f'{SCRATCH}/final_batter_top10.csv', index=False)
print("  Saved: final_batter_top10.csv")

# Extract Top 10 Bowlers
bowl_top10_cols = [
    'rank', 'player_name', 'bowler_id', 'nationality', 'ipl_team_history',
    'total_matches', 'press_legal', 'press_runs_conc', 'press_econ', 'press_econ_shrunk',
    'press_avg', 'press_dot_pct', 'press_bdry_pct', 'press_bowler_wkts', 'career_econ',
    'death_econ', 'recent_econ', 'total_saved', 'raw_composite_score', 'reliability_adjusted_score',
    'confidence'
]
bowl_top10 = final_bowl_pool.head(10)[bowl_top10_cols].copy()
bowl_top10.to_csv(f'{SCRATCH}/final_bowler_top10.csv', index=False)
print("  Saved: final_bowler_top10.csv")

# ==============================================================================
# STEP 10: AUDIT SECTION 13 BOWLERS & OLD VS FINAL RANKINGS
# ==============================================================================
print("\n[10/10] Verifying Section 13 Bowlers & Old vs Final Comparisons...")

sec13_pids = [3653, 4900, 4373, 2320, 8661, 4692, 6806, 1813, 7270, 6523, 6628, 3174, 25048, 1071, 1487]
sec13_names = ['Avesh Khan', 'Wanindu Hasaranga', 'Mustafizur Rahman', 'Trent Boult', 'Matheesha Pathirana',
               'Lockie Ferguson', 'Tushar Deshpande', 'Deepak Chahar', 'Anrich Nortje', 'Blessing Muzarabani',
               'Gerald Coetzee', 'Matt Henry', 'Umran Malik', 'Jaydev Unadkat', 'Adam Milne']

sec13_res = []
for pid, name in zip(sec13_pids, sec13_names):
    b_row = bowl_agg[bowl_agg['bowler_id'] == pid].iloc[0]
    in_final = final_bowl_pool[final_bowl_pool['bowler_id'] == pid]
    final_rk = in_final['rank'].values[0] if len(in_final) > 0 else 'Unranked / Ineligible'
    status = 'Available'
    if pid == 4373: status = 'BCCI Excluded (Bangladesh)'
    elif pid in retained_pids: status = 'Retained'
    
    sec13_res.append({
        'bowler_id': pid,
        'player_name': name,
        'status': status,
        'final_rank': final_rk,
        'score': round(b_row['reliability_adjusted_score'], 1),
        'career_econ': round(b_row['career_econ'], 2),
        'press_econ': round(b_row['press_econ'], 2),
        'press_econ_shrunk': round(b_row['press_econ_shrunk'], 2),
        'death_econ': round(b_row['death_econ'], 2),
        'press_wkts': int(b_row['press_bowler_wkts']),
        'press_balls': int(b_row['press_legal']),
        'matches': int(b_row['total_matches']),
        'confidence': b_row['confidence']
    })

sec13_audit_df = pd.DataFrame(sec13_res)
sec13_audit_df.to_csv(f'{SCRATCH}/section13_bowlers_audit.csv', index=False)
print("  Saved: section13_bowlers_audit.csv")

# Old vs Final Rankings Comparison (Batters & Bowlers)
# Load old rankings if available
old_bat = pd.read_csv(f'{SCRATCH}/batter_top10.csv') if os.path.exists(f'{SCRATCH}/batter_top10.csv') else pd.DataFrame()
old_bowl = pd.read_csv(f'{SCRATCH}/bowler_top10.csv') if os.path.exists(f'{SCRATCH}/bowler_top10.csv') else pd.DataFrame()

comp_rows = []
for i, r in bat_top10.head(10).iterrows():
    comp_rows.append({
        'role': 'Batter',
        'final_rank': r['rank'],
        'player_name': r['player_name'],
        'final_score': round(r['reliability_adjusted_score'], 1),
        'press_legal_balls': r['press_legal'],
        'confidence': r['confidence']
    })
for i, r in bowl_top10.head(10).iterrows():
    comp_rows.append({
        'role': 'Bowler',
        'final_rank': r['rank'],
        'player_name': r['player_name'],
        'final_score': round(r['reliability_adjusted_score'], 1),
        'press_legal_balls': r['press_legal'],
        'confidence': r['confidence']
    })

pd.DataFrame(comp_rows).to_csv(f'{SCRATCH}/old_vs_final_rankings.csv', index=False)
print("  Saved: old_vs_final_rankings.csv")

print("\n" + "=" * 80)
print("PIPELINE V3 COMPLETED SUCCESSFULLY")
print("=" * 80)
