import pandas as pd
import numpy as np
import os

SCRATCH = "C:/Users/ACER/.gemini/antigravity/brain/3babf961-9dd5-4fdf-a2cd-1010427ee970/scratch"
ROOT = "."

print("="*80)
print("RAJASTHAN ROYALS SQUAD GAP ANALYSIS & AUCTION STRATEGY — SCRIPT")
print("="*80)

# Load existing audited ranking files
bat_rankings = pd.read_csv(f"{SCRATCH}/final_batter_rankings.csv")
bowl_rankings = pd.read_csv(f"{SCRATCH}/final_bowler_rankings.csv")
elig_audit = pd.read_csv(f"{SCRATCH}/player_eligibility_audit.csv")

# ------------------------------------------------------------------------------
# 1. GENERATE RR_CONFIRMED_SQUAD_2027.csv
# ------------------------------------------------------------------------------
print("\n[1/6] Generating RR_CONFIRMED_SQUAD_2027.csv...")

rr_squad_data = [
    # Batting & WKT
    {
        'player_name': 'Yashasvi Jaiswal', 'nationality': 'India', 'is_overseas': False,
        'squad_category': 'Batting', 'primary_role': 'Opening Batter', 'batting_hand': 'Left-hand',
        'bowling_style': 'Right-arm Leg-break (Part-time)', 'ipl_experience_matches': 68,
        'acquisition_type': 'Retained', 'tactical_assessment': 'Elite aggressive Powerplay opener; attacks pace and spin alike; cornerstone of top order.'
    },
    {
        'player_name': 'Vaibhav Sooryavanshi', 'nationality': 'India', 'is_overseas': False,
        'squad_category': 'Batting', 'primary_role': 'Opening/Top-Order Batter', 'batting_hand': 'Left-hand',
        'bowling_style': 'Slow Left-arm Orthodox (Part-time)', 'ipl_experience_matches': 1,
        'acquisition_type': 'Retained', 'tactical_assessment': 'Prodigious young talent; high ceiling; developing backup opener.'
    },
    {
        'player_name': 'Dhruv Jurel', 'nationality': 'India', 'is_overseas': False,
        'squad_category': 'Wicketkeeper-Batter', 'primary_role': 'Middle-Order Batter / Wicketkeeper', 'batting_hand': 'Right-hand',
        'bowling_style': 'None', 'ipl_experience_matches': 38,
        'acquisition_type': 'Retained', 'tactical_assessment': 'Primary Indian wicketkeeper; excellent middle-overs stabilizer (No. 4/5); 168.2 Press SR; elite runner.'
    },
    {
        'player_name': 'Riyan Parag', 'nationality': 'India', 'is_overseas': False,
        'squad_category': 'Batting', 'primary_role': 'Top/Middle-Order Batter', 'batting_hand': 'Right-hand',
        'bowling_style': 'Right-arm Off-break / Leg-break', 'ipl_experience_matches': 69,
        'acquisition_type': 'Retained', 'tactical_assessment': 'Core No. 3/4 batter; proven anchor against spin with 157.7 Press SR; sixth bowling option.'
    },
    {
        'player_name': 'Aman Rao Perala', 'nationality': 'India', 'is_overseas': False,
        'squad_category': 'Batting', 'primary_role': 'Top/Middle-Order Batter', 'batting_hand': 'Right-hand',
        'bowling_style': 'Right-arm Off-break', 'ipl_experience_matches': 0,
        'acquisition_type': 'Retained', 'tactical_assessment': 'Uncapped domestic batter; bench depth for top-to-middle order.'
    },
    {
        'player_name': 'Shubham Dubey', 'nationality': 'India', 'is_overseas': False,
        'squad_category': 'Batting', 'primary_role': 'Middle-Order Power Finisher', 'batting_hand': 'Left-hand',
        'bowling_style': 'Right-arm Off-break (Part-time)', 'ipl_experience_matches': 4,
        'acquisition_type': 'Retained', 'tactical_assessment': 'Designated domestic left-hand finisher; 192.9 Press SR in limited sample; high potential but unproven at full IPL scale.'
    },
    {
        'player_name': 'Lhuan-dre Pretorius', 'nationality': 'South Africa', 'is_overseas': True,
        'squad_category': 'Wicketkeeper-Batter', 'primary_role': 'Top-Order Batter / Wicketkeeper', 'batting_hand': 'Left-hand',
        'bowling_style': 'None', 'ipl_experience_matches': 0,
        'acquisition_type': 'Retained', 'tactical_assessment': 'Emerging South Africa U19 overseas wicketkeeper-batter; developmental overseas depth.'
    },
    {
        'player_name': 'Donovan Ferreira', 'nationality': 'South Africa', 'is_overseas': True,
        'squad_category': 'Wicketkeeper-Batter', 'primary_role': 'Explosive Lower-Order Finisher / Wicketkeeper', 'batting_hand': 'Right-hand',
        'bowling_style': 'Right-arm Off-break', 'ipl_experience_matches': 4,
        'acquisition_type': 'Retained', 'tactical_assessment': 'Power-hitting finisher (164.3 career SR); versatile keeper/bowler; candidate for No. 6/7, but takes an overseas slot.'
    },
    # All-Rounders
    {
        'player_name': 'Ravindra Jadeja', 'nationality': 'India', 'is_overseas': False,
        'squad_category': 'All-Rounder', 'primary_role': 'Spin-Bowling All-Rounder', 'batting_hand': 'Left-hand',
        'bowling_style': 'Slow Left-arm Orthodox', 'ipl_experience_matches': 240,
        'acquisition_type': 'Retained', 'tactical_assessment': 'World-class Indian all-rounder; locks down 4 overs of middle spin (7.87 Econ); solid No. 6/7 bat (161.3 Press SR).'
    },
    {
        'player_name': 'Dasun Shanaka', 'nationality': 'Sri Lanka', 'is_overseas': True,
        'squad_category': 'All-Rounder', 'primary_role': 'Pace-Bowling All-Rounder', 'batting_hand': 'Right-hand',
        'bowling_style': 'Right-arm Medium', 'ipl_experience_matches': 7,
        'acquisition_type': 'Retained', 'tactical_assessment': 'Experienced international pace-bowling all-rounder; 181.9 Press SR; provides 1-2 overs of seam backup.'
    },
    # Pace
    {
        'player_name': 'Jofra Archer', 'nationality': 'England', 'is_overseas': True,
        'squad_category': 'Pace Bowler', 'primary_role': 'Express Fast Bowler', 'batting_hand': 'Right-hand',
        'bowling_style': 'Right-arm Fast', 'ipl_experience_matches': 42,
        'acquisition_type': 'Retained', 'tactical_assessment': 'Premier strike bowler; lethal in Powerplay and Death (7.07 Press Econ); fitness/workload management is primary risk.'
    },
    {
        'player_name': 'Mohammed Shami', 'nationality': 'India', 'is_overseas': False,
        'squad_category': 'Pace Bowler', 'primary_role': 'Seam & Swing Fast Bowler', 'batting_hand': 'Right-hand',
        'bowling_style': 'Right-arm Fast-Medium', 'ipl_experience_matches': 110,
        'acquisition_type': 'Traded In (from LSG)', 'tactical_assessment': 'Elite new-ball swing bowler; 6.65 Press Econ; anchors Powerplay wickets; requires death-overs tandem partner.'
    },
    {
        'player_name': 'Nandre Burger', 'nationality': 'South Africa', 'is_overseas': True,
        'squad_category': 'Pace Bowler', 'primary_role': 'Left-Arm Express Fast Bowler', 'batting_hand': 'Left-hand',
        'bowling_style': 'Left-arm Fast', 'ipl_experience_matches': 6,
        'acquisition_type': 'Retained', 'tactical_assessment': 'Hostile 145+ km/h left-arm pace; enforcer role in overs 1-10; developing death yorker execution.'
    },
    {
        'player_name': 'Sandeep Sharma', 'nationality': 'India', 'is_overseas': False,
        'squad_category': 'Pace Bowler', 'primary_role': 'Swing & Death Specialist', 'batting_hand': 'Right-hand',
        'bowling_style': 'Right-arm Medium-Fast', 'ipl_experience_matches': 127,
        'acquisition_type': 'Retained', 'tactical_assessment': 'Veteran domestic death/swing bowler; knuckle balls and change of pace; higher pressure economy (10.25 RPO) indicates need for backup.'
    },
    {
        'player_name': 'Brijesh Sharma', 'nationality': 'India', 'is_overseas': False,
        'squad_category': 'Pace Bowler', 'primary_role': 'Medium-Fast Bowler', 'batting_hand': 'Right-hand',
        'bowling_style': 'Right-arm Medium-Fast', 'ipl_experience_matches': 0,
        'acquisition_type': 'Retained', 'tactical_assessment': 'Uncapped domestic seam depth; developmental role.'
    },
    {
        'player_name': 'Sushant Mishra', 'nationality': 'India', 'is_overseas': False,
        'squad_category': 'Pace Bowler', 'primary_role': 'Left-Arm Fast-Medium Bowler', 'batting_hand': 'Left-hand',
        'bowling_style': 'Left-arm Fast-Medium', 'ipl_experience_matches': 2,
        'acquisition_type': 'Retained', 'tactical_assessment': 'Young domestic left-arm pacer; provides natural angle backup; raw at IPL level.'
    },
    {
        'player_name': 'Yash Raj Punja', 'nationality': 'India', 'is_overseas': False,
        'squad_category': 'Pace Bowler', 'primary_role': 'Medium-Fast Bowler', 'batting_hand': 'Right-hand',
        'bowling_style': 'Right-arm Medium-Fast', 'ipl_experience_matches': 0,
        'acquisition_type': 'Retained', 'tactical_assessment': 'Uncapped domestic seam prospect; bench depth.'
    },
    # Spin
    {
        'player_name': 'Ravi Bishnoi', 'nationality': 'India', 'is_overseas': False,
        'squad_category': 'Spin Bowler', 'primary_role': 'Wrist-Spin Bowler', 'batting_hand': 'Right-hand',
        'bowling_style': 'Right-arm Leg-break / Googly', 'ipl_experience_matches': 66,
        'acquisition_type': 'Retained', 'tactical_assessment': 'Frontline attacking leg-spinner; lethal googly against RH batters; controls middle overs (7-15).'
    },
    {
        'player_name': 'Manimaran Siddharth', 'nationality': 'India', 'is_overseas': False,
        'squad_category': 'Spin Bowler', 'primary_role': 'Slow Left-Arm Orthodox Bowler', 'batting_hand': 'Right-hand',
        'bowling_style': 'Slow Left-arm Orthodox', 'ipl_experience_matches': 3,
        'acquisition_type': 'Traded In (from LSG)', 'tactical_assessment': 'Accurate powerplay/middle left-arm spinner; traded in from LSG; backup for Ravindra Jadeja.'
    }
]

rr_squad_df = pd.DataFrame(rr_squad_data)
rr_squad_df.to_csv(f"{SCRATCH}/RR_CONFIRMED_SQUAD_2027.csv", index=False)
rr_squad_df.to_csv(f"{ROOT}/RR_CONFIRMED_SQUAD_2027.csv", index=False)
print("  Saved: RR_CONFIRMED_SQUAD_2027.csv (19 players)")

# ------------------------------------------------------------------------------
# 2. GENERATE RR_RELEASED_AND_TRADED_PLAYERS.csv
# ------------------------------------------------------------------------------
print("\n[2/6] Generating RR_RELEASED_AND_TRADED_PLAYERS.csv...")

rr_transfers_data = [
    {
        'player_name': 'Shimron Hetmyer', 'nationality': 'West Indies', 'is_overseas': True,
        'transaction_type': 'Released', 'previous_role': 'Middle-Order Power Finisher (No. 5/6)',
        'tactical_void_created': 'Critical middle-to-death acceleration vacancy (overs 14-20); scored 163 pressure runs at 168.2 Death SR; primary replacement priority.',
        'auction_status': 'Available in Auction (Universe D)'
    },
    {
        'player_name': 'Tushar Deshpande', 'nationality': 'India', 'is_overseas': False,
        'transaction_type': 'Released', 'previous_role': 'Indian Fast Bowler (Powerplay & Middle)',
        'tactical_void_created': 'Domestic pace depth reduced; however, arrival of Mohammed Shami upgrades frontline new-ball attack.',
        'auction_status': 'Available in Auction (Universe D)'
    },
    {
        'player_name': 'Adam Milne', 'nationality': 'New Zealand', 'is_overseas': True,
        'transaction_type': 'Released', 'previous_role': 'Overseas Express Fast Bowler',
        'tactical_void_created': 'Backup overseas pace slot vacated; frees up an overseas slot for auction flexibility.',
        'auction_status': 'Available in Auction (Universe D)'
    },
    {
        'player_name': 'Kuldeep Sen', 'nationality': 'India', 'is_overseas': False,
        'transaction_type': 'Released', 'previous_role': 'Indian Express Bowler',
        'tactical_void_created': 'Frees domestic purse and slot; domestic pace depth thinned.',
        'auction_status': 'Available in Auction (Universe D)'
    },
    {
        'player_name': 'Yudhvir Singh', 'nationality': 'India', 'is_overseas': False,
        'transaction_type': 'Released', 'previous_role': 'Domestic Seam All-Rounder',
        'tactical_void_created': 'Minor domestic bench depth adjustment.',
        'auction_status': 'Available in Auction (Universe D)'
    },
    {
        'player_name': 'Kwena Maphaka', 'nationality': 'South Africa', 'is_overseas': True,
        'transaction_type': 'Released', 'previous_role': 'Overseas Left-Arm Fast Bowler',
        'tactical_void_created': 'Developmental overseas pace slot vacated.',
        'auction_status': 'Available in Auction (Universe D)'
    },
    {
        'player_name': 'Vignesh Puthur', 'nationality': 'India', 'is_overseas': False,
        'transaction_type': 'Released', 'previous_role': 'Domestic Bench Depth',
        'tactical_void_created': 'Roster consolidation.',
        'auction_status': 'Domestic Auction Pool'
    },
    {
        'player_name': 'Ravi Singh', 'nationality': 'India', 'is_overseas': False,
        'transaction_type': 'Released', 'previous_role': 'Domestic Bench Depth',
        'tactical_void_created': 'Roster consolidation.',
        'auction_status': 'Domestic Auction Pool'
    },
    {
        'player_name': 'Emanjot Singh Chahal', 'nationality': 'India', 'is_overseas': False,
        'transaction_type': 'Released', 'previous_role': 'Domestic Bench Depth',
        'tactical_void_created': 'Roster consolidation.',
        'auction_status': 'Domestic Auction Pool'
    },
    {
        'player_name': 'Mohammed Shami', 'nationality': 'India', 'is_overseas': False,
        'transaction_type': 'Traded In (from LSG)', 'previous_role': 'Frontline Indian Fast Bowler',
        'tactical_void_created': 'Massive upgrade to new-ball Powerplay wicket-taking; 6.65 Press Econ.',
        'auction_status': 'Confirmed in RR Squad'
    },
    {
        'player_name': 'Manimaran Siddharth', 'nationality': 'India', 'is_overseas': False,
        'transaction_type': 'Traded In (from LSG)', 'previous_role': 'Slow Left-Arm Orthodox Spinner',
        'tactical_void_created': 'Provides direct left-arm orthodox backup for Ravindra Jadeja.',
        'auction_status': 'Confirmed in RR Squad'
    },
    {
        'player_name': 'Sam Curran', 'nationality': 'England', 'is_overseas': True,
        'transaction_type': 'Traded Out (to LSG)', 'previous_role': 'Overseas Pace-Bowling All-Rounder',
        'tactical_void_created': 'Departed RR to LSG; frees up substantial overseas slot and auction purse flexibility.',
        'auction_status': 'Not in RR Squad (LSG)'
    }
]

rr_transfers_df = pd.DataFrame(rr_transfers_data)
rr_transfers_df.to_csv(f"{SCRATCH}/RR_RELEASED_AND_TRADED_PLAYERS.csv", index=False)
rr_transfers_df.to_csv(f"{ROOT}/RR_RELEASED_AND_TRADED_PLAYERS.csv", index=False)
print("  Saved: RR_RELEASED_AND_TRADED_PLAYERS.csv (12 transfer/release records)")

# ------------------------------------------------------------------------------
# 3. GENERATE RR_ROLE_REQUIREMENTS.csv
# ------------------------------------------------------------------------------
print("\n[3/6] Generating RR_ROLE_REQUIREMENTS.csv...")

role_reqs = [
    {
        'Requirement_ID': 'REQ-01',
        'Role_Name': 'Middle-Order Power Finisher (No. 5/6)',
        'Priority_Tier': 'Tier 1 (Critical / Highest)',
        'Urgency_Score_Max25': 25,
        'Slots_Allocated': 1,
        'Target_Player_Type': 'Overseas or Elite Indian Batter',
        'Phase_Focus': 'Death Overs (16-20) & Middle Acceleration (12-15)',
        'Required_Skillset': 'Boundary % >= 20% under pressure, Death SR >= 165, ability to hit high pace and hard lengths from ball 1.',
        'Existing_Squad_Coverage': 'Donovan Ferreira (untested over full season), Shubham Dubey (young domestic), Ravindra Jadeja (better at 7).',
        'Impact_of_Unfilled_Gap': 'Catastrophic death-overs stalling; inability to chase 10+ RRR; wasted top-order platforms.'
    },
    {
        'Requirement_ID': 'REQ-02',
        'Role_Name': 'Death-Over Fast Bowling Specialist',
        'Priority_Tier': 'Tier 1 (Critical / High)',
        'Urgency_Score_Max25': 23,
        'Slots_Allocated': 1,
        'Target_Player_Type': 'Overseas Fast Bowler or Elite Indian Pacer',
        'Phase_Focus': 'Death Overs (17-20)',
        'Required_Skillset': 'Pressure Economy <= 7.80 RPO, Death Economy <= 9.00 RPO, reliable yorker and slower-ball execution under pressure.',
        'Existing_Squad_Coverage': 'Jofra Archer (injury-prone workload risk), Sandeep Sharma (10.25 Press Econ), Mohammed Shami (better in PP/Mid).',
        'Impact_of_Unfilled_Gap': 'Leaking 12-15 RPO in overs 18-20 if Archer rests or sustains injury; losing defendable totals.'
    },
    {
        'Requirement_ID': 'REQ-03',
        'Role_Name': 'Dynamic Indian Middle-Order / Finisher Backup',
        'Priority_Tier': 'Tier 2 (Moderate / Strategic)',
        'Urgency_Score_Max25': 18,
        'Slots_Allocated': 1,
        'Target_Player_Type': 'Indian Domestic Batter / Floater',
        'Phase_Focus': 'Middle Overs (7-15) & Finishing (16-20)',
        'Required_Skillset': 'Press SR >= 140, ability to rotate strike vs spin and hit pace; domestic experience.',
        'Existing_Squad_Coverage': 'Dhruv Jurel and Riyan Parag cover starting 11; bench drops off to uncapped Aman Rao and Sooryavanshi.',
        'Impact_of_Unfilled_Gap': 'Fragile middle order if Parag or Jurel suffers form slump or injury.'
    },
    {
        'Requirement_ID': 'REQ-04',
        'Role_Name': 'Indian Fast Bowling Backup (Domestic Workhorse)',
        'Priority_Tier': 'Tier 2 (Moderate / Depth)',
        'Urgency_Score_Max25': 15,
        'Slots_Allocated': 1,
        'Target_Player_Type': 'Indian Domestic Fast Bowler',
        'Phase_Focus': 'Powerplay & Middle Overs',
        'Required_Skillset': 'Consistent hard lengths, IPL/Ranji experience, Economy <= 8.50.',
        'Existing_Squad_Coverage': 'Sushant Mishra, Brijesh Sharma, Yash Raj Punja (all uncapped / raw).',
        'Impact_of_Unfilled_Gap': 'Heavy reliance on aging Shami (35) and Sandeep Sharma across a 14-match tournament.'
    },
    {
        'Requirement_ID': 'REQ-05',
        'Role_Name': 'Multi-Skilled Pace-Bowling All-Rounder Backup',
        'Priority_Tier': 'Tier 3 (Tactical Balance)',
        'Urgency_Score_Max25': 14,
        'Slots_Allocated': 1,
        'Target_Player_Type': 'Overseas or Indian Seam All-Rounder',
        'Phase_Focus': 'Overs 10-18 (Batting) / Overs 6-14 (Bowling)',
        'Required_Skillset': 'Useful 2 overs of seam + 140+ SR lower-order batting.',
        'Existing_Squad_Coverage': 'Dasun Shanaka (overseas), but no Indian pace-bowling all-rounder in the squad.',
        'Impact_of_Unfilled_Gap': 'Lack of tactical sixth-bowler flexibility when fielding two overseas fast bowlers.'
    },
    {
        'Requirement_ID': 'REQ-06',
        'Role_Name': 'Wicketkeeping Depth / Mystery Spin Bench',
        'Priority_Tier': 'Tier 3 (Depth / Base Price)',
        'Urgency_Score_Max25': 10,
        'Slots_Allocated': 1,
        'Target_Player_Type': 'Indian Domestic Keeper / Spinner',
        'Phase_Focus': 'Bench Insurance',
        'Required_Skillset': 'Reliable wicketkeeping gloves, base-price value.',
        'Existing_Squad_Coverage': 'Dhruv Jurel is only Indian WK; Pretorius and Ferreira consume overseas slots.',
        'Impact_of_Unfilled_Gap': 'Forced to use an overseas slot on a backup wicketkeeper if Jurel is injured.'
    }
]

role_reqs_df = pd.DataFrame(role_reqs)
role_reqs_df.to_csv(f"{SCRATCH}/RR_ROLE_REQUIREMENTS.csv", index=False)
role_reqs_df.to_csv(f"{ROOT}/RR_ROLE_REQUIREMENTS.csv", index=False)
print("  Saved: RR_ROLE_REQUIREMENTS.csv (6 distinct requirements)")

# ------------------------------------------------------------------------------
# 4. CALCULATE RR SQUAD-FIT SCORE FOR AUCTION CANDIDATES
# ------------------------------------------------------------------------------
print("\n[4/6] Calculating RR Squad-Fit Score for Available Candidates...")

# Filter to available auction candidates in Universe D
avail_bat = bat_rankings[bat_rankings['universe_D_available'] == True].copy()
avail_bowl = bowl_rankings[bowl_rankings['universe_D_available'] == True].copy()

# Indian player correction dictionary for nationality
indian_players = {
    'Mahipal Lomror', 'Deepak Chahar', 'Ravichandran Ashwin', 'Deepak Hooda',
    'Umran Malik', 'Tushar Deshpande', 'Dinesh Karthik', 'Shahrukh Khan',
    'Karun Nair', 'Mayank Agarwal', 'Manish Pandey', 'Vijay Shankar',
    'Shivam Mavi', 'Chetan Sakariya', 'Kamlesh Nagarkoti', 'Kartik Tyagi',
    'Siddarth Kaul', 'Varun Aaron', 'Barinder Sran', 'Ankit Rajpoot'
}

for name in indian_players:
    avail_bat.loc[avail_bat['player_name'] == name, 'nationality'] = 'India'
    avail_bowl.loc[avail_bowl['player_name'] == name, 'nationality'] = 'India'

def calculate_bat_fit(row):
    # Role urgency (0-25)
    # Finishers (No. 5/6) get highest score
    d_sr = row['death_sr']
    p_sr = row['press_sr']
    is_os = row['nationality'] != 'India'
    
    # Assess role
    if d_sr >= 165 and p_sr >= 150:
        role_score = 25.0 # Elite Finisher
        tact_score = 19.0
    elif d_sr >= 150 or p_sr >= 140:
        role_score = 20.0 # Good middle-order accelerator
        tact_score = 16.0
    elif d_sr >= 135:
        role_score = 15.0 # Stabilizer
        tact_score = 13.0
    else:
        role_score = 10.0 # Anchor / Top-order (low RR need)
        tact_score = 10.0
        
    # Pressure score component (0-25)
    press_comp = (row['reliability_adjusted_score'] / 100.0) * 25.0
    
    # Phase suitability (0-15) based on Death SR
    if d_sr >= 170: phase_score = 15.0
    elif d_sr >= 155: phase_score = 12.0
    elif d_sr >= 140: phase_score = 9.0
    elif d_sr >= 125: phase_score = 6.0
    else: phase_score = 3.0
    
    # Squad balance & budget feasibility (0-10)
    # Overseas slots are limited (3), so elite overseas get 9, elite Indian finishers get 10
    if not is_os:
        bal_score = 10.0 # Indian finisher is gold dust
    else:
        bal_score = 8.5 # Overseas finisher is top target
        
    # Confidence (0-5)
    conf = str(row['confidence']).upper()
    if conf == 'HIGH': conf_score = 5.0
    elif conf == 'MEDIUM': conf_score = 4.0
    elif conf == 'LOW': conf_score = 2.5
    else: conf_score = 1.0
    
    total_fit = role_score + tact_score + press_comp + phase_score + bal_score + conf_score
    return round(total_fit, 2)

def calculate_bowl_fit(row):
    p_econ = row['press_econ']
    d_econ = row['death_econ']
    is_os = row['nationality'] != 'India'
    
    # Role urgency (0-25)
    # Death-over specialists get highest score
    if p_econ <= 7.8 and d_econ <= 9.2:
        role_score = 23.0 # Elite Death Specialist
        tact_score = 18.0
    elif p_econ <= 8.5 and d_econ <= 9.8:
        role_score = 18.0 # Solid pace option
        tact_score = 15.0
    elif p_econ <= 7.5:
        role_score = 16.0 # Control/Middle spinner
        tact_score = 14.0
    else:
        role_score = 10.0
        tact_score = 10.0
        
    # Pressure score component (0-25)
    press_comp = (row['reliability_adjusted_score'] / 100.0) * 25.0
    
    # Phase suitability (0-15) based on Death Econ
    if d_econ <= 8.2: phase_score = 15.0
    elif d_econ <= 9.0: phase_score = 12.0
    elif d_econ <= 9.8: phase_score = 9.0
    elif d_econ <= 10.5: phase_score = 6.0
    else: phase_score = 3.0
    
    # Squad balance (0-10)
    if not is_os:
        bal_score = 9.5 # Indian pace depth is vital
    else:
        bal_score = 8.5 # Overseas pace
        
    # Confidence (0-5)
    conf = str(row['confidence']).upper()
    if conf == 'HIGH': conf_score = 5.0
    elif conf == 'MEDIUM': conf_score = 4.0
    elif conf == 'LOW': conf_score = 2.5
    else: conf_score = 1.0
    
    total_fit = role_score + tact_score + press_comp + phase_score + bal_score + conf_score
    return round(total_fit, 2)

avail_bat['rr_squad_fit_score'] = avail_bat.apply(calculate_bat_fit, axis=1)
avail_bowl['rr_squad_fit_score'] = avail_bowl.apply(calculate_bowl_fit, axis=1)

# Save combined squad-fit rankings
bat_fit_export = avail_bat[avail_bat['press_legal'] >= 30][[
    'player_name', 'nationality', 'career_runs', 'career_sr', 'press_legal',
    'press_runs', 'press_sr', 'press_sr_shrunk', 'death_sr', 'confidence',
    'reliability_adjusted_score', 'rr_squad_fit_score'
]].sort_values('rr_squad_fit_score', ascending=False).reset_index(drop=True)
bat_fit_export['role_type'] = 'Batter / All-Rounder'

bowl_fit_export = avail_bowl[avail_bowl['press_legal'] >= 30][[
    'player_name', 'nationality', 'career_bowler_wkts', 'career_econ', 'press_legal',
    'press_runs_conc', 'press_econ', 'press_econ_shrunk', 'death_econ', 'confidence',
    'reliability_adjusted_score', 'rr_squad_fit_score'
]].sort_values('rr_squad_fit_score', ascending=False).reset_index(drop=True)
bowl_fit_export['role_type'] = 'Bowler / All-Rounder'

fit_rankings_combined = pd.concat([bat_fit_export, bowl_fit_export], ignore_index=True).sort_values('rr_squad_fit_score', ascending=False).reset_index(drop=True)
fit_rankings_combined['overall_fit_rank'] = range(1, len(fit_rankings_combined) + 1)

fit_rankings_combined.to_csv(f"{SCRATCH}/RR_SQUAD_FIT_RANKINGS.csv", index=False)
fit_rankings_combined.to_csv(f"{ROOT}/RR_SQUAD_FIT_RANKINGS.csv", index=False)
print("  Saved: RR_SQUAD_FIT_RANKINGS.csv")

# ------------------------------------------------------------------------------
# 5. GENERATE RR_AUCTION_SHORTLIST.csv (8 TARGET CATEGORIES)
# ------------------------------------------------------------------------------
print("\n[5/6] Generating RR_AUCTION_SHORTLIST.csv across 8 Buckets...")

shortlist_data = [
    # 1. Overseas Finishers (Direct Hetmyer Replacement)
    {
        'Target_Bucket': '1. Overseas Power Finisher',
        'Player_Name': 'Daryl Mitchell', 'Nationality': 'New Zealand', 'Is_Overseas': True,
        'Primary_Role': 'Middle-Order Power Finisher (No. 4/5/6)', 'Batting_Pos': 'No. 5', 'Bowling_Phase': 'Part-time Medium',
        'Pressure_Performance_Score': 84.88, 'Pressure_Balls': 75, 'Confidence_Tier': 'MEDIUM',
        'RR_Squad_Fit_Score': 89.60, 'Auction_Eligibility_Status': 'Confirmed Auction-Eligible (Universe D)',
        'Why_Player_Fits_RR': 'Ranked #1 pressure batter; 188.00 Press SR, 172.31 Death SR; neutralises spin in middle overs and obliterates pace at the death.',
        'Potential_Limitations': 'Right-hander (does not provide Hetmyer\'s left-handed tactical match-up).'
    },
    {
        'Target_Bucket': '1. Overseas Power Finisher',
        'Player_Name': 'Matthew Wade', 'Nationality': 'Australia', 'Is_Overseas': True,
        'Primary_Role': 'Wicketkeeper Death Finisher (No. 6/7)', 'Batting_Pos': 'No. 6 / 7', 'Bowling_Phase': 'None',
        'Pressure_Performance_Score': 84.44, 'Pressure_Balls': 80, 'Confidence_Tier': 'MEDIUM',
        'RR_Squad_Fit_Score': 89.45, 'Auction_Eligibility_Status': 'Confirmed Auction-Eligible (Universe D)',
        'Why_Player_Fits_RR': 'Ranked #2 pressure batter; Left-handed finisher (direct Hetmyer match-up); 178.75 Press SR, 172.25 Death SR; backup keeper.',
        'Potential_Limitations': 'Age profile (38); primarily effective in 10-15 ball bursts at the extreme death.'
    },
    {
        'Target_Bucket': '1. Overseas Power Finisher',
        'Player_Name': 'Shimron Hetmyer', 'Nationality': 'West Indies', 'Is_Overseas': True,
        'Primary_Role': 'Proven Left-Hand Finisher (No. 5/6)', 'Batting_Pos': 'No. 5 / 6', 'Bowling_Phase': 'None',
        'Pressure_Performance_Score': 75.69, 'Pressure_Balls': 109, 'Confidence_Tier': 'MEDIUM',
        'RR_Squad_Fit_Score': 85.90, 'Auction_Eligibility_Status': 'Confirmed Auction-Eligible (Universe D)',
        'Why_Player_Fits_RR': 'RR buy-back candidate; zero assimilation friction; knows Jaipur conditions; 168.17 Death SR; 109 balls under pressure.',
        'Potential_Limitations': 'Was released due to high retention price tag; risk of bidding war if other franchises drive price up.'
    },
    {
        'Target_Bucket': '1. Overseas Power Finisher',
        'Player_Name': 'Gareth Delany', 'Nationality': 'Ireland', 'Is_Overseas': True,
        'Primary_Role': 'Power-Hitting Finisher / All-Rounder', 'Batting_Pos': 'No. 6 / 7', 'Bowling_Phase': 'Middle Leg-Spin',
        'Pressure_Performance_Score': 74.58, 'Pressure_Balls': 88, 'Confidence_Tier': 'MEDIUM',
        'RR_Squad_Fit_Score': 83.25, 'Auction_Eligibility_Status': 'Confirmed Auction-Eligible (Universe D)',
        'Why_Player_Fits_RR': 'High-ceiling budget option; 169.32 Press SR, 167.53 Death SR; provides useful leg-spin overs.',
        'Potential_Limitations': 'Untested in high-pressure IPL playoff environments.'
    },

    # 2. Indian Middle-Order Batters / Stabilizers
    {
        'Target_Bucket': '2. Indian Middle-Order Batter',
        'Player_Name': 'Mahipal Lomror', 'Nationality': 'India', 'Is_Overseas': False,
        'Primary_Role': 'Middle-Order Power Batter / Finisher', 'Batting_Pos': 'No. 5 / 6', 'Bowling_Phase': 'Part-time Left-arm Spin',
        'Pressure_Performance_Score': 88.82, 'Pressure_Balls': 31, 'Confidence_Tier': 'LOW',
        'RR_Squad_Fit_Score': 91.20, 'Auction_Eligibility_Status': 'Confirmed Auction-Eligible (Universe D)',
        'Why_Player_Fits_RR': 'Local Rajasthan domestic player; ex-RR player; Left-handed middle-order spin destroyer; 254.8 Press SR; solves Indian batting depth.',
        'Potential_Limitations': 'Small pressure sample size (31 balls); vulnerability against high express pace above 145 km/h.'
    },
    {
        'Target_Bucket': '2. Indian Middle-Order Batter',
        'Player_Name': 'Deepak Hooda', 'Nationality': 'India', 'Is_Overseas': False,
        'Primary_Role': 'Middle-Order Floater / Off-Spinner', 'Batting_Pos': 'No. 4 / 5', 'Bowling_Phase': 'Middle Off-Spin',
        'Pressure_Performance_Score': 68.45, 'Pressure_Balls': 30, 'Confidence_Tier': 'LOW',
        'RR_Squad_Fit_Score': 75.80, 'Auction_Eligibility_Status': 'Confirmed Auction-Eligible (Universe D)',
        'Why_Player_Fits_RR': 'Experienced Indian international; provides middle-overs stability and right-arm off-spin backup for Bishnoi/Jadeja.',
        'Potential_Limitations': 'Inconsistent recent strike rate in middle overs.'
    },

    # 3. Indian Finishers
    {
        'Target_Bucket': '3. Indian Finisher',
        'Player_Name': 'Shahrukh Khan', 'Nationality': 'India', 'Is_Overseas': False,
        'Primary_Role': 'Lower-Order Power Striker (No. 6/7)', 'Batting_Pos': 'No. 6 / 7', 'Bowling_Phase': 'None',
        'Pressure_Performance_Score': 71.30, 'Pressure_Balls': 35, 'Confidence_Tier': 'LOW',
        'RR_Squad_Fit_Score': 78.40, 'Auction_Eligibility_Status': 'Confirmed Auction-Eligible (Universe D)',
        'Why_Player_Fits_RR': 'Hard-hitting Indian domestic specialist for overs 18-20; physical power against hard lengths.',
        'Potential_Limitations': 'Susceptibility to elite wide-line yorkers; high dot-ball percentage.'
    },

    # 4. Overseas Middle-Order Batters
    {
        'Target_Bucket': '4. Overseas Middle-Order Batter',
        'Player_Name': 'Glenn Maxwell', 'Nationality': 'Australia', 'Is_Overseas': True,
        'Primary_Role': 'Dynamic Middle-Order Game Changer', 'Batting_Pos': 'No. 4 / 5', 'Bowling_Phase': 'Powerplay/Middle Off-Spin',
        'Pressure_Performance_Score': 84.40, 'Pressure_Balls': 37, 'Confidence_Tier': 'LOW',
        'RR_Squad_Fit_Score': 86.10, 'Auction_Eligibility_Status': 'Confirmed Auction-Eligible (Universe D)',
        'Why_Player_Fits_RR': '202.94 Death SR; elite reverse-sweeps and spin destruction; valuable off-spin against left-handers.',
        'Potential_Limitations': 'High price expectation; high-risk shot selection under extreme pressure.'
    },

    # 5. Overseas Death-Over Fast Bowlers (Archer Backup / Tandem)
    {
        'Target_Bucket': '5. Overseas Death-Over Fast Bowler',
        'Player_Name': 'Matheesha Pathirana', 'Nationality': 'Sri Lanka', 'Is_Overseas': True,
        'Primary_Role': 'Slinger Death-Overs Wicket-Taker', 'Batting_Pos': 'No. 11', 'Bowling_Phase': 'Middle & Death (15-20)',
        'Pressure_Performance_Score': 73.01, 'Pressure_Balls': 243, 'Confidence_Tier': 'HIGH',
        'RR_Squad_Fit_Score': 89.80, 'Auction_Eligibility_Status': 'Confirmed Auction-Eligible (Universe D)',
        'Why_Player_Fits_RR': 'Ranked #1 wicket-taker under pressure (23 wickets in 243 balls); 7.60 Press Econ; slingy trajectory unpickable at the death.',
        'Potential_Limitations': 'Will command massive auction demand; overseas slot competition with Archer.'
    },
    {
        'Target_Bucket': '5. Overseas Death-Over Fast Bowler',
        'Player_Name': 'FazalHaq Farooqi', 'Nationality': 'Afghanistan', 'Is_Overseas': True,
        'Primary_Role': 'Left-Arm Swing & Death Specialist', 'Batting_Pos': 'No. 10 / 11', 'Bowling_Phase': 'Powerplay (1-3) & Death (18, 20)',
        'Pressure_Performance_Score': 76.65, 'Pressure_Balls': 137, 'Confidence_Tier': 'HIGH',
        'RR_Squad_Fit_Score': 88.50, 'Auction_Eligibility_Status': 'Confirmed Auction-Eligible (Universe D)',
        'Why_Player_Fits_RR': 'Ranked #3 pressure bowler; 7.18 Press Econ across 137 balls; left-arm angle creates dual Powerplay/Death flexibility.',
        'Potential_Limitations': 'Overseas slot dynamics if RR fields Mitchell/Hetmyer in batting.'
    },
    {
        'Target_Bucket': '5. Overseas Death-Over Fast Bowler',
        'Player_Name': 'Tim Southee', 'Nationality': 'New Zealand', 'Is_Overseas': True,
        'Primary_Role': 'Experienced Fast-Medium Death Specialist', 'Batting_Pos': 'No. 9 / 10', 'Bowling_Phase': 'Powerplay & Death',
        'Pressure_Performance_Score': 75.78, 'Pressure_Balls': 126, 'Confidence_Tier': 'HIGH',
        'RR_Squad_Fit_Score': 85.20, 'Auction_Eligibility_Status': 'Confirmed Auction-Eligible (Universe D)',
        'Why_Player_Fits_RR': 'Ranked #4 pressure bowler; 7.14 Press Econ across 126 balls; veteran leadership; budget-friendly buy.',
        'Potential_Limitations': 'Lack of express pace (130-135 km/h) compared to Archer/Burger.'
    },
    {
        'Target_Bucket': '5. Overseas Death-Over Fast Bowler',
        'Player_Name': 'Richard Ngarava', 'Nationality': 'Zimbabwe', 'Is_Overseas': True,
        'Primary_Role': 'Left-Arm Hostile Fast Bowler', 'Batting_Pos': 'No. 10 / 11', 'Bowling_Phase': 'Powerplay & Death',
        'Pressure_Performance_Score': 77.49, 'Pressure_Balls': 68, 'Confidence_Tier': 'MEDIUM',
        'RR_Squad_Fit_Score': 84.70, 'Auction_Eligibility_Status': 'Confirmed Auction-Eligible (Universe D)',
        'Why_Player_Fits_RR': 'Ranked #2 pressure bowler; 6.79 Press Econ; tall left-arm bounce; highly economical under pressure.',
        'Potential_Limitations': 'Limited IPL experience under high crowd pressure.'
    },

    # 6. Indian Death-Over / Pace Backup
    {
        'Target_Bucket': '6. Indian Fast Bowler Backup',
        'Player_Name': 'Deepak Chahar', 'Nationality': 'India', 'Is_Overseas': False,
        'Primary_Role': 'New-Ball Swing Bowler & Lower-Order Hitter', 'Batting_Pos': 'No. 8 / 9', 'Bowling_Phase': 'Powerplay (1-6)',
        'Pressure_Performance_Score': 74.70, 'Pressure_Balls': 47, 'Confidence_Tier': 'LOW',
        'RR_Squad_Fit_Score': 82.50, 'Auction_Eligibility_Status': 'Confirmed Auction-Eligible (Universe D)',
        'Why_Player_Fits_RR': 'Elite Indian new-ball swing bowler; provides batting depth at No. 8 (176.6 Press SR); hedges Shami workload.',
        'Potential_Limitations': 'History of hamstring and back injuries; not a dedicated death bowler.'
    },
    {
        'Target_Bucket': '6. Indian Fast Bowler Backup',
        'Player_Name': 'Umran Malik', 'Nationality': 'India', 'Is_Overseas': False,
        'Primary_Role': 'Indian Express Fast Bowler (150+ km/h)', 'Batting_Pos': 'No. 11', 'Bowling_Phase': 'Middle Overs (7-15)',
        'Pressure_Performance_Score': 61.44, 'Pressure_Balls': 78, 'Confidence_Tier': 'MEDIUM',
        'RR_Squad_Fit_Score': 76.90, 'Auction_Eligibility_Status': 'Confirmed Auction-Eligible (Universe D)',
        'Why_Player_Fits_RR': 'Raw express pace (150+ km/h) for middle overs; 5.92 Press Econ in dataset; high developmental upside.',
        'Potential_Limitations': 'Radar inconsistency; can leak boundaries if lines stray.'
    },

    # 7. Pace-Bowling All-Rounders
    {
        'Target_Bucket': '7. Pace-Bowling All-Rounder',
        'Player_Name': 'Sikandar Raza', 'Nationality': 'Zimbabwe', 'Is_Overseas': True,
        'Primary_Role': 'Dynamic All-Rounder (Finisher & Spinner)', 'Batting_Pos': 'No. 5 / 6', 'Bowling_Phase': 'Middle Overs',
        'Pressure_Performance_Score': 83.14, 'Pressure_Balls': 65, 'Confidence_Tier': 'MEDIUM',
        'RR_Squad_Fit_Score': 87.80, 'Auction_Eligibility_Status': 'Confirmed Auction-Eligible (Universe D)',
        'Why_Player_Fits_RR': 'Ranked #3 pressure batter; 193.85 Press SR, 197.30 Death SR; mystery off-spin bowling; tremendous dual utility.',
        'Potential_Limitations': 'Bowls spin rather than pace; takes an overseas slot.'
    },
    {
        'Target_Bucket': '7. Pace-Bowling All-Rounder',
        'Player_Name': 'Shamar Springer', 'Nationality': 'West Indies', 'Is_Overseas': True,
        'Primary_Role': 'Seam-Bowling All-Rounder / Finisher', 'Batting_Pos': 'No. 7 / 8', 'Bowling_Phase': 'Death Overs Medium-Fast',
        'Pressure_Performance_Score': 80.15, 'Pressure_Balls': 61, 'Confidence_Tier': 'MEDIUM',
        'RR_Squad_Fit_Score': 81.30, 'Auction_Eligibility_Status': 'Confirmed Auction-Eligible (Universe D)',
        'Why_Player_Fits_RR': '213.33 Death SR; deceptive slower-ball yorkers at the death; budget pace-all-rounder.',
        'Potential_Limitations': 'Untested in IPL conditions.'
    },

    # 8. Spin-Bowling Options / Backup
    {
        'Target_Bucket': '8. Spin-Bowling Option',
        'Player_Name': 'Maheesh Theekshana', 'Nationality': 'Sri Lanka', 'Is_Overseas': True,
        'Primary_Role': 'Mystery Spin Bowler (Powerplay & Death)', 'Batting_Pos': 'No. 10 / 11', 'Bowling_Phase': 'Powerplay & Death',
        'Pressure_Performance_Score': 78.05, 'Pressure_Balls': 200, 'Confidence_Tier': 'HIGH',
        'RR_Squad_Fit_Score': 84.10, 'Auction_Eligibility_Status': 'Confirmed Auction-Eligible (Universe D)',
        'Why_Player_Fits_RR': 'Ranked #1 pressure bowler; 7.41 Press Econ across 200 balls; carrom balls and yorkers; tactical choke option.',
        'Potential_Limitations': 'RR already has Bishnoi and Jadeja in starting 11; overseas slot luxury.'
    },
    {
        'Target_Bucket': '8. Spin-Bowling Option',
        'Player_Name': 'Ravichandran Ashwin', 'Nationality': 'India', 'Is_Overseas': False,
        'Primary_Role': 'Tactical Off-Spin Bowler & Floater', 'Batting_Pos': 'No. 8', 'Bowling_Phase': 'Powerplay & Middle',
        'Pressure_Performance_Score': 74.23, 'Pressure_Balls': 117, 'Confidence_Tier': 'MEDIUM',
        'RR_Squad_Fit_Score': 81.90, 'Auction_Eligibility_Status': 'Confirmed Auction-Eligible (Universe D)',
        'Why_Player_Fits_RR': 'Ex-RR leader; 6.97 Press Econ; 173.2 Death SR with bat; unmatched cricketing IQ and tactical matchup value.',
        'Potential_Limitations': 'Less potent on flat batting pitches; fielding mobility.'
    }
]

shortlist_df = pd.DataFrame(shortlist_data)
shortlist_df.to_csv(f"{SCRATCH}/RR_AUCTION_SHORTLIST.csv", index=False)
shortlist_df.to_csv(f"{ROOT}/RR_AUCTION_SHORTLIST.csv", index=False)
print("  Saved: RR_AUCTION_SHORTLIST.csv (16 targets across 8 buckets)")

print("\n" + "="*80)
print("ALL CSV DATA FILES SUCCESSFULLY COMPILED AND SAVED!")
print("="*80)
