import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math
import seaborn as sns

min_profits_interest = 0.15
operational_impact = {
    "Fund Manager": 0.45,
    "Data Manager": 0.25,
    "Legal Manager": 0.30
}

if "fund_manager" not in st.session_state:
    st.session_state.fund_manager = 0.0
if "data_manager" not in st.session_state:
    st.session_state.data_manager = 0.0
if "legal_manager" not in st.session_state:
    st.session_state.legal_manager = 0.0
if "operational_expenses" not in st.session_state:
    st.session_state.operational_expenses = 0.0
if "management_fee" not in st.session_state:
    st.session_state.management_fee = 0.0
if "snp500_return" not in st.session_state:
    st.session_state.snp500_return = 0.0
if "fund_return" not in st.session_state:
    st.session_state.fund_return = 0.0

def allocate_split(amount, partner_pct, manager_pct):
    partner_split = amount * (partner_pct / 100)
    manager_split = amount * (manager_pct / 100)
    return manager_split, partner_split

def money_format(x):
    return f"${x:,.2f}"

#st.title("Distribution Waterfall Calculator")

st.markdown(
    "<h1 style='white-space: nowrap; margin-top: 0;'>Quarterly Distribution Waterfall Calculator</h1>",
    unsafe_allow_html=True
)

st.write("### Financial Inputs")
col1, col2 = st.columns(2)

#with col2:
#    st.markdown(
#        "<div style='height: var(--input-height, 56px);'></div>",
#        unsafe_allow_html=True
#    )

with col2.expander("Manager Salaries"):
    fund_manager_salary = st.number_input("Fund Manager ($)", min_value=0.0, value=0.0)
    data_manager_salary = st.number_input("Data Manager ($)", min_value=0.0, value=0.0)
    legal_manager_salary = st.number_input("Legal Manager ($)", min_value=0.0, value=0.0)

aum = col2.number_input("Assets Under Management (in $)", min_value=0.0, value=2000000.0)

with col1.expander("Contributions per Manager"):
    fund_manager = st.number_input("Fund Manager ($)", min_value=0.0, max_value = aum, 
                                   key="fund_manager")
    data_manager = st.number_input("Data Manager ($)", min_value=0.0, max_value = aum, 
                                   key="data_manager")
    legal_manager = st.number_input("Legal Manager ($)", min_value=0.0, max_value = aum, 
                                   key="legal_manager")

detailed_total = fund_manager + data_manager + legal_manager
if detailed_total > aum:
    st.error("⚠️ Manager contributions cannot exceed total AUM.")
    maanger_contributions = 0
else:
    manager_contributions = detailed_total

col1.number_input("Manager Contributions (in $)", min_value=0.0, value=manager_contributions, disabled=True)

snp500_return = col1.number_input("S&P 500 Return (in %)", min_value=0.0, 
                                key="snp500_return")
fund_return = col2.number_input("Fund Return (in %)", min_value=0.0, 
                                key="fund_return")


# AUM depedent calculations
max_liquidity_reserve = aum * 0.03
max_additional_liquidity_reserve = aum * 0.12
investor_contributions = aum - manager_contributions

if manager_contributions > 0:
    fund_manager_pct = fund_manager / manager_contributions
    data_manager_pct = data_manager / manager_contributions
    legal_manager_pct = legal_manager / manager_contributions
else:
    fund_manager_pct = data_manager_pct = legal_manager_pct = (1.0 / 3.0)

liquidity_reserve = col1.number_input("Liquidity Reserve (in $)", min_value=0.0, max_value = max_liquidity_reserve, value=0.0)
operational_expenses = col2.number_input("Operational Expenses (in $)", min_value=0.0, 
                                         key="operational_expenses")
additional_liquidity_reserve = col1.number_input("Additional Liquidity Reserve (in $)", min_value=0.0, max_value = max_additional_liquidity_reserve, value=0.0)
management_fee = col2.number_input("Management Fee (in %)", min_value=0.0, max_value = 2.0, 
                                   key="management_fee")

# Calculate NAV and profit splits
start_nav = aum
end_nav = aum + (aum * (fund_return / 100))
management_fee_amt = aum * (management_fee / 100)
manager_salaries = fund_manager_salary + data_manager_salary + legal_manager_salary
net_profits = (end_nav - start_nav) - liquidity_reserve - operational_expenses - additional_liquidity_reserve - management_fee_amt - manager_salaries
remaining_nav = net_profits

fund_manager_returns = [0, fund_manager_salary, management_fee_amt * 0.45]
data_manager_returns = [0, data_manager_salary, management_fee_amt * 0.25]
legal_manager_returns = [0, legal_manager_salary, management_fee_amt * 0.30]
investor_returns = [0, 0, 0]
remaining_navs = [end_nav - start_nav, net_profits + manager_salaries, net_profits + management_fee_amt]

if aum > 0:
    manager_investor_share = manager_contributions / aum
else:
    manager_investor_share = 0

if manager_investor_share < min_profits_interest:
    manager_investor_share = min_profits_interest

hurdle_return = start_nav * (snp500_return / 100)
fund_manager_return = hurdle_return * (fund_manager / aum)
data_manager_return = hurdle_return * (data_manager / aum)
legal_manager_return = hurdle_return * (legal_manager / aum)
investor_return = hurdle_return * (investor_contributions / aum)
fund_manager_returns.append(fund_manager_return)
data_manager_returns.append(data_manager_return)
legal_manager_returns.append(legal_manager_return)
investor_returns.append(investor_return)
remaining_navs.append(remaining_nav)
remaining_nav -= hurdle_return

tier1_cap = start_nav * 0.0625
tier1_cap = min(tier1_cap, remaining_nav)
tier1_managers, tier1_partners = allocate_split(tier1_cap, 80, 20)
fund_manager_return += tier1_managers * 0.45
data_manager_return += tier1_managers * 0.25
legal_manager_return += tier1_managers * 0.30
investor_return += tier1_partners
fund_manager_returns.append(tier1_managers * 0.45)
data_manager_returns.append(tier1_managers * 0.25)
legal_manager_returns.append(tier1_managers * 0.30)
investor_returns.append(tier1_partners)
remaining_navs.append(remaining_nav)
remaining_nav -= tier1_cap

tier2_cap = start_nav * 0.0625
tier2_cap = min(tier2_cap, remaining_nav)
tier2_managers, tier2_partners = allocate_split(tier2_cap, 75, 25)
tier2_managers_profit_interests = tier2_partners * manager_investor_share
tier2_managers += tier2_managers_profit_interests
tier2_partners -= tier2_managers_profit_interests
fund_manager_return += tier2_managers * fund_manager_pct
data_manager_return += tier2_managers * data_manager_pct
legal_manager_return += tier2_managers * legal_manager_pct
investor_return += tier2_partners
fund_manager_returns.append(tier2_managers * fund_manager_pct)
data_manager_returns.append(tier2_managers * data_manager_pct)
legal_manager_returns.append(tier2_managers * legal_manager_pct)
investor_returns.append(tier2_partners)
remaining_navs.append(remaining_nav)
remaining_nav -= tier2_cap

tier3_cap = remaining_nav
tier3_managers, tier3_partners = allocate_split(tier3_cap, 50, 50)
tier3_managers_profit_interests = tier3_partners * manager_investor_share
tier3_managers += tier3_managers_profit_interests
tier3_partners -= tier3_managers_profit_interests
fund_manager_return += tier3_managers * fund_manager_pct
data_manager_return += tier3_managers * data_manager_pct
legal_manager_return += tier3_managers * legal_manager_pct
investor_return += tier3_partners
fund_manager_returns.append(tier3_managers * fund_manager_pct)
data_manager_returns.append(tier3_managers * data_manager_pct)
legal_manager_returns.append(tier3_managers * legal_manager_pct)
investor_returns.append(tier3_partners)
remaining_navs.append(remaining_nav)


total_managers = fund_manager_return + data_manager_return + legal_manager_return
total_partners = investor_return

fund_manager_returns.append(fund_manager_return + fund_manager_returns[1] + fund_manager_returns[2])
data_manager_returns.append(data_manager_return + data_manager_returns[1] + data_manager_returns[2])
legal_manager_returns.append(legal_manager_return + legal_manager_returns[1] + legal_manager_returns[2])
investor_returns.append(total_partners)
remaining_navs.append(0)

st.write("### NAV Breakdown")
col1, col2 = st.columns(2)
col1.metric(label="Starting NAV", value=f"${start_nav:,.2f}")
col1.metric(label="Net Profits", value=f"${net_profits:,.2f}")
col2.metric(label="Managers' Return", value=f"${total_managers:,.2f}")
col2.metric(label="Investors' Return", value=f"${total_partners:,.2f}")

returns_breakdown = {
    "Fund Manager": fund_manager_return,
    "Data Manager": data_manager_return,
    "Legal Manager": legal_manager_return,
    "Investors": total_partners
}

labels = list(returns_breakdown.keys())
values = list(returns_breakdown.values())

df = pd.DataFrame({"Entity": labels, "Returns": values})

fig, ax = plt.subplots()
sns.barplot(x="Entity", y="Returns", data=df, edgecolor="black", hue="Entity", legend=False,
            palette=["cyan", "deeppink", "mediumspringgreen", "mediumslateblue"], ax=ax)
ax.set_ylabel("Returns ($)")
ax.set_title("Quarterly Profits Split")
ax.set_ylim(0, max(values) * 1.2)  # add some headroom
for i, v in enumerate(values):
    ax.text(i, v + max(values)*0.02, f"${v:,.0f}", ha="center", fontweight='bold')

with st.expander("Net Profits Split Visualization"):
    st.pyplot(fig)


manager_returns = []
for i in range(len(fund_manager_returns)):
    manager_returns.append(fund_manager_returns[i] + data_manager_returns[i] + legal_manager_returns[i])

waterfall_df = pd.DataFrame(
    data = {
    "Fund Manager": fund_manager_returns,
    "Data Manager": data_manager_returns,
    "Legal Manager": legal_manager_returns,
    "Investors": investor_returns,
    "Profits": remaining_navs,
    "Managers": manager_returns
    },
    index = [
        "Start", "Salary", "Mgt. Fee", "Hurdle Return", "80/20 Split", "75/25 Split", "50/50 Split", "Total"]
)

waterfall_df = waterfall_df.map(money_format)

st.write("### Waterfall Breakdown")
st.write(waterfall_df)