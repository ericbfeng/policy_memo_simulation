import random

def simulate_game(
    n_rounds=50,
    cost_high_safety=100,    # Cost if AI Company invests in high safety
    cost_low_safety=40,     # Cost if AI Company invests in low safety
    prob_bias_high=0.05,     # Bias probability if high safety is invested
    prob_bias_low=0.3,       # Bias probability if low safety is invested
    auditor_check_cost=5,    # Cost for Auditor's thorough check
    wager_amount=50,         # Amount Auditor risks if filing a report
    fine_amount=1000         # Fine on AI Company if bias is confirmed
):
    """
    In each round:
      1. The AI Company chooses high or low safety (incurring a cost).
         - If high: cost = -300; if low: cost = -100.
      2. The Auditor decides whether to pay for due dilligence.
         - If yes: cost = -5; if no: 0.
      3. If a bias signal is generated, the Auditor may place a wager.
         - If wager placed:
             * Auditor pays wager_amount (-10) then:
                 - If bias is confirmed (true positive): 
                       Auditor gains (fine_amount + wager_amount) and AI Company loses fine_amount.
                 - If bias is not confirmed (false positive): 
                       Auditor loses wager_amount and AI Company recovers half the wager.
         - If no wager is placed, both wager effects are 0.
    
    Overall round outcome:
      - AI Company: incremental_ai = ai_safety_effect + ai_wager_effect
      - Auditor: incremental_auditor = auditor_check_effect + auditor_wager_effect

    Returns a history of rounds with:
      - Decisions and individual incremental effects.
      - Overall round outcomes (incremental_ai, incremental_auditor).
    """
    history = []
    cumulative_ai = 0
    cumulative_auditor = 0

    for round_i in range(n_rounds):
        # 1. AI Company Safety Investment
        ai_invests_high = random.choice([True, False])
        if ai_invests_high:
            prob_bias = prob_bias_high
            ai_safety_effect = -cost_high_safety
        else:
            prob_bias = prob_bias_low
            ai_safety_effect = -cost_low_safety

        # 2. Auditor Check Decision for due diligence:
        auditor_pays_for_check = random.choice([True, False])
        if auditor_pays_for_check:
            auditor_check_effect = -auditor_check_cost
            # With check, better detection
            signal_bias = random.random() < (prob_bias * 0.9 + (1 - prob_bias) * 0.1)
        else:
            auditor_check_effect = 0
            signal_bias = random.random() < prob_bias

        # 3. Wager Decision
        if signal_bias:
            wager_placed = True
            # Auditor pays wager cost.
            auditor_wager_effect = -wager_amount
            is_biased = random.random() < prob_bias
            if is_biased:
                # True Positive:
                auditor_wager_effect += fine_amount + wager_amount  # net gain = fine_amount
                ai_wager_effect = -fine_amount
            else:
                # False Positive:
                auditor_wager_effect = -wager_amount
                ai_wager_effect = wager_amount * 0.5
        else:
            wager_placed = False
            auditor_wager_effect = 0
            ai_wager_effect = 0

        incremental_ai = ai_safety_effect + ai_wager_effect
        incremental_auditor = auditor_check_effect + auditor_wager_effect

        cumulative_ai += incremental_ai
        cumulative_auditor += incremental_auditor

        history.append({
            'round': round_i + 1,
            'ai_invests_high': ai_invests_high,
            'auditor_pays_for_check': auditor_pays_for_check,
            'signal_bias': signal_bias,
            'wager_placed': wager_placed,
            'ai_safety_effect': ai_safety_effect,
            'auditor_check_effect': auditor_check_effect,
            'ai_wager_effect': ai_wager_effect,
            'auditor_wager_effect': auditor_wager_effect,
            'incremental_ai': incremental_ai,
            'incremental_auditor': incremental_auditor,
            'cumulative_ai': cumulative_ai,
            'cumulative_auditor': cumulative_auditor
        })
    
    return history, cumulative_ai, cumulative_auditor

def summarize_buckets(history):
    """
    For each decision bucket, group rounds by whether the decision was True or False,
    and record the overall round outcome for each party.
      - For ai_invests_high: record incremental_ai for rounds where it's True, else 0.
      - For auditor_pays_for_check: record incremental_auditor for rounds where it's True, else 0.
      - For wager_placed: record incremental_ai and incremental_auditor for rounds where it's True, else 0.
    Then compute the average outcome for each bucket.
    """
    buckets = {
        'ai_invests_high': {
            'true': {'ai': [], 'auditor': []},
            'false': {'ai': [], 'auditor': []}
        },
        'auditor_pays_for_check': {
            'true': {'ai': [], 'auditor': []},
            'false': {'ai': [], 'auditor': []}
        },
        'wager_placed': {
            'true': {'ai': [], 'auditor': []},
            'false': {'ai': [], 'auditor': []}
        }
    }
    
    for round_info in history:
        # For ai_invests_high, record overall incremental outcome for AI Company.
        if round_info['ai_invests_high']:
            buckets['ai_invests_high']['true']['ai'].append(round_info['incremental_ai'])
            buckets['ai_invests_high']['true']['auditor'].append(round_info['incremental_auditor'])
        else:
            buckets['ai_invests_high']['false']['ai'].append(round_info['incremental_ai'])
            buckets['ai_invests_high']['false']['auditor'].append(round_info['incremental_auditor'])
            
        # For auditor_pays_for_check, record overall incremental outcome for Auditor.
        if round_info['auditor_pays_for_check']:
            buckets['auditor_pays_for_check']['true']['auditor'].append(round_info['incremental_auditor'])
            buckets['auditor_pays_for_check']['true']['ai'].append(round_info['incremental_ai'])
        else:
            buckets['auditor_pays_for_check']['false']['auditor'].append(round_info['incremental_auditor'])
            buckets['auditor_pays_for_check']['false']['ai'].append(round_info['incremental_ai'])
            
        # For wager_placed, record overall round outcome if wager was placed; else 0.
        if round_info['wager_placed']:
            buckets['wager_placed']['true']['ai'].append(round_info['incremental_ai'])
            buckets['wager_placed']['true']['auditor'].append(round_info['incremental_auditor'])
        else:
            buckets['wager_placed']['false']['ai'].append(0)
            buckets['wager_placed']['false']['auditor'].append(0)
    
    summary = {}
    for bucket, groups in buckets.items():
        summary[bucket] = {}
        for group, outcomes in groups.items():
            avg_ai = sum(outcomes['ai']) / len(outcomes['ai']) if outcomes['ai'] else 0
            avg_auditor = sum(outcomes['auditor']) / len(outcomes['auditor']) if outcomes['auditor'] else 0
            summary[bucket][group] = {
                'count': len(outcomes['ai']),
                'avg_ai_outcome': avg_ai,
                'avg_auditor_outcome': avg_auditor
            }
    return summary

def main():
    random.seed(42)  # For reproducibility.
    history, final_cum_ai, final_cum_auditor = simulate_game(n_rounds=5000)
    bucket_summary = summarize_buckets(history)

    print("Final Cumulative AI Company Payoff:", final_cum_ai)
    print("Final Cumulative Auditor Payoff:", final_cum_auditor)
    print("\nBucket Summary (Average Outcome per Decision):")
    
    print("\nDecision: ai_invests_high")
    print("  True Decisions: Count =", bucket_summary['ai_invests_high']['true']['count'],
          "Average AI Outcome =", bucket_summary['ai_invests_high']['true']['avg_ai_outcome'],
          "Average Auditor Outcome =", bucket_summary['ai_invests_high']['true']['avg_auditor_outcome'])
    print("  False Decisions: Count =", bucket_summary['ai_invests_high']['false']['count'],
          "Average AI Outcome =", bucket_summary['ai_invests_high']['false']['avg_ai_outcome'],
          "Average Auditor Outcome =", bucket_summary['ai_invests_high']['false']['avg_auditor_outcome'])
    
    print("\nDecision: auditor_pays_for_check")
    print("  True Decisions: Count =", bucket_summary['auditor_pays_for_check']['true']['count'],
          "Average AI Outcome =", bucket_summary['auditor_pays_for_check']['true']['avg_ai_outcome'],
          "Average Auditor Outcome =", bucket_summary['auditor_pays_for_check']['true']['avg_auditor_outcome'])
    print("  False Decisions: Count =", bucket_summary['auditor_pays_for_check']['false']['count'],
          "Average AI Outcome =", bucket_summary['auditor_pays_for_check']['false']['avg_ai_outcome'],
          "Average Auditor Outcome =", bucket_summary['auditor_pays_for_check']['false']['avg_auditor_outcome'])
    
    print("\nDecision: wager_placed")
    print("  True Decisions: Count =", bucket_summary['wager_placed']['true']['count'],
          "Average AI Outcome =", bucket_summary['wager_placed']['true']['avg_ai_outcome'],
          "Average Auditor Outcome =", bucket_summary['wager_placed']['true']['avg_auditor_outcome'])
    print("  False Decisions: Count =", bucket_summary['wager_placed']['false']['count'],
          "Average AI Outcome =", bucket_summary['wager_placed']['false']['avg_ai_outcome'],
          "Average Auditor Outcome =", bucket_summary['wager_placed']['false']['avg_auditor_outcome'])
    
    # Sanity check for wager_placed for Auditor (False): should be 0.
    print("\nSanity Check for 'wager_placed' Bucket (Auditor, False):",
          bucket_summary['wager_placed']['false']['avg_auditor_outcome'])

if __name__ == "__main__":
    main()
