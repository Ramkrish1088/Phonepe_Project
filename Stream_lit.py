# phonepe_dashboard_app.py  #python -m streamlit run Stream_lit.py
import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import requests
import json

# --- DB Connection ---
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ramkrish9159981599",
        database="db_phonepe"
    )

def execute_query(query, params=None):
    try:
        with get_db_connection() as mydb:
            cursor = mydb.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
        return pd.DataFrame(result)
    except mysql.connector.Error as err:
        st.error(f"Error executing query: {err}")
        return pd.DataFrame()

# --- Global Config ---
st.set_page_config(page_title="PhonePe Dashboard", layout="wide")
GEO_URL = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
geo = json.loads(requests.get(GEO_URL).content)
quarter_map = {
    "Q1 (Jan-Mar)": 1,
    "Q2 (Apr-Jun)": 2,
    "Q3 (Jul-Sep)": 3,
    "Q4 (Oct-Dec)": 4
}
# Query wrapper
def run_query(query, params=None):
    conn = get_db_connection()
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# --- Custom CSS for Sidebar ---
st.markdown("""
    <style>
    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #1E1E2F;
        padding: 1rem 0.5rem;
    }
    .sidebar-title {
        font-size: 1.4rem;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .menu-item {
        display: flex;
        align-items: center;
        padding: 12px 15px;
        margin: 8px 0;
        font-size: 1.05rem;
        color: #ccc;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
    }
    .menu-item:hover {
        background-color: #4E89FF;
        color: white;
    }
    .menu-item i {
        margin-right: 10px;
    }
    .menu-selected {
        background-color: #4E89FF;
        color: white !important;
        font-weight: bold;
    }   
    </style>
""", unsafe_allow_html=True)


menu_options = {
    "Home": "🏡",
    "Business Case Study": "📂",
    "Case Study Dashboard": "📑"
}

if "menu" not in st.session_state:
    st.session_state["menu"] = "Home"

for name, icon in menu_options.items():
    if st.sidebar.button(f"{icon} {name}", key=name):
        st.session_state["menu"] = name

section = st.session_state["menu"]

# --- Page Content ---
if section == "Home":    
    st.markdown(
    """
    <h1 style='text-align: center;'>Welcome to the PhonePe Dashboard!</h1>
    """,
    unsafe_allow_html=True
    )
    st.markdown("<h1 style='text-align: center; font-weight: normal;'>Explore insights and analytics related to PhonePe transactions across <strong>India</strong>.</h1>", unsafe_allow_html=True)

# Expander sections for each highlight
    with st.expander("📈 Transaction Trends"):
        st.write("Track volumes by type, state, and district over time.")

    with st.expander("👥 User Engagement"):
        st.write("Understand how users interact with the app across states and districts.")

    with st.expander("🛡 Insurance Analytics"):
        st.write("Analyze adoption of insurance services at state and district levels.")

    with st.expander("🌐 Interactive Visuals"):
        st.write("Visualize data using charts, maps, and filters for interactive exploration.")

elif section == "Business Case Study":
    st.title("📂 Business Case Study")
    sub_tab = st.selectbox("Explore analytics by:", ["Transaction", "User", "Insurance"])

    # Year & Quarter Dropdown (once only)
    years = ["All"] + [str(y) for y in range(2018, 2025)]
    quarters = ["All"] + list(quarter_map.keys())

    col1, col2 = st.columns(2)
    selected_year = st.sidebar.selectbox("Select Year", options=years)
    selected_quarter = st.sidebar.selectbox("Select Quarter", options=quarters)

    year = int(selected_year) if selected_year != "All" else None
    quarter = quarter_map[selected_quarter] if selected_quarter != "All" else None

    conditions = []
    params = []

    if year is not None:
        conditions.append("Years = %s")
        params.append(year)
    if quarter is not None:
        conditions.append("Quarter = %s")
        params.append(quarter)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    if sub_tab == "Transaction":
        st.subheader("💳 Transaction Overview")

        df = execute_query(f"""
            SELECT SUM(Transaction_count) AS TotalTransactions,
                   AVG(Transaction_count) AS AvgTransactions,
                   SUM(Transaction_amount) AS TotalRevenue,
                   AVG(Transaction_amount) AS AvgRevenue
            FROM aggregate_transaction
            {where_clause}
        """, tuple(params))

        st.markdown(f"""
    <style>
    .card-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin-top: 30px;
    }}
    .card {{
        background: #f1f3f6;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        text-align: center;
        transition: all 0.3s ease;
    }}
    .card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    .card-title {{
        font-size: 1rem;
        color: #444;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}
    .card-value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: #111;
    }}
    </style>

    <div class="card-grid">
        <div class="card">
            <div class="card-title">Total Transactions</div>
            <div class="card-value">{df['TotalTransactions'][0]:,}</div>
        </div>
        <div class="card">
            <div class="card-title">Total Revenue (₹)</div>
            <div class="card-value">{df['TotalRevenue'][0]:,.2f}</div>
        </div>
        <div class="card">
            <div class="card-title">Average Transactions</div>
            <div class="card-value">{df['AvgTransactions'][0]:,.2f}</div>
        </div>
        <div class="card">
            <div class="card-title">Avg Revenue (₹)</div>
            <div class="card-value">{df['AvgRevenue'][0]:,.2f}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

        df_map = execute_query(f"""
            SELECT States, SUM(Transaction_count) AS TotalTransactions
            FROM map_transaction
            {where_clause}
            GROUP BY States
        """, tuple(params))

        fig = px.choropleth(df_map, geojson=geo, locations="States",
                            featureidkey="properties.ST_NM", color="TotalTransactions",
                            color_continuous_scale="Reds", title="State-wise Total Transactions")
        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📌 Top 10 States by Transaction Volume")
        df_top = df_map.sort_values(by="TotalTransactions", ascending=False).head(10)
        st.dataframe(df_top, use_container_width=True)

    elif sub_tab == "User":
        st.subheader(" User Engagement and Growth Strategy")

        df_total = execute_query(f"""
            SELECT SUM(RegisteredUser) as TotalUsers, SUM(AppOpens) as TotalOpens 
            FROM map_user {where_clause}
        """, tuple(params))

        if not df_total.empty:
            st.metric("**🧑‍💻 Total Registered Users**", f"{int(df_total.iloc[0]['TotalUsers']):,}")
            st.metric("**📱Total App Opens**", f"{int(df_total.iloc[0]['TotalOpens']):,}")

        tab1, = st.tabs(["States"])
        with tab1:
            df_states = execute_query(f"""
                SELECT States, SUM(RegisteredUser) as TotalUsers 
                FROM map_user {where_clause} 
                GROUP BY States ORDER BY TotalUsers DESC LIMIT 10
            """, tuple(params))
            if not df_states.empty:
                st.markdown("#### 🏆 Top 10 States by Registered Users")
                st.dataframe(df_states, use_container_width=True)
        

    elif sub_tab == "Insurance":
        st.subheader("🛡 Insurance Engagement Insights")

        df_total = execute_query(f"""
            SELECT SUM(Transaction_count) as TotalTransactions, SUM(Transaction_amount) as TotalAmount
            FROM map_insurance {where_clause}
        """, tuple(params))

        if not df_total.empty:
            total_transactions = df_total.iloc[0].get('TotalTransactions')
            total_amount = df_total.iloc[0].get('TotalAmount')

            st.metric(
                "Total Insurance Transactions",
                f"{int(total_transactions):,}" if total_transactions is not None else "N/A"
            )

            st.metric(
                "Total Insurance Amount (₹)",
                f"{int(total_amount):,}" if total_amount is not None else "N/A"
            )
        else:
            st.metric("Total Insurance Transactions", "N/A")
            st.metric("Total Insurance Amount (₹)", "N/A")

        tab1,= st.tabs(["States"])

        with tab1:
            df_states = execute_query(f"""
                SELECT States, SUM(Transaction_count) as TotalTransactions
                FROM map_insurance {where_clause}
                GROUP BY States ORDER BY TotalTransactions DESC LIMIT 10
            """, tuple(params))
            if not df_states.empty:
                st.markdown("#### 🏆 Top 10 States by Insurance Transactions")
                st.dataframe(df_states, use_container_width=True)
        

elif section == "Case Study Dashboard":
    st.title("📑 Case Study Dashboard")
         # Year and Quarter Filters
    years = ["All"] + [str(y) for y in range(2018, 2025)]
    quarters = ["All"] + list(quarter_map.keys())

    col1, col2 = st.columns(2)
    selected_year = col1.selectbox("Select Year", years)
    selected_quarter = col2.selectbox("Select Quarter", quarters)

    year = int(selected_year) if selected_year != "All" else None
    quarter = quarter_map[selected_quarter] if selected_quarter != "All" else None

    conditions = []
    params = []

    if year is not None:
        conditions.append("Years = %s")
        params.append(year)
    if quarter is not None:
        conditions.append("Quarter = %s")
        params.append(quarter)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    case_option = st.selectbox("Select Case Study", [
        "Decoding Transaction Dynamics",
        "Device Dominance and User Engagement",
        "Insurance Penetration and Growth Potential",
        "Transaction Analysis for Market Expansion",
        "User Engagement and Growth Strategy"
    ])
    if case_option == "Decoding Transaction Dynamics":
        # 1. Average Transaction Amount by Transaction Type
        df_avg_amount = execute_query(
            f"""
            SELECT Transaction_type, AVG(Transaction_amount) AS AvgAmount 
            FROM aggregate_transaction 
            {where_clause} 
            GROUP BY Transaction_type
            """,
            tuple(params)
        )
        st.plotly_chart(
            px.bar(
                df_avg_amount, 
                x="Transaction_type", 
                y="AvgAmount", 
                title="Distribution of Transactions Across Types",
                color="Transaction_type",
                color_discrete_sequence=px.colors.sequential.Plasma
            )
        )

        # 2. Min and Max Transaction Amount Over Years
        df_min_max = execute_query(
            f"""
            SELECT Years, 
                MIN(Transaction_amount) AS MinAmount, 
                MAX(Transaction_amount) AS MaxAmount
            FROM aggregate_transaction
            {where_clause}
            GROUP BY Years
            """,
            tuple(params)
        )
        fig_min_max = px.line(
            df_min_max, 
            x="Years", 
            y=["MinAmount", "MaxAmount"], 
            markers=True,
            title="Transaction Amount Growth Over Years",
            labels={"value": "Transaction Amount", "variable": "Metric"},
            color_discrete_sequence=["green", "red"]
        )
        st.plotly_chart(fig_min_max)

        # 3. Total Transaction Amount by State (Map)
        df_amount_by_state = execute_query(
            f"""
            SELECT States, SUM(Transaction_amount) AS TotalAmount
            FROM map_transaction
            {where_clause}
            GROUP BY States
            """,
            tuple(params)
        )
        fig_amount_map = px.choropleth(
            df_amount_by_state, 
            geojson=geo, 
            locations="States", 
            featureidkey="properties.ST_NM", 
            color="TotalAmount",
            title="Geographical Distribution of Transactions",
            color_continuous_scale="Viridis"
        )
        fig_amount_map.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig_amount_map)

        # 4. Top 5 Transaction Types by Total Amount
        df_top_amount_types = execute_query(
            f"""
            SELECT Transaction_type, SUM(Transaction_amount) AS TotalAmount
            FROM aggregate_transaction
            {where_clause}
            GROUP BY Transaction_type
            ORDER BY TotalAmount DESC
            LIMIT 5
            """,
            tuple(params)
        )
        st.plotly_chart(
            px.bar(
                df_top_amount_types, 
                x="Transaction_type", 
                y="TotalAmount", 
                title="Leading Transaction Categories by Amount",
                color="Transaction_type",
                color_discrete_sequence=px.colors.sequential.Magenta
            )
        )

    elif case_option == "Device Dominance and User Engagement":
        df_retention_proxy = execute_query(f"""
            SELECT au.Brands, au.Years, au.Quarter, SUM(mu.AppOpens) AS AppOpens
            FROM aggregate_user au
            JOIN map_user mu ON au.States = mu.States AND au.Years = mu.Years AND au.Quarter = mu.Quarter
            {where_clause.replace('Years', 'au.Years').replace('Quarter', 'au.Quarter')}
            GROUP BY au.Brands, au.Years, au.Quarter
            ORDER BY au.Brands, au.Years, au.Quarter
        """, tuple(params))

        df_retention_proxy["Time"] = df_retention_proxy["Years"].astype(str) + "-Q" + df_retention_proxy["Quarter"].astype(str)

        st.plotly_chart(
            px.line(
                df_retention_proxy, x="Time", y="AppOpens", color="Brands", 
                title="Quarterly App Opens Trend by Brand",
                markers=True, color_discrete_sequence=px.colors.qualitative.Safe
            )
        )
        df_top_brand_state = execute_query(f"""
            SELECT States, Brands, SUM(Transaction_count) AS Users
            FROM aggregate_user
            {where_clause}
            GROUP BY States, Brands
        """, tuple(params))

        # Get the top brand per state
        df_top_brand = df_top_brand_state.loc[df_top_brand_state.groupby("States")["Users"].idxmax()]

        st.plotly_chart(
            px.bar(
                df_top_brand, x="States", y="Users", color="Brands",
                title="Most Used Device Brand by State",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
        )
                

    elif case_option == "Insurance Penetration and Growth Potential":
        df_state_yearly = execute_query(
            f"SELECT States, Years, SUM(Total_count) AS TotalCount FROM aggregated_insurance {where_clause} GROUP BY States, Years",
            tuple(params)
        )
        st.plotly_chart(
            px.bar(
                df_state_yearly.sort_values(by="TotalCount", ascending=False),
                x="States", y="TotalCount", color="Years",
                title="Insurance Transactions by State and Year",
                barmode="group", color_discrete_sequence=px.colors.sequential.Viridis
            )
        )

        df_avg_state = execute_query(
            f"SELECT States, AVG(Total_count) AS AvgCount FROM aggregated_insurance {where_clause} GROUP BY States",
            tuple(params)
        )
        st.plotly_chart(
            px.pie(
                df_avg_state.sort_values(by="AvgCount", ascending=True).head(10),
                names="States", values="AvgCount",
                title="Least Penetrated States by Avg Yearly Count"
            )
        )

    elif case_option == "Transaction Analysis for Market Expansion":
        df_by_type = execute_query(f"""
            SELECT Transaction_type, SUM(Transaction_amount) AS Amount
            FROM aggregate_transaction
            {where_clause}
            GROUP BY Transaction_type
        """, tuple(params))

        st.plotly_chart(
            px.bar(
                df_by_type, x="Transaction_type", y="Amount",
                title="Transaction Value by Type",
                color_discrete_sequence=px.colors.qualitative.Dark2
            )
        )
        df_map_amt = execute_query(f"SELECT States, SUM(Transaction_amount) AS TotalAmount FROM map_transaction {where_clause} GROUP BY States", tuple(params))
        fig = px.choropleth(df_map_amt, geojson=geo, locations="States", featureidkey="properties.ST_NM", color="TotalAmount", color_continuous_scale="Purples", title="State-wise Market Value Map")
        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig)

    elif case_option == "User Engagement and Growth Strategy":
        df_app = execute_query(f"SELECT States, SUM(AppOpens) AS Opens FROM map_user {where_clause} GROUP BY States", tuple(params))
        st.plotly_chart(px.bar(df_app.sort_values(by="Opens", ascending=False).head(10), x="States", y="Opens", title="Top States by App Opens", color="States", color_discrete_sequence=px.colors.sequential.Mint))
       
        df_districts = execute_query(f"SELECT Districts, SUM(RegisteredUser) AS Users FROM map_user {where_clause} GROUP BY Districts ORDER BY Users DESC LIMIT 10", tuple(params))
        st.plotly_chart(px.pie(df_districts, names="Districts", values="Users", title="Top Districts by Registrations Share"))

    

    
       
        




    
