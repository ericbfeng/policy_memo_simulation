import random

def simulate_game(
    n_rounds=50,
    cost_high_safety=300,   # Cost to AI Company if it invests in high safety
    cost_low_safety=100,     # Cost to AI Company if it invests in low safety
    prob_bias_high=0.05,    # Probability that bias is present if AI invests in high safety
    prob_bias_low=0.5,     # Probability that bias is present if AI invests in low safety
    auditor_check_cost=5,  # Cost for the auditor to perform a thorough check
    wager_amount=10,       # Amount the auditor risks if it files a report
    fine_amount=5000         # Fine imposed on the AI Company if bias is confirmed
):
    """
    Simulate multiple rounds of interaction between:
      - An AI Company choosing high or low safety investment
      - An AI Auditor choosing whether to pay for a thorough check and file a wager

    Returns a record of outcomes for each round.
    """
    ai_company_payoff = 0
    auditor_payoff = 0
    history = []

    for round_i in range(n_rounds):
        # AI Company decision: High or Low safety
        ai_invests_high = random.choice([True, False])
        if ai_invests_high:
            prob_bias = prob_bias_high
            ai_cost = cost_high_safety
        else:
            prob_bias = prob_bias_low
            ai_cost = cost_low_safety
        ai_company_payoff -= ai_cost

        # Auditor decision: Whether to pay for a thorough check
        auditor_pays_for_check = random.choice([True, False])
        if auditor_pays_for_check:
            auditor_payoff -= auditor_check_cost
            # With a thorough check, the chance to correctly detect bias is higher:
            signal_bias = random.random() < (prob_bias * 0.95 + (1 - prob_bias) * 0.05)
        else:
            # No check => a noisier estimate
            signal_bias = random.random() < prob_bias

        # Auditor decision: Whether to place a wager based on the signal
        wager_placed = False
        if signal_bias:
            wager_placed = True
            auditor_payoff -= wager_amount  # Subtract wager cost
            # Determine true bias
            is_biased = random.random() < prob_bias
            if is_biased:
                # True Positive: AI Company fined; auditor gains reward plus wager back
                ai_company_payoff -= fine_amount
                auditor_payoff += fine_amount + wager_amount
            else:
                # False Positive: Auditor loses wager; AI Company recovers half the wager
                ai_company_payoff += wager_amount * 0.5

        # Record round result
        history.append({
            'round': round_i + 1,
            'ai_invests_high': ai_invests_high,
            'auditor_pays_for_check': auditor_pays_for_check,
            'signal_bias': signal_bias,
            'wager_placed': wager_placed,
            'ai_company_payoff': ai_company_payoff,
            'auditor_payoff': auditor_payoff
        })

    return history, ai_company_payoff, auditor_payoff

def summarize_history(history):
    summary = {
        'rounds': len(history),
        'ai_invests_high': {'True': 0, 'False': 0},
        'auditor_pays_for_check': {'True': 0, 'False': 0},
        'signal_bias': {'True': 0, 'False': 0},
        'wager_placed': {'True': 0, 'False': 0},
    }
    for round_info in history:
        for key in ['ai_invests_high', 'auditor_pays_for_check', 'signal_bias', 'wager_placed']:
            if round_info[key]:
                summary[key]['True'] += 1
            else:
                summary[key]['False'] += 1
    return summary

def summarize_payouts(history):
    # For each decision, compute the average payoff for AI Company and Auditor
    decisions = ['ai_invests_high', 'auditor_pays_for_check', 'signal_bias', 'wager_placed']
    payout_summary = {}
    for decision in decisions:
        true_ai_payoffs = []
        false_ai_payoffs = []
        true_auditor_payoffs = []
        false_auditor_payoffs = []
        for round_info in history:
            if round_info[decision]:
                true_ai_payoffs.append(round_info['ai_company_payoff'])
                true_auditor_payoffs.append(round_info['auditor_payoff'])
            else:
                false_ai_payoffs.append(round_info['ai_company_payoff'])
                false_auditor_payoffs.append(round_info['auditor_payoff'])
        avg_true_ai = sum(true_ai_payoffs) / len(true_ai_payoffs) if true_ai_payoffs else 0
        avg_false_ai = sum(false_ai_payoffs) / len(false_ai_payoffs) if false_ai_payoffs else 0
        avg_true_aud = sum(true_auditor_payoffs) / len(true_auditor_payoffs) if true_auditor_payoffs else 0
        avg_false_aud = sum(false_auditor_payoffs) / len(false_auditor_payoffs) if false_auditor_payoffs else 0
        payout_summary[decision] = {
            'true': {
                'count': len(true_ai_payoffs),
                'avg_ai_company_payoff': avg_true_ai,
                'avg_auditor_payoff': avg_true_aud
            },
            'false': {
                'count': len(false_ai_payoffs),
                'avg_ai_company_payoff': avg_false_ai,
                'avg_auditor_payoff': avg_false_aud
            }
        }
    return payout_summary

def main():
    history, final_ai_payoff, final_auditor_payoff = simulate_game(n_rounds=5000)
    decision_summary = summarize_history(history)
    payout_summary = summarize_payouts(history)

    print("Summary of Decisions and Outcomes:")
    print(f"Total Rounds: {decision_summary['rounds']}")
    print("AI Company - High Safety Investment:", decision_summary['ai_invests_high'])
    print("Auditor - Paid for Check:", decision_summary['auditor_pays_for_check'])
    print("Auditor - Signal Bias:", decision_summary['signal_bias'])
    print("Auditor - Wager Placed:", decision_summary['wager_placed'])
    print(f"\nFinal AI Company Payoff: {final_ai_payoff}")
    print(f"Final Auditor Payoff: {final_auditor_payoff}\n")
    
    print("Average Payoffs by Decision:")
    for decision, data in payout_summary.items():
        print(f"\nDecision: {decision}")
        print("  True Decisions:")
        print(f"    Count: {data['true']['count']}")
        print(f"    Average AI Company Payoff: {data['true']['avg_ai_company_payoff']/data['true']['count']:.2f}")
        print(f"    Average Auditor Payoff: {data['true']['avg_auditor_payoff']/data['true']['count']:.2f}")
        print("  False Decisions:")
        print(f"    Count: {data['false']['count']}")
        print(f"    Average AI Company Payoff: {data['false']['avg_ai_company_payoff']/data['false']['count']:.2f}")
        print(f"    Average Auditor Payoff: {data['false']['avg_auditor_payoff']/data['false']['count']:.2f}")

if __name__ == "__main__":
    main()
