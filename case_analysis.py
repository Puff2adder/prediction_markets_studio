"""Worked and sensitivity analyses use the same financial engine and renderer."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from engine import binary_position, complete_set, conversion, discount
from studio_theme import style_plotly


def say(message):
    st.markdown(message.replace('$', r'\$'))


def table(data):
    frame = pd.DataFrame(data).map(lambda x: x.replace('$', r'\$') if isinstance(x, str) else x)
    st.table(frame)


def plot(fig):
    st.plotly_chart(style_plotly(fig), use_container_width=True, theme=None)


def sports(price=.62, n=100, r=0.0, t=.5):
    v=binary_position(price,n,r,t,.5)
    say(f'**Purchase cost today:** {n} × ${price:.2f} = **${v["cost"]:.2f}**. '
        f'If this cost is financed, repayment at T is **${v["funding"]:.2f}**.')
    table({'Result':['Harbor wins','Draw','Valley wins'],
           'Yes payoff per claim ($)':[1,0,0], 'No payoff per claim ($)':[0,1,1],
           'Total Yes payoff ($)':[n,0,0],
           'Profit after financing at T ($)':[v['yes_profit'],v['no_profit'],v['no_profit']]})
    say('**Interpretation:** a draw is a No outcome. The digital payout does not grow with the winning margin. '
        'Payoff describes what the claim delivers; profit also deducts its cost. At zero interest, financing adds nothing to the initial cost.')
    if price>v['discount']:
        st.warning('This chosen quote exceeds the price of a certain $1 and violates the textbook upper bound. Cash-flow arithmetic still applies.')


def binary_set(yes=.56,no=.38,r=.04,t=.5):
    v=complete_set([yes,no],r,t)
    d=v['discount']
    table({'Result':['Harbor wins','Draw','Valley wins'],
           'Yes payoff ($)':[1,0,0],'No payoff ($)':[0,1,1],'Pair payoff ($)':[1,1,1]})
    say(f'The pair pays $1 for certain at T, so its no-arbitrage value is '
        f'**P(0,T) = exp(−rT) = ${d:.6f}**. The quoted total is **${v["total"]:.6f}**.')
    if v['direction']=='balanced':
        st.success('The prices satisfy complete-set parity: this comparison offers no arbitrage gain.')
    else:
        buy=v['direction']=='buy';sign=1 if buy else -1
        say('**Buy both claims and borrow the present value of $1.**' if buy else
            '**Short both claims and buy a bond paying $1 at T.**')
        table({'Transaction':['Buy Yes' if buy else 'Short Yes','Buy No' if buy else 'Short No',
                              'Borrow P(0,T)' if buy else 'Buy bond','Net'],
               'Today ($)':[-sign*yes,-sign*no,sign*d,abs(v['gap'])],
               'Harbor wins at T ($)':[sign,0,-sign,0],
               'Harbor does not win at T ($)':[0,sign,-sign,0]})
        say(f'**Outcome:** receive **${abs(v["gap"]):.6f} today**, with zero future net liability in either event.')
    say('**Interpretation:** this trade relies on matching cash flows, not forecasting the winner. '
        'Changing r or T changes the value today of the certain future dollar. All trades use the stated frictionless funding and execution assumptions.')


def three_set(qh=.5,draw_share=.4,offset=.02,r=.04,t=.5):
    d=discount(r,t);qd=(1-qh)*draw_share;qa=1-qh-qd
    qs=[qh,qd,qa];vs=[d*q for q in qs];fair=vs[0]+vs[1];quote=fair+offset
    table({'Result':['Home win','Draw','Away win'],'Pricing probability qᵢ':qs,
           'Claim price Vᵢ today ($)':vs,'Payoff if home wins ($)':[1,0,0],
           'Payoff if draw ($)':[0,1,0],'Payoff if away wins ($)':[0,0,1]})
    say(f'One of each pays $1 for certain and costs **${sum(vs):.6f} = P(0,T)**. '
        'These prices are constructed from pricing probabilities; no physical forecast is assumed.')
    say(f'**Related claim: Harbor does not lose.** Buy a home-win claim and a draw claim. '
        f'Together they cost **${fair:.6f}** and reproduce that payoff. '
        f'The separate claim is quoted at **${quote:.6f}**.')
    sign=1 if offset>=0 else -1
    if abs(offset)<1e-9:
        st.success('The combined claim matches its replication value.')
    else:
        say('**Short the combined claim; buy home + draw.**' if offset>0 else
            '**Buy the combined claim; short home + draw.**')
        table({'Transaction':['Combined claim','Home + draw claims','Net'],
               'Today ($)':[sign*quote,-sign*fair,abs(offset)],
               'Home win at T ($)':[-sign,sign,0],'Draw at T ($)':[-sign,sign,0],
               'Away win at T ($)':[0,0,0]})
    say('**Interpretation:** home win, draw and away win are disjoint and exhaustive. '
        'But “home win” overlaps with “home does not lose”: their summed payoff is 2, 1 or 0, not a certain dollar. '
        'Do not add related markets unless their outcome definitions justify it.')


def beliefs(price=.62,p=.70,n=100,r=0.0,t=.5):
    v=binary_position(price,n,r,t,p)
    if v['q'] is None:
        st.error('This quote exceeds P(0,T); dividing it by the bond price produces a number above 1, not a valid pricing probability. Lower the price to compare p and q.')
        return
    q=v['q']
    table({'Measure':['Personal belief p','Pricing probability q = Y₀/P(0,T)'],
           'Value':[f'{p:.1%}',f'{q:.1%}'],
           'Meaning':['Your assessment of the chance of a win','Probability implied by a consistent textbook price']})
    say(f'**Step 1: cash flows.** Buying {n} claims costs **${v["cost"]:.2f}** today; '
        f'the financed repayment at T is **${v["funding"]:.2f}**.')
    table({'Outcome':['Harbor wins','Harbor does not win'], 'Your probability':[p,1-p],
           'Claim payout ($)':[n,0],'Profit at T after financing ($)':[v['yes_profit'],v['no_profit']]})
    say(f'**Step 2: expected profit under your belief.** '
        f'{p:.2f} × ({v["yes_profit"]:.2f}) + {1-p:.2f} × ({v["no_profit"]:.2f}) '
        f'= **${v["expected_profit"]:.2f}**.')
    st.latex(r'q=Y_0/P(0,T)=Y_0e^{rT},\qquad E_p[\text{profit at }T]=n(p-q)')
    say('Each claim pays $1 if it wins. Y₀ is its price today; n is the number of claims; '
        'P(0,T) = exp(−rT) is the discount factor. Eₚ means expectation under your belief p. '
        'The displayed profit is at T after financing. Its present value is P(0,T) × n(p−q).')
    say('**Interpretation:** p > q gives positive expected profit under your belief, but the losing outcome remains possible. '
        'Your belief is not necessarily the true physical probability. Neither a market price nor a personal opinion establishes that true probability. '
        'No-arbitrage constrains relative prices; it does not guarantee q equals the physical probability.')


def gdp(p=.20,price=.30):
    q=price;cost=40*price;expected=40*p-cost
    table({'Measure':['Assumed objective probability p','Price V of low-GDP claim today','Pricing probability q = V/P(0,T)'],
           'Value':[f'{p:.0%}',f'${price:.2f}',f'{q:.0%}']})
    st.latex(r'q=\frac{V}{P(0,T)}=\frac{V}{1}\quad\text{when }r=0')
    say('V is the dollar price of a $1-payout claim. P(0,T) is the dollar price today of a certain $1 at payment. '
        'The ratio q is unitless. The objective probability p describes likelihood; q is inferred from price.')
    say(f'**Buy 40 claims.** Their cost is **${cost:.2f}**. Borrow that amount at zero interest '
        'and repay it in either state. This makes the cost of protection explicit.')
    table({'State':['Low GDP: g < 1%','Other: g ≥ 1%'],'Objective probability':[p,1-p],
           'Income without protection ($)':[60,100],'Claim payout ($)':[40,0],
           'Cost repayment ($)':[cost,cost],'Net income with protection ($)':[100-cost,100-cost]})
    say(f'Expected claim payout is 40 × p = **${40*p:.2f}**. Expected profit on the claims alone is '
        f'**${expected:.2f}**. Expected income without protection is **${100-40*p:.2f}**; '
        f'with protection, income is **${100-cost:.2f} in either state**.')
    if q>p+1e-9:
        say('**Interpretation: protection commands a premium in this example.** q exceeds p. '
            'The household gives up some expected income but receives money when income is low and an extra dollar is especially useful. '
            'That can explain why insurance is desirable despite negative expected investment profit. It does not mean low GDP became more likely.')
    elif q<p-1e-9:
        say('**Interpretation:** q is below p. This chosen quote no longer illustrates an extra price for bad-state protection. '
            'The claims have positive expected profit under the assumed objective probability, but remain risky by themselves.')
    else:
        say('**Interpretation:** q equals p. Price equals expected payout at zero interest, so the claims have zero expected investment profit. '
            'They still transfer income into the low-GDP state.')
    say('The price is a separate hypothetical input, not a formula derived from p. The value of protection can help explain q > p, '
        'but does not specify the exact price. Whether protection is worth its cost depends on preferences and exposure.')
    say(f'The complementary other-state claim costs **${1-price:.2f}**. Together the two claims cost and pay $1, '
        'so their prices satisfy complete-set parity even when pricing and objective probabilities differ.')


def platform(yb=.57,ya=.58,nb=.38,na=.39,bc=.01,sc=.01):
    if yb>ya or nb>na:
        st.error('A bid must not exceed its ask in this exercise. Correct the quotes before calculating conversion gains.')
        return
    v=conversion(yb,ya,nb,na,bc,sc)
    table({'Strategy':['Buy at asks, then merge','Split collateral, then sell at bids'],
           'Proceeds':[1,yb+nb],'Outlay':[ya+na,1],'Total costs':[bc,sc],
           'Net gain (collateral units)':[v['buy_merge'],v['split_sell']]})
    say(f'**Buy-and-merge:** 1 − {ya:.3f} − {na:.3f} − {bc:.3f} = **{v["buy_merge"]:.3f}**. '
        f'**Split-and-sell:** {yb:.3f} + {nb:.3f} − 1 − {sc:.3f} = **{v["split_sell"]:.3f}**.')
    say('**Interpretation:** buying uses asks and selling uses bids. Proceeds from merging are available now, '
        'so the comparison is with current collateral. A positive calculated gain assumes both orders fill and conversion succeeds; '
        'displayed last-trade prices alone do not demonstrate a live opportunity.')
