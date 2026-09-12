"""Prediction Studio: worked cases before sensitivity controls."""
import math
import random
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from engine import discount, binary_position
from questions import QUESTIONS
from studio_theme import apply_studio_theme, style_plotly
import case_analysis as analysis


def prose(renderer):
    def render(message, *args, **kwargs):
        return renderer(message.replace('$', r'\$'), *args, **kwargs)
    return render

write, info, success, warning, error, caption = (
    prose(getattr(st, name)) for name in ('write','info','success','warning','error','caption')
)
st.set_page_config(page_title='Prediction Studio · Digital Claims',page_icon='◈',layout='wide')
apply_studio_theme()
PAGES=['Start here','1 · Sports payoffs','2 · Complete sets','3 · Prices and beliefs',
       '4 · GDP protection','5 · Polymarket connection','6 · Practice']

def reset_prefix(prefix):
    for key in list(st.session_state):
        if key.startswith(prefix):
            del st.session_state[key]


def reset_all():
    st.session_state.clear()


def preset(values):
    st.session_state.update(values)


def table(data):
    frame = pd.DataFrame(data).map(lambda x: x.replace('$', r'\$') if isinstance(x, str) else x)
    st.table(frame)


def chart(fig):
    st.plotly_chart(style_plotly(fig), use_container_width=True, theme=None)


def funding(prefix, rate=4.0, years=0.5):
    a, b = st.columns(2)
    r = a.slider('Annual continuously compounded interest rate r (%)', 0.0, 12.0, rate, 0.5,
                 key=prefix+'rate')
    t = b.slider('Time until payment T (years)', 0.0, 2.0, years, 0.25, key=prefix+'years')
    d = discount(r/100, t)
    caption(f'P(0,T) = exp(−rT) = {d:.6f} dollars today per $1 at payment. '
               'The calculation converts the displayed percentage r to a decimal. '
               'T = 0 is the immediate-payment benchmark.')
    return r/100, t, d


def assumptions():
    info('Textbook model: each claim pays $1 in its stated outcome, zero otherwise, '
            'only at the common date T. Same currency, certain payment, no fees, '
            'borrowing/lending at r, and feasible purchases and short sales at the displayed prices.')


def mcq(question, prefix='quiz_'):
    ident, prompt, options, correct, hint, explanation = question
    key = prefix+ident
    order = list(range(len(options)))
    random.Random(ident).shuffle(order)
    answer = st.radio(prompt.replace('$', r'\$'), order, index=None,
                      format_func=lambda i: options[i], key=key+'_answer')
    if st.button('Check answer', key=key+'_check'):
        if answer is None:
            warning('Choose an answer first.')
        else:
            st.session_state[key+'_attempt'] = answer
    attempted = st.session_state.get(key+'_attempt')
    if attempted is not None:
        if answer != attempted:
            caption('Answer changed. Check again to update the feedback.')
        elif attempted == correct:
            success(explanation)
        else:
            warning('Try again. '+hint)
        if st.button('Explain the solution', key=key+'_explain'):
            st.session_state[key+'_reveal'] = True
        if st.session_state.get(key+'_reveal'):
            info(options[correct]+': '+explanation)


def numeric(prompt, target, hint, solution, key, tolerance=0.005):
    answer = st.number_input(prompt, value=None, format='%.4f', key=key+'_answer')
    if st.button('Check calculation', key=key+'_check'):
        if answer is None:
            warning('Enter your calculation first.')
        else:
            st.session_state[key+'_attempt'] = answer
    if key+'_attempt' in st.session_state:
        attempt = st.session_state[key+'_attempt']
        if answer != attempt:
            caption('Answer changed. Check again to update the feedback.')
        elif math.isclose(attempt, target, abs_tol=tolerance):
            success('Correct. '+solution)
        else:
            warning('Not yet. '+hint)
        if st.button('Show worked solution', key=key+'_solution'):
            st.session_state[key+'_show'] = True
        if st.session_state.get(key+'_show'):
            info(solution)



st.sidebar.title('Prediction Studio')
page=st.sidebar.radio('Learning sequence',PAGES,key='page')
st.sidebar.caption('Hypothetical cases · Ungraded practice')
if page=='Start here':
    st.title('Prediction Studio')
    write('Learn how digital claims transfer risk, how replication connects their prices, and why a pricing probability can differ from the likelihood of an event.')
    st.markdown("""
- **Sports:** distinguish payoff from profit and build complete sets of outcomes.
- **Beliefs and GDP:** separate likelihood from price and understand the value of protection in bad times.
- **Market connection and practice:** apply the ideas to a brief conversion example and check your understanding.
""")
    info('Each case starts with a problem, learning objectives, default data and a worked explanation. Open the sensitivity controls only after studying the example, then answer the consolidation questions. Begin with Sports payoffs in the menu.')
    st.stop()

index=PAGES.index(page)
prefix=f's{index}_'
st.sidebar.button('Reset this section',on_click=reset_prefix,args=(prefix,))
st.sidebar.button('Start over',on_click=reset_all)
st.title(page.split(' · ')[1])


def opening(problem,objective):
    st.subheader('The problem')
    write(problem)
    st.subheader('What you will learn')
    write(objective)


def data(items):
    st.subheader('Default data')
    table({'Input and definition':list(items),'Benchmark value':list(items.values())})
    caption('These benchmark values stay fixed. Later controls change only the separate scenario below.')


def explore(prompt):
    st.divider()
    st.subheader('Explore sensitivities — after the worked example')
    write(prompt)
    return st.checkbox('Open sensitivity controls',key=prefix+'explore')


def consolidate(ids,summary):
    st.divider()
    st.subheader('Consolidate your learning')
    for i in ids:
        mcq(QUESTIONS[i],prefix)
    st.subheader('What you accomplished')
    write(summary)


if index==1:
    opening('You are considering buying a claim on Harbor FC beating Valley United. What does it pay, and how much could you gain or lose? A draw matters: “Harbor does not win” includes both a draw and a loss.',
            'Identify a digital payoff, distinguish the payoff from profit, and explain why the purchase price changes profit without changing the contractual payout.')
    data({'Event':'Harbor wins a completed regulation-time soccer match',
          'Settlement rule':'Regulation includes stoppage time; extra time and penalties excluded. Assume completion and certain payment; void/cancellation rules excluded.',
          'Yes / No payout':'$1 if Harbor wins / $1 if Harbor does not win; zero otherwise',
          'Y₀ — Yes purchase price':'$0.62 per claim', 'n — long position':'100 claims',
          'T — time until payment':'0.5 years (six months)', 'r — annual continuous interest rate':'0%; no fees'})
    st.subheader('Worked analysis and outcome')
    analysis.sports()
    if explore('Predict first: if the premium rises, does the payoff change or just profit? What happens when the number of claims doubles?'):
        a,b=st.columns(2)
        price=a.slider('Yes purchase price Y₀ ($ per claim)',0.0,1.0,.62,.01,key='s1_price')
        n=b.slider('Number of long claims n',0,200,100,10,key='s1_n')
        r,t,d=funding('s1_',rate=0.0)
        st.subheader('Your scenario: result and interpretation')
        analysis.sports(price,n,r,t)
    consolidate([0,1],'You can read both sides of a binary contract and calculate the cash flows in every match result, including a draw.')

elif index==2:
    opening('Can you combine claims on the same match to produce a certain payment? And can a separately quoted related claim be replicated more cheaply?',
            'Recognize mutually exclusive, exhaustive outcomes; use the bond price to value a complete set; and distinguish an arbitrage from a forecast.')
    mode=st.radio('Choose the case',['Binary: Yes plus No','Three outcomes: win, draw, loss'],key='s2_mode')
    assumptions()
    if mode.startswith('Binary'):
        data({'Yes event':'Harbor wins in regulation', 'No event':'Harbor draws or loses',
              'Y₀ / N₀ — claim prices today':'$0.56 / $0.38','Payout':'One winning claim pays $1 at T',
              'r — annual continuous rate':'4%', 'T — years to payment':'0.5'})
        st.subheader('Worked analysis and outcome')
        analysis.binary_set()
    else:
        data({'Outcomes':'Home win, draw, away win in the same completed regulation-time match',
              'q_home / q_draw / q_away — pricing probabilities':'50% / 20% / 30%; these are not physical forecasts',
              'Vᵢ — price of the $1 claim on outcome i':'Constructed as P(0,T) × qᵢ',
              'Related claim':'Harbor does not lose: pays $1 on home win OR draw',
              'Separate quote':'Replication value plus $0.02', 'r / T':'4% annually, continuously compounded / 0.5 years'})
        st.subheader('Worked analysis and outcome')
        analysis.three_set()
    if explore('Change one input at a time. Does the certain payoff change when interest rates change? In the three-outcome case, which claims reproduce “Harbor does not lose”?'):
        r,t,d=funding('s2_')
        a,b=st.columns(2)
        if mode.startswith('Binary'):
            yes=a.number_input('Yes price Y₀ ($)',0.0,1.0,.56,.01,format='%.3f',key='s2_yes')
            no=b.number_input('No price N₀ ($)',0.0,1.0,.38,.01,format='%.3f',key='s2_no')
            st.subheader('Your scenario: result and interpretation')
            analysis.binary_set(yes,no,r,t)
        else:
            qh=a.slider('Home-win pricing probability q_home (%)',5,85,50,5,key='s2_qh')/100
            share=b.slider('Draw share of the remaining pricing probability (%)',0,100,40,5,key='s2_share')/100
            caption('q_draw = (1 − q_home) × draw share; q_away = 1 − q_home − q_draw. The three pricing probabilities therefore sum to one.')
            offset=st.slider('Separate combined-claim quote minus replication value ($)',-.02,.02,.02,.005,key='s2_offset')
            st.subheader('Your scenario: result and interpretation')
            analysis.three_set(qh,share,offset,r,t)
    consolidate([3,4],'You can use a complete set to replicate a bond and combine disjoint outcomes to price related claims. Overlapping claims do not automatically sum to a certain dollar.')

elif index==3:
    opening('You believe Harbor has a 70% chance of winning, but its $1 Yes claim costs $0.62. Is the market wrong? Is buying the claim a guaranteed gain?',
            'Distinguish three ideas: the true physical likelihood, your personal belief p about that likelihood, and the pricing probability q inferred from a quote. Calculate expected profit under a stated belief without confusing it with arbitrage.')
    data({'Contract':'$1 if Harbor wins in regulation; $0 on a draw or loss',
          'Y₀ — hypothetical market price':'$0.62 per claim', 'p — your personal belief':'70%; not asserted to be the true probability',
          'n — number of claims bought':'100', 'r / T':'0% interest / 0.5 years; no fees',
          'P(0,T) — price of a certain $1 at payment':'$1 at zero interest'})
    st.subheader('Worked analysis and outcome')
    analysis.beliefs()
    st.subheader('Before changing inputs: what should move?')
    table({'Personal belief p':['60%','70%','80%'], 'Market price Y₀ ($)':[.62,.62,.62],
           'Pricing probability q':['62%','62%','62%'],'Expected profit on 100 claims ($)':[-2,8,18]})
    write('Holding the quote fixed, changing your belief changes expected profit, but leaves q and both outcome payoffs unchanged. The chance of losing is not eliminated by a positive expected profit.')
    if explore('First vary only your belief. Then hold your belief fixed and vary the price. Explain which changes reflect a forecast and which reflect the cost of taking the position.'):
        a,b=st.columns(2)
        price=a.slider(r'Yes price Y₀ (\$ per \$1 claim)',0.0,1.0,.62,.01,key='s3_price')
        p=b.slider('Your personal probability p (%)',0,100,70,1,key='s3_p')/100
        n=st.slider('Number of Yes claims n',0,200,100,10,key='s3_n')
        r,t,d=funding('s3_',rate=0.0)
        st.subheader('Your scenario: result and interpretation')
        analysis.beliefs(price,p,n,r,t)
        if price<=d:
            q=price/d
            fig=go.Figure(go.Scatter(x=list(range(101)),y=[n*(i/100-q) for i in range(101)],mode='lines',name='Expected profit',line_color='#0756A3'))
            fig.add_hline(y=0,line_color='#00866A');fig.add_vline(x=q*100,line_dash='dash',line_color='#BF2424')
            fig.update_layout(xaxis_title='Personal probability p (%)',yaxis_title='Expected financed profit at T ($)',title='The dashed line is the pricing probability q')
            chart(fig)
    consolidate([5,6],'You can calculate expected profit under a belief, explain the price-implied probability, and recognize that neither is automatically the true physical probability.')

elif index==4:
    opening('A household earns less when GDP growth is low. It can buy a claim that pays in that bad state. Why might it pay more than the claim’s objective expected cash payout?',
            'Separate the objective likelihood p of low GDP from the pricing probability q. Understand why an extra dollar in bad times can make protection desirable, even with negative expected investment profit.')
    data({'g — annual real GDP growth':'Low state: g < 1%; other state: g ≥ 1%',
          'Observation and payment':'First published annual figure for the specified year; ignore revisions. Assume observation and certain payment at T = 1 year.',
          'p — assumed objective low-GDP probability':'20%; assumed known for teaching, not estimated from data',
          'V — hypothetical low-GDP claim price':'$0.30 for a $1 payout in low GDP, zero otherwise',
          'Household income at payment':'$60 in low GDP; $100 otherwise (small teaching amounts)',
          'Protection bought':'40 claims, financed at zero interest', 'r — annual interest rate':'0%; no fees; P(0,T) = $1'})
    st.subheader('Worked analysis and outcome')
    analysis.gdp()
    st.subheader('Before changing inputs: what should move?')
    table({'Objective probability p':['20%','20%','20%'], 'Price V ($)':[.20,.30,.40],
           'Pricing probability q':['20%','30%','40%'], 'Cost of 40 claims ($)':[8,12,16],
           'Income after protection in either state ($)':[92,88,84]})
    write('A higher insurance price lowers income after paying for protection and raises q. It does not, by itself, make low GDP more likely. The exact market price is not determined by this insurance intuition.')
    if explore('Keep the objective probability at 20% and raise the price. What changes about the protection and its cost? Then hold the price fixed and change p: which expectation changes, and which cash flows stay the same?'):
        a,b=st.columns(2)
        p=a.slider('Assumed objective probability of low GDP p (%)',5,60,20,5,key='s4_p')/100
        price=b.slider('Hypothetical low-GDP claim price V ($ per claim)',.05,.60,.30,.01,key='s4_price')
        caption('These inputs are independent. The studio does not derive a market price from p. Interest remains zero and the hedge remains 40 claims.')
        st.subheader('Your scenario: result and interpretation')
        analysis.gdp(p,price)
        fig=go.Figure(go.Bar(x=['Objective probability p','Pricing probability q'],y=[p,price],marker_color=['#00866A','#0756A3']))
        fig.update_layout(yaxis_title='Probability',yaxis_tickformat='.0%',yaxis_range=[0,1],title='Likelihood and the price of protection')
        chart(fig)
    consolidate([7,8],'You can explain how protection pays when income is low, why its price can imply q > p, and why that does not establish a higher objective chance of bad times.')

elif index==5:
    opening('Imagine token versions of Harbor’s Yes and No claims. A matching pair can be merged into collateral immediately. How would you test whether buying the pair and merging it is profitable?',
            'Distinguish a future certain dollar from collateral now; use executable asks for purchases, bids for sales, and subtract all transaction costs.')
    data({'Mechanism':'One collateral unit can be split into one Yes + one No; the pair can be merged before resolution.',
          'Yes bid / ask':'0.57 / 0.58 collateral units', 'No bid / ask':'0.38 / 0.39 collateral units',
          'All-in costs':'0.01 per complete buy/merge strategy; 0.01 per complete split/sell strategy',
          'Assumptions':'Invented quotes and costs; both orders fill, conversion succeeds; ignore rewards and collateral risk.'})
    st.subheader('Worked analysis and outcome')
    analysis.platform()
    if explore('Raise the asks or the purchase costs. At what point does buy-and-merge cease to be profitable? Why do higher bids affect the other direction?'):
        a,b=st.columns(2)
        yb=a.number_input('Yes bid (collateral units)',0.0,1.0,.57,.01,key='s5_yb')
        ya=b.number_input('Yes ask (collateral units)',0.0,1.0,.58,.01,key='s5_ya')
        nb=a.number_input('No bid (collateral units)',0.0,1.0,.38,.01,key='s5_nb')
        na=b.number_input('No ask (collateral units)',0.0,1.0,.39,.01,key='s5_na')
        bc=a.number_input('Total buy-and-merge cost per pair',0.0,.2,.01,.005,format='%.3f',key='s5_bc')
        sc=b.number_input('Total split-and-sell cost per pair',0.0,.2,.01,.005,format='%.3f',key='s5_sc')
        st.subheader('Your scenario: result and interpretation')
        analysis.platform(yb,ya,nb,na,bc,sc)
    consolidate([10,11],'You can distinguish the textbook payment-date benchmark from immediate token conversion and evaluate a hypothetical opportunity using executable prices after costs.')
    st.markdown('Sources: [Polymarket positions and tokens](https://docs.polymarket.com/concepts/positions-tokens) and [fees](https://docs.polymarket.com/trading/fees), checked 11 September 2026. This is a brief illustration of documented mechanics, not a live trading opportunity.')

else:
    opening('Can you apply the cash-flow and replication ideas on your own?',
            'Retrieve the key distinctions and solve the short homework calculations before revealing their explanations.')
    with st.expander('Review a worked benchmark before attempting the homework'):
        data({'Quantity':'10 Yes claims','Price':'$0.40 per $1-payout claim', 'Interest / fees':'Zero'})
        write('Cost is $4. If the event occurs, payout is $10 and profit is $6. Otherwise payout is zero and profit is −$4. Payoff and profit answer different questions.')
    write('Attempt each question before opening a worked explanation. These are ungraded checks; '
             'nothing is submitted to an instructor. Reset this section to retry from a blank attempt.')
    activity=st.radio('Practice activity',['Three short calculations','Knowledge checks'],key='s6_activity')
    if activity=='Three short calculations':
        st.subheader('1 · Payoff, profit and belief')
        write('Buy 100 Harbor-win claims for $0.62 each, at zero interest and zero fees. '
                 'Your personal home-win probability is 70%. Claims pay $1 each on a home win and zero otherwise.')
        numeric('Expected profit under your belief ($)',8,
                'Compute profit in both outcomes and weight by your probabilities.',
                'Cost = $62. Win profit = $38; non-win profit = −$62. Expected profit = 0.70×38 + 0.30×(−62) = $8. '
                'The loss remains possible; this is not arbitrage.','s6_hw1')
        st.subheader('2 · Replicate the complete set')
        write('Yes costs $0.56 and No costs $0.38. Both pay only in six months. The annual continuously '
                 'compounded rate is 4%. Assume the frictionless textbook trading and payment conditions.')
        numeric('Arbitrage profit today per pair ($)',discount(.04,.5)-.94,
                'Borrow the present value of $1, then pay for both claims.',
                'Borrow exp(−0.04×0.5) = $0.980199. Buy both for $0.94. Keep $0.040199 today. '
                'At T exactly one claim pays $1, repaying the $1 loan in every result.','s6_hw2',.00005)
        st.subheader('3 · Immediate conversion')
        write('An immediately mergeable Yes/No pair has asks of 0.58 and 0.39 collateral units. '
                 'All purchase and conversion costs together are 0.01. Assume successful fills and conversion.')
        numeric('Net collateral gain per pair',.02,
                'Subtract both asks and the total cost from immediate proceeds of one.',
                '1 − 0.58 − 0.39 − 0.01 = 0.02. This benchmark is collateral now, not a future payment.','s6_hw3',.00005)
    else:
        selection=st.selectbox('Choose a question',range(len(QUESTIONS)),
                               format_func=lambda i:f'{i+1}. {QUESTIONS[i][1]}',key='s6_question')
        mcq(QUESTIONS[selection],'s6_')
        caption('Twelve questions cover the lecture, homework and GDP extension. There is no grade or leaderboard.')


st.divider()
caption('Hypothetical teaching cases · No student information or grades are collected.')
