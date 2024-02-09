import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import calendar
from datetime import datetime
from streamlit_option_menu import option_menu
import mongodb as db


# two lists for the different incomes and expenses
incomes = ["Salary", "Other Income"]
expenses = ["Rent", "Groceries", "Utilities", "Shopping", "Insurance", "Other Expenses"]
currency = "USD"
currency_symbol = "$"
page_title = "Income and Expenses Tracker"
page_icon = ":money_with_wings:"
layout = "centered"

st.set_page_config(page_title, page_icon, layout)
st.title(page_title + " " + page_icon)


# hide streamlit style
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


years = [datetime.today().year, datetime.today().year + 1]
months = list(calendar.month_name)[1:]

def get_all_periods():
    items = db.fetch_all_periods()
    periods = [item["_id"] for item in items]
    return periods


selected = option_menu(menu_title=None,
                       options=["Data Entry", "Data Visualization"],
                       icons=["pencil-fill", "bar-chart-fill"],
                       orientation="horizontal") # more icons: https://icons.getbootstrap.com/

if selected == "Data Entry":
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox("Select Month", months, key="month")
        col2.selectbox("Select Year", years, key="year")

        "---"
        with st.expander("Income"):
            for income in incomes:
                st.number_input(f"{income}:", min_value=0, format="%i", key=income, step=100, help=f"Enter your {income} in {currency_symbol}")
        with st.expander("Expenses"):
            for expense in expenses:
                st.number_input(f"{expense}:", min_value=0, format="%i", key=expense, step=100, help=f"Enter your {expense} in {currency_symbol}")
        with st.expander("Comments"):
            st.text_area("", placeholder="Enter any comments here", key="comments")

        "---"
        col1, col2, col3 = st.columns([1, 1, 1])
        submit_button = col2.form_submit_button("Submit", use_container_width=True)
        if submit_button:
            period = str(st.session_state.year) + " " + str(st.session_state.month)
            incomes = {income: st.session_state[income] for income in incomes}
            expenses = {expense: st.session_state[expense] for expense in expenses}
            comment = st.session_state.comments

            # st.write(f"Period: {period}")
            # st.write("Incomes:", incomes)
            # st.write("Expenses:", expenses)

            # check if period already exists
            if period in get_all_periods():
                st.error("Record already exists!")
            else:
                db.insert_period(period, incomes, expenses, comment)
                st.success("Data submitted successfully!")

elif selected == "Data Visualization":
    # plot periods
    st.header("Data Visualization")
    with st.form("saved_periods"):
        # get data from db
        period = st.selectbox("Select Period", get_all_periods())
        col1, col2, col3 = st.columns([1, 1, 1])
        submit_button = col2.form_submit_button("Plot", use_container_width=True)
        if submit_button:
            period_data = db.get_period(period)
            comment = period_data.get("comment")
            incomes = period_data.get("incomes")
            expenses = period_data.get("expenses")
            # comment = "Some comment"
            # incomes = {"Salary": 1000, "Other Income": 200}
            # expenses = {"Rent": 500, "Groceries": 200, "Utilities": 100, "Shopping": 300, "Insurance": 100, "Other Expenses": 100}

            # metrics
            total_income = sum(incomes.values())
            total_expense = sum(expenses.values())
            remaining_budget = total_income - total_expense
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"{currency_symbol}{total_income}")
            col2.metric("Total Expense", f"{currency_symbol}{total_expense}")
            col3.metric("Remaining Budget", f"{currency_symbol}{remaining_budget}")
            st.text(f"Comments: {comment}")

            # create a sankey diagram
            labels = list(incomes.keys()) + ["Total Income"] + list(expenses.keys())
            source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
            target = [len(incomes)] * len(incomes) + [labels.index(expense) for expense in expenses]
            values = list(incomes.values()) + list(expenses.values())
            # Assigning unique rgba colors to each node and link
            income_colors = ['rgba(31, 119, 180, 0.2)', 'rgba(255, 127, 14, 0.4)']  # Example rgba colors for incomes
            expense_colors = ['rgba(44, 160, 44, 0.4)', 'rgba(214, 39, 40, 0.4)', 'rgba(148, 103, 189, 0.4)', 'rgba(140, 86, 75, 0.4)', 'rgba(227, 119, 194, 0.4)', 'rgba(127, 127, 127, 0.4)']  # Example rgba colors for expenses
            total_income_color = ['rgba(160, 0, 200, 0.8)']  # rgba color for "Total Income" node
            
            
            node_colors = ['rgba(31, 119, 180, 0.8)', 'rgba(255, 127, 14, 0.8)', 'rgba(160, 0, 200, 0.8)', 
                        'rgba(44, 160, 44, 0.8)', 'rgba(214, 39, 40, 0.8)', 'rgba(148, 103, 189, 0.8)', 
                        'rgba(140, 86, 75, 0.8)', 'rgba(227, 119, 194, 0.8)', 'rgba(127, 127, 127, 0.8)']
            
            # node_colors = income_colors + total_income_color + expense_colors

            # Colors for links - using similar rgba values with perhaps different alpha values for distinction
            link_colors = income_colors + expense_colors  # Using the same colors for simplicity

            link = dict(source=source, target=target, value=values, color=link_colors)
            node = dict(label=labels, pad=15, thickness=15, color=node_colors)


        
            # link = dict(source=source, target=target, value=values)
            # node = dict(label=labels, pad=15, thickness=15, color='rgba(255, 0, 255, 0.6)')
            data = go.Sankey(link=link, node=node)

            fig = go.Figure(data)
            fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
            st.plotly_chart(fig, use_container_width=True)
