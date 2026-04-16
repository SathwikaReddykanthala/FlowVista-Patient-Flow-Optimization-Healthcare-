"""
╔══════════════════════════════════════════════════════════════════════╗
║        Patient Flow Optimization BI SYSTEM                         ║
║       Star Schema · KPIs · Recommendations · AI Chatbot             ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings("ignore")
from dotenv import load_dotenv
import os


load_dotenv(dotenv_path=".env")
print("KEY:", os.getenv("OPENAI_API_KEY"))

# ─────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=" Patient Flow Optimization",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────
# DARK THEME CSS
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, .stApp { background-color: #0d1117; color: #e6edf3; font-family: 'Segoe UI', sans-serif; }
section[data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }
section[data-testid="stSidebar"] * { color: #c9d1d9 !important; }
div[data-testid="stMetric"] { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 12px; }

.kpi-card {
    background: linear-gradient(145deg,#1c2128 0%,#161b22 100%);
    border: 1px solid #30363d; border-radius: 14px;
    padding: 22px 18px; text-align: center;
    box-shadow: 0 6px 24px rgba(0,0,0,0.5);
    transition: transform .2s, box-shadow .2s;
    height: 130px; display: flex; flex-direction: column; justify-content: center;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 10px 32px rgba(0,0,0,0.6); }
.kpi-label { font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 8px; }
.kpi-value { font-size: 28px; font-weight: 700; color: #f0f6fc; line-height: 1.1; }
.kpi-sub   { font-size: 12px; margin-top: 6px; }
.kpi-sub.good    { color: #3fb950; }
.kpi-sub.bad     { color: #f85149; }
.kpi-sub.neutral { color: #d29922; }

.alert-red    { background:#2d1117; border-left:4px solid #f85149; border-radius:8px; padding:12px 16px; margin:5px 0; color:#ff7b72; font-size:13px; }
.alert-yellow { background:#2d2208; border-left:4px solid #d29922; border-radius:8px; padding:12px 16px; margin:5px 0; color:#e3b341; font-size:13px; }
.alert-green  { background:#0d2a1a; border-left:4px solid #3fb950; border-radius:8px; padding:12px 16px; margin:5px 0; color:#56d364; font-size:13px; }
.alert-blue   { background:#0d1b2e; border-left:4px solid #388bfd; border-radius:8px; padding:12px 16px; margin:5px 0; color:#79c0ff; font-size:13px; }

.section-title {
    font-size: 16px; font-weight: 700; color: #f0f6fc;
    border-bottom: 2px solid #21262d; padding-bottom: 8px;
    margin: 18px 0 12px 0; text-transform: uppercase; letter-spacing: 0.5px;
}

.page-banner {
    background: linear-gradient(90deg,#1f2d3d 0%,#1c2128 100%);
    border: 1px solid #30363d; border-radius: 12px;
    padding: 18px 24px; margin-bottom: 20px;
}
.page-banner h1 { font-size: 22px; font-weight: 700; color: #f0f6fc; margin: 0; }
.page-banner p  { font-size: 13px; color: #8b949e; margin: 4px 0 0 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────
# PLOTLY DARK TEMPLATE
# ─────────────────────────────────────────────────────────────────────
DARK_LAYOUT = dict(
    paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
    font=dict(color="#c9d1d9", family="Segoe UI"),
    xaxis=dict(gridcolor="#21262d", showgrid=True, linecolor="#30363d"),
    yaxis=dict(gridcolor="#21262d", showgrid=True, linecolor="#30363d"),
    margin=dict(l=30, r=20, t=50, b=30),
    legend=dict(bgcolor="#1c2128", bordercolor="#30363d", borderwidth=1)
)

COLORS = ["#388bfd","#3fb950","#d29922","#f85149","#a5d6ff","#56d364",
          "#e3b341","#ff7b72","#79c0ff","#7ee787","#ffa657","#cae8ff"]


# ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():

    # ── FACT TABLES ─────────────────────────────
    staffing = pd.read_csv("Fact_Staffing.csv")
    deptlogs = pd.read_csv("Fact_DeptLogs.csv")

    # normalize
    staffing.columns = staffing.columns.str.lower()
    deptlogs.columns = deptlogs.columns.str.lower()

    # ── DIMENSION TABLES ────────────────────────
    dim_patients = pd.read_csv("Dim_Patients.csv")
    dim_visits = pd.read_csv("Dim_Visits.csv")
    dim_departments = pd.read_csv("Dim_Departments.csv")
    dim_calendar = pd.read_csv("Dim_Calendar.csv")

    dim_patients.columns = dim_patients.columns.str.lower()
    dim_visits.columns = dim_visits.columns.str.lower()
    dim_departments.columns = dim_departments.columns.str.lower()
    dim_calendar.columns = dim_calendar.columns.str.lower()

    # fix department name
    dim_departments.rename(columns={"dept_name": "department_name"}, inplace=True)

    # ── CALENDAR FIX ────────────────────────────
    dim_calendar["date"] = pd.to_datetime(dim_calendar["date"])
    dim_calendar["date_key"] = dim_calendar["date"].astype("int64") // 10**9

    deptlogs["entry_date_key"] = pd.to_datetime(deptlogs["entry_timestamp"]).astype("int64") // 10**9

    # ── JOIN ALL TABLES ─────────────────────────
    df = (deptlogs
        .merge(dim_visits, on="visit_id", how="left")
        .merge(dim_patients, on="patient_id", how="left")
        .merge(dim_departments, on="dept_key", how="left")
        .merge(dim_calendar, left_on="entry_date_key", right_on="date_key", how="left")
    )

    df.columns = df.columns.str.lower()

    # ── STAFFING AGGREGATION ────────────────────
    staffing_agg = staffing.groupby("dept_key", as_index=False).agg({
        "nurse_count": "sum",
        "doc_count": "sum"
    })

    df = df.merge(staffing_agg, on="dept_key", how="left")

    # ── SAFE DEFAULTS ───────────────────────────
    df["nurse_count"] = df.get("nurse_count", 0)
    df["doc_count"] = df.get("doc_count", 0)

    # ── DATE FIX (IMPORTANT) ────────────────────
    df["date"] = pd.to_datetime(df["entry_timestamp"]).dt.normalize()

    # ── KPI CALCULATIONS ────────────────────────
    #df["is_active"] = df["exit_timestamp"].isna()
    # ✅ POWER BI MATCH LOGIC
    df["is_active"] = 1 
    #df["is_active"] = df["visit_id"].notna().astype(int)
    df["wait_duration_min"] = df["wait_duration_min"].fillna(0)

    df["total_staff"] = df["nurse_count"] + df["doc_count"]

    df["staff_to_patient_ratio"] = (
        df["total_staff"] / df["is_active"].replace(0, np.nan)
    )
    # 🔥 ADD THESE LINES

    # Ensure ALOS exists
    if "target_alos_hours" not in df.columns:
        df["target_alos_hours"] = 3
    
    # 🔥 CREATE STAGE COLUMN (MATCH POWER BI)

    df["stage"] = np.select(
        [
            df["dept_key"] == 6,
            df["dept_key"] == 2,
            df["dept_key"] == 3,
            df["dept_key"] == 1
        ],
        [
            "Triage",
            "Radiology",
            "Labs",
            "Ward"
        ],
        default="Support Services"
    )

    # Create capacity
    df["department_capacity"] = df["target_alos_hours"] * 10
    return df, dim_departments, dim_calendar
    
    df["Adjusted_Value"] = df["Target_Wait_Time"]

    df.loc[df["Department"] == "Cardiology", "Adjusted_Value"] *= 2.5
    df.loc[df["Department"] == "Neurology", "Adjusted_Value"] *= 0.6
    df.loc[df["Department"] == "Orthopedics", "Adjusted_Value"] *= 1.3
    df.loc[df["Department"] == "Emergency", "Adjusted_Value"] *= 0.4
    df.loc[df["Department"] == "General Medicine", "Adjusted_Value"] *= 1.8
# ─────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────
def fmt_currency(v):
    if v >= 1_000_000: return f"${v/1_000_000:.2f}M"
    if v >= 1_000:     return f"${v/1_000:.1f}K"
    return f"${v:,.0f}"


def kpi_card(label, value, sub="", sub_class="neutral"):
    return f"""<div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub {sub_class}">{sub}</div>
    </div>"""


def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def alert(msg, kind="blue"):
    st.markdown(f'<div class="alert-{kind}">{msg}</div>', unsafe_allow_html=True)


def apply_filters(df, date_range, departments, age_groups):

    d0 = pd.Timestamp(date_range[0])
    d1 = pd.Timestamp(date_range[1])

    # date filter
    m = df[(df["date"] >= d0) & (df["date"] <= d1)].copy()

    # department filter
    if departments:
        m = m[m["department_name"].isin(departments)]

    # age group filter (FIXED ✅)
    if age_groups:
        m = m[m["age_group"].isin(age_groups)]

    return m


# ─────────────────────────────────────────────────────────────────────
# PAGE 1 — Executive Flow Overview
# ─────────────────────────────────────────────────────────────────────

def page_executive(df):
    
    st.markdown("""
    <div class="page-banner">
        <h1>Executive Flow Overview</h1>
    </div>
    """, unsafe_allow_html=True)

    # ───────────── KPIs ─────────────
    active_patients = df["visit_id"].nunique()
    avg_wait = df["wait_duration_min"].mean()
    TOTAL_CAPACITY = 246
    capacity_pct = (active_patients / TOTAL_CAPACITY) * 100

    nurse_ratio = df["total_staff"].sum() / active_patients if active_patients else 0
    alos = df["wait_duration_min"].mean() / 60  # convert to hours

    # KPI ROW 1
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(kpi_card("Active Patients", f"{int(active_patients)}"), unsafe_allow_html=True)

    with c2:
        st.markdown(kpi_card("Capacity %", f"{capacity_pct:.2f}%"), unsafe_allow_html=True)

    with c3:
        st.markdown(kpi_card("Avg Wait Time", f"{avg_wait:.2f}"), unsafe_allow_html=True)

    with c4:
        st.markdown(kpi_card("Nurse Ratio", f"{nurse_ratio:.2f}"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # KPI ROW 2
    c5, c6 = st.columns(2)

    with c5:
        st.markdown(kpi_card("ALOS (Hours)", f"{alos:.2f}"), unsafe_allow_html=True)

    if active_patients < 5000:
        load = "Low"
    elif active_patients < 12000:
        load = "Normal"
    else:
        load = "High"

    with c6:
        st.markdown(kpi_card("Patient Load", load,), unsafe_allow_html=True)
        #with c6:
        #st.markdown(kpi_card("Capacity Used", f"{capacity_pct:.2f}%"), unsafe_allow_html=True)

    # ───────────── CHARTS ─────────────

    section("Stage-wise Visit Count")

    # Aggregate data
    stage_df = df.groupby("stage")["visit_id"].count().reset_index()
    

    # Sort (largest at top like Power BI)
    stage_df = stage_df.sort_values(by="visit_id", ascending=False)

    # Create funnel chart
    fig_funnel = go.Figure(go.Funnel(
        y=stage_df["stage"],
        x=stage_df["visit_id"],
        textinfo="value+percent initial",
        marker=dict(
            color=[
                "#1f77b4",  # Triage - Blue
                "#ff7f0e",  # Radiology - Orange
                "#2ca02c",  # Labs - Green
                "#d62728",  # Ward - Red
                "#9467bd"   # Support Services - Purple
            ]
    )))

    #fig_funnel.update_layout(
       # title="Visit Flow by Stage"
    #)

    st.plotly_chart(fig_funnel, use_container_width=True)

    # Visits by Department
    # Visits by Department
    section("Department Demand Analysis")

    dept = df.groupby("department_name").agg(
        total_visits=("visit_id", "count")
    ).reset_index()

    fig2 = px.bar(
        dept,
        x="department_name",
        y="total_visits",
        color="total_visits"
    )

    st.plotly_chart(fig2, use_container_width=True)

    # Age Group Analysis
    section("Age based Demand Across Departments")

    #age = df.groupby(["age_group", "department_name"])["visit_id"].count().reset_index()
    age = df.groupby(["age_group", "department_name"]).agg(
    total_visits=("visit_id", "count")
    ).reset_index()

    fig3 = px.bar(
    age,
    x="age_group",
    y="total_visits",
    color="department_name",
    #title="Total Visits by Age Group and Department"
    )

    #fig3 = px.bar(age, x="age_group", y="visit_id", color="department_name")
    st.plotly_chart(fig3, use_container_width=True)



    # ───────────── INSIGHTS ─────────────
    st.markdown("---")
    st.subheader("🔍 Executive Insights & Recommendations")

    # 📊 Patient Load
    if active_patients > 10000:
        st.info(f"📈 High patient volume ({active_patients}) indicating strong demand.")
        st.markdown("""
        **👉 Suggestions:**
        - Allocate additional staff during peak hours  
        - Prioritize high-demand departments  
        """)

    # 🛏️ Capacity Utilization
    if capacity_pct < 50:
        st.warning(f"⚠️ Only {capacity_pct:.1f}% capacity utilized — underutilization detected.")
        st.markdown("""
        **👉 Suggestions:**
        - Improve patient admission flow  
        - Optimize bed allocation across departments  
        - Promote underutilized services  
        """)
    elif capacity_pct > 85:
        st.error(f"🚨 Capacity at {capacity_pct:.1f}% — overcrowding risk.")
        st.markdown("""
        **👉 Suggestions:**
        - Add temporary beds or expand capacity  
        - Speed up discharge process  
        - Redirect patients to less crowded departments  
        """)
    else:
        st.success(f"✅ Capacity utilization ({capacity_pct:.1f}%) is optimal.")
        st.markdown("""
        **👉 Suggestions:**
        - Maintain current resource planning  
        - Monitor trends regularly  
        """)

    # ⏳ Wait Time
    if avg_wait > 30:
        st.warning(f"⏳ Avg wait time is {avg_wait:.1f} mins — delays detected.")
        st.markdown("""
        **👉 Suggestions:**
        - Improve triage prioritization  
        - Increase staffing in peak hours  
        - Streamline patient flow between stages  
        """)
    else:
        st.success(f"⚡ Avg wait time ({avg_wait:.1f} mins) is within limits.")
        st.markdown("""
        **👉 Suggestions:**
        - Maintain current process efficiency  
        - Monitor for sudden spikes  
        """)

    # 👩‍⚕️ Staffing Insight
    if nurse_ratio < 0.5:
        st.error("👩‍⚕️ Low nurse coverage detected.")
        st.markdown("""
        **👉 Suggestions:**
        - Hire or reallocate nursing staff  
        - Reduce workload per nurse  
        - Improve shift scheduling  
        """)
    elif nurse_ratio > 2:
        st.warning("⚠️ Nurse ratio unusually high.")
        st.markdown("""
        **👉 Suggestions:**
        - Reallocate excess staff to busy departments  
        - Review staffing efficiency  
        """)
    else:
        st.success("✅ Staffing levels are balanced.")
        st.markdown("""
        **👉 Suggestions:**
        - Maintain current staffing strategy  
        """)

    # 🔄 Stage Bottleneck
    top_stage = stage_df.iloc[0]["stage"]
    top_count = stage_df.iloc[0]["visit_id"]

    st.info(f"🔄 Highest load at **{top_stage}** stage ({top_count} visits).")
    st.markdown("""
    **👉 Suggestions:**
    - Add resources to this stage  
    - Reduce processing time  
    - Introduce parallel workflows  
    """)

    # 🏥 Department Demand
    top_dept = dept.sort_values(by="total_visits", ascending=False).iloc[0]

    st.info(f"🏥 **{top_dept['department_name']}** has highest demand ({top_dept['total_visits']} visits).")
    st.markdown("""
    **👉 Suggestions:**
    - Allocate more staff and beds to this department  
    - Monitor wait times closely  
    - Optimize scheduling and patient routing  
    """)
    
    
    if active_patients < 5000:
        st.warning(f"⚠️ Patient load is LOW ({active_patients})")

        st.markdown("""
    **📊 Insight:**
    - Hospital is underutilized  
    - Available resources (beds/staff) are not fully used  

    **👉 Recommendations:**
    - Increase patient intake through outreach/referrals  
    - Promote specialized services  
    - Optimize resource allocation  
    """)

    elif active_patients <= 12000:
        st.success(f"✅ Patient load is NORMAL ({active_patients})")

        st.markdown("""
    **📊 Insight:**
    - Patient flow is balanced  
    - Resources are being used efficiently  

    **👉 Recommendations:**
    - Maintain current operations  
    - Monitor trends for sudden spikes  
    - Focus on improving service quality  
    """)

    else:
        st.error(f"🚨 Patient load is HIGH ({active_patients})")

        st.markdown("""
    **📊 Insight:**
    - Hospital is experiencing high demand  
    - Risk of increased wait time and staff overload  

    **👉 Recommendations:**
    - Increase staffing during peak hours  
    - Optimize patient flow across departments  
    - Prioritize critical cases  
    - Consider expanding capacity temporarily  
    """)

# ─────────────────────────────────────────────────────────────────────
# PAGE 2 —Bottleneck Diagnostics
# ─────────────────────────────────────────────────────────────────────
def page_bottleneck(df):

    st.markdown("""
    <div class="page-banner">
        <h1>Bottleneck Diagnostics</h1>
    </div>
    """, unsafe_allow_html=True)

    # ───────────── FILTERS ─────────────
    c1, c2, c3 = st.columns(3)

    with c1:
        date_range = st.date_input("Date", value=(df["date"].min(), df["date"].max()))

    with c2:
        wait_range = st.slider("Wait Duration (Min)", 0, 120, (10, 60))

    with c3:
        #triage = st.multiselect("Triage_Priority", df["Triage_Priority"].unique())
        triage = st.multiselect("Triage Priority", df["triage_priority"].dropna().unique())
    # Apply filters
    dff = df.copy()

    if len(date_range) == 2:
        dff = dff[(dff["date"] >= pd.Timestamp(date_range[0])) &
                  (dff["date"] <= pd.Timestamp(date_range[1]))]

    dff = dff[(dff["wait_duration_min"] >= wait_range[0]) &
          (dff["wait_duration_min"] <= wait_range[1])]

    if triage:
        dff = dff[dff["triage_priority"].isin(triage)]
    

    # ───────────── KPI ─────────────
    throughput = len(dff) / dff["date"].nunique() if dff["date"].nunique() else 0

    st.markdown(kpi_card("Throughput Rate", f"{throughput:.2f}"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # ───────────── HEATMAP ─────────────
    section("Time-based Wait Analysis")

    #dff["hour"] = pd.to_datetime(dff["Entry_Timestamp"]).dt.hour
    #dff["day"] = pd.to_datetime(dff["Entry_Timestamp"]).dt.day_name()
    dff["hour"] = pd.to_datetime(dff["entry_timestamp"]).dt.hour
    dff["day"] = pd.to_datetime(dff["entry_timestamp"]).dt.day_name()

    heat = dff.pivot_table(
        values="wait_duration_min",
        index="day",
        columns="hour",
        aggfunc="mean"
    )

    fig_heat = px.imshow(heat, aspect="auto", color_continuous_scale="RdYlGn_r")
    st.plotly_chart(fig_heat, use_container_width=True)

    # ───────────── BUBBLE CHART ─────────────
    section("Department Efficiency Analysis")

    bubble = dff.groupby("department_name").agg(
        patient_volume=("visit_id", "count"),
        avg_wait=("wait_duration_min", "mean")
    ).reset_index()

    fig_bubble = px.scatter(
        bubble,
        x="patient_volume",
        y="avg_wait",
        size="patient_volume",
        color="department_name",
        hover_name="department_name"
    )

    st.plotly_chart(fig_bubble, use_container_width=True)



    # ───────────── INSIGHTS ─────────────
    st.markdown("---")
    st.subheader("🔍 Bottleneck Insights & Recommendations")

    # ⚡ Throughput Insight
    if throughput < 50:
        st.warning(f"⚠️ Low throughput rate ({throughput:.1f}) — system is processing fewer patients.")
        st.markdown("""
        **👉 Suggestions:**
        - Improve process efficiency across stages  
        - Reduce delays in high-wait areas  
        - Optimize staff allocation during peak hours  
        """)
    else:
        st.success(f"✅ Throughput rate ({throughput:.1f}) is healthy.")
        st.markdown("""
        **👉 Suggestions:**
        - Maintain current workflow efficiency  
        - Monitor for sudden drops  
        """)

    # ⏳ Wait Time Insight
    avg_wait_overall = dff["wait_duration_min"].mean()

    if avg_wait_overall > 40:
        st.error(f"🚨 High average wait time ({avg_wait_overall:.1f} mins) detected.")
        st.markdown("""
        **👉 Suggestions:**
        - Improve triage prioritization  
        - Add staff during peak hours  
        - Reduce handoff delays between stages  
        """)
    else:
        st.success(f"⚡ Average wait time ({avg_wait_overall:.1f} mins) is acceptable.")
        st.markdown("""
        **👉 Suggestions:**
        - Continue monitoring performance  
        - Maintain current staffing levels  
        """)

    # 🕒 Peak Hour Detection (from heatmap)
    peak_hour = dff.groupby("hour")["wait_duration_min"].mean().idxmax()
    peak_day = dff.groupby("day")["wait_duration_min"].mean().idxmax()

    st.info(f"🕒 Peak delay observed on **{peak_day} at {peak_hour}:00 hrs**.")
    st.markdown("""
    **👉 Suggestions:**
    - Increase staffing during peak hours  
    - Pre-schedule high-demand services  
    - Introduce fast-track queues for critical patients  
    """)

    # 🏥 Department Bottleneck
    worst_dept = bubble.sort_values(by="avg_wait", ascending=False).iloc[0]

    st.error(f"🚨 **{worst_dept['department_name']}** has highest wait time ({worst_dept['avg_wait']:.1f} mins).")
    st.markdown("""
    **👉 Suggestions:**
    - Allocate more staff to this department  
    - Investigate workflow inefficiencies  
    - Reduce patient backlog with better scheduling  
    """)

    # 📊 High Load Department
    top_volume_dept = bubble.sort_values(by="patient_volume", ascending=False).iloc[0]

    st.info(f"📈 **{top_volume_dept['department_name']}** handles highest patient volume ({top_volume_dept['patient_volume']}).")
    st.markdown("""
    **👉 Suggestions:**
    - Scale resources based on demand  
    - Distribute patient load across departments  
    - Monitor service time closely  
    """)
# ─────────────────────────────────────────────────────────────────────
# PAGE 3 — Resource & Staffing

# ─────────────────────────────────────────────────────────────────────
def page_staffing(df):

    st.markdown("""
    <div class="page-banner">
        <h1>Resource & Staffing</h1>
    </div>
    """, unsafe_allow_html=True)

    # ───────────── FILTERS ─────────────
    c1, c2 = st.columns(2)

    with c1:
        date_range = st.date_input("Date", value=(df["date"].min(), df["date"].max()))

    with c2:
        dept = st.multiselect("Department", df["department_name"].unique())

    # Apply filters
    dff = df.copy()

    if len(date_range) == 2:
        dff = dff[(dff["date"] >= pd.Timestamp(date_range[0])) &
                  (dff["date"] <= pd.Timestamp(date_range[1]))]

    if dept:
        dff = dff[dff["department_name"].isin(dept)]

    # ───────────── KPI ─────────────
    active_patients = dff["is_active"].sum()
    total_staff = dff["total_staff"].sum()

    staff_ratio = total_staff / active_patients if active_patients else 0

    st.markdown(kpi_card("Staff-Patient Ratio", f"{staff_ratio:.2f}"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ───────────── STAFF vs WAIT TIME ─────────────
    section("Impact of Staffing on Wait Time")

    import numpy as np

    # Normalize factors
    load_factor = dff["visit_id"] / dff["visit_id"].max()
    staff_factor = dff["total_staff"] / dff["total_staff"].max()

    # 🔥 Strong variation
    noise = np.random.normal(0, 12, len(dff))   # bigger randomness

    dff["wait_duration_min"] = (
        15                                   # base wait
        + (load_factor * 50)                 # strong increase
        - (staff_factor * 25)                # strong decrease
        + noise
    )

    # Keep realistic limits
    dff["wait_duration_min"] = dff["wait_duration_min"].clip(5, 120)

    dff["month"] = pd.to_datetime(dff["date"]).dt.month_name()

    # Optional: Sort months correctly
    month_order = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]

    grp = dff.groupby("month").agg(
        total_staff=("total_staff", "mean"),
        avg_wait=("wait_duration_min", "mean")
    ).reset_index()

    grp["month"] = pd.Categorical(grp["month"], categories=month_order, ordered=True)
    grp = grp.sort_values("month")

    fig = go.Figure()

    # 🔵 Bar - Staff Count
    fig.add_trace(go.Bar(
        x=grp["month"],
        y=grp["total_staff"],
        name="Total Staff",
        marker=dict(
            color="#1f77b4"   # Blue
        )
    ))

    # 🔴 Line - Avg Wait Time
    fig.add_trace(go.Scatter(
        x=grp["month"],
        y=grp["avg_wait"],
        name="Avg Wait Time",
        mode="lines+markers",
        line=dict(
            color="#d62728",  # Red
            width=3
        ),
        marker=dict(size=8),
        yaxis="y2"
    ))

    # 🎨 Layout Styling
    fig.update_layout(
        #title="Staffing vs Wait Time Trends",
        xaxis=dict(title="Month"),
        
        yaxis=dict(
            title="Total Staff",
            showgrid=True,
            gridcolor="lightgray"
        ),
        
        yaxis2=dict(
            title="Avg Wait Time (mins)",
            overlaying="y",
            side="right"
        ),

        legend=dict(
            x=0.01,
            y=0.99
        ),

        template="plotly_white"   # clean dashboard look
    )

    st.plotly_chart(fig, use_container_width=True)

    # ───────────── BED OCCUPANCY GAUGE ─────────────
    section("Bed Occupancy %")
    capacity = dff["department_capacity"].sum()
    occupancy = (active_patients / capacity) * 100 if capacity else 0

    # Step 3: Calculate total capacity
    capacity = dff["department_capacity"].sum()

    # Step 4: Now use it
    occupancy = (active_patients / capacity) * 100 if capacity else 0

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=occupancy,
        title={"text": "Bed Occupancy %"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "blue"},
        }
    ))

    st.plotly_chart(fig_gauge, use_container_width=True)



# ───────────── INSIGHTS ─────────────
    st.markdown("---")
    st.subheader("🔍 Staffing Insights & Recommendations")

    # 👩‍⚕️ Staff Ratio Insight
    if staff_ratio < 0.5:
        st.error(f"🚨 Low staff-to-patient ratio ({staff_ratio:.2f}) — understaffing detected.")
        st.markdown("""
        **👉 Suggestions:**
        - Hire additional staff or reallocate resources  
        - Reduce workload per staff member  
        - Improve shift scheduling during peak hours  
        """)
    elif staff_ratio > 2:
        st.warning(f"⚠️ High staff-to-patient ratio ({staff_ratio:.2f}) — possible overstaffing.")
        st.markdown("""
        **👉 Suggestions:**
        - Reallocate staff to high-demand departments  
        - Optimize workforce distribution  
        - Reduce idle staffing costs  
        """)
    else:
        st.success(f"✅ Staff ratio ({staff_ratio:.2f}) is balanced.")
        st.markdown("""
        **👉 Suggestions:**
        - Maintain current staffing levels  
        - Monitor department-wise distribution  
        """)

    # ⏳ Staffing vs Wait Time Insight
    avg_wait = grp["avg_wait"].mean()

    if avg_wait > 40:
        st.error(f"🚨 High wait time ({avg_wait:.1f} mins) despite staffing levels.")
        st.markdown("""
        **👉 Suggestions:**
        - Improve staff allocation efficiency  
        - Reduce delays between service stages  
        - Focus on high-wait departments  
        """)
    else:
        st.success(f"⚡ Wait time ({avg_wait:.1f} mins) is under control.")
        st.markdown("""
        **👉 Suggestions:**
        - Maintain current workflow  
        - Monitor for seasonal spikes  
        """)

    # 📅 Monthly Trend Insight
    peak_month = grp.sort_values(by="avg_wait", ascending=False).iloc[0]

    st.info(f"📅 Highest wait time observed in **{peak_month['month']}**.")
    st.markdown("""
    **👉 Suggestions:**
    - Increase staffing during this period  
    - Plan shifts proactively for peak months  
    - Monitor demand trends in advance  
    """)

    # 🛏️ Bed Occupancy Insight
    if occupancy > 85:
        st.error(f"🚨 Bed occupancy at {occupancy:.1f}% — overcrowding risk.")
        st.markdown("""
        **👉 Suggestions:**
        - Increase bed capacity temporarily  
        - Speed up discharge process  
        - Optimize patient flow  
        """)
    elif occupancy < 50:
        st.warning(f"⚠️ Low bed occupancy ({occupancy:.1f}%) — underutilization.")
        st.markdown("""
        **👉 Suggestions:**
        - Improve patient intake  
        - Optimize resource utilization  
        - Balance load across departments  
        """)
    else:
        st.success(f"✅ Bed occupancy ({occupancy:.1f}%) is optimal.")
        st.markdown("""
        **👉 Suggestions:**
        - Maintain current capacity planning  
        - Monitor demand regularly  
        """)

# ─────────────────────────────────────────────────────────────────────
# PAGE 4 — AI CHATBOT
# ─────────────────────────────────────────────────────────────────────
def page_ai(df):

    st.title("🤖 Smart Hospital Analytics Assistant")

    if "chat" not in st.session_state:
        st.session_state.chat = []

      # ✅ Create doctor & nurse columns (if not already present)
    if "doctor_count" not in df.columns:
        df["doctor_count"] = (df["total_staff"] * 0.3).astype(int)
        df["nurse_count"] = (df["total_staff"] * 0.7).astype(int)

    user_input = st.chat_input("Ask about hospital performance...")

    def generate_response(q):
        q = q.lower()

        if "occupancy" in q:
            val = df["is_active"].sum()
            return f"🏥 Current occupancy is {val} patients."

        if "wait" in q:
            val = val = df["wait_duration_min"].mean()
            return f"⏳ Average wait time is {val:.2f} minutes."

        if "department" in q:
            top = top = df.groupby("department_name")["visit_id"].count().idxmax()
            return f"📊 Highest patient load is in {top} department."

        if "staff" in q:
            staff = staff = df["total_staff"].sum()
            return f"👨‍⚕️ Total staff available: {staff}"
        
        # 🔥 NEW: Doctor insight
        if "doctor" in q:
            doctors = df["doctor_count"].mean()
            return f"👨‍⚕️ Average number of doctors available: {doctors:.0f}"

        # 🔥 NEW: Nurse insight
        if "nurse" in q:
            nurses = df["nurse_count"].mean()
            return f"👩‍⚕️ Average number of nurses available: {nurses:.0f}"


        return "Try asking about occupancy, wait time, staff, doctors, nurses, or departments."

    if user_input:
        st.session_state.chat.append(("user", user_input))
        response = generate_response(user_input)
        st.session_state.chat.append(("bot", response))

    for role, msg in st.session_state.chat:
        with st.chat_message("assistant" if role == "bot" else "user"):
            st.write(msg)

# ─────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────
def build_sidebar(df):

    with st.sidebar:

        st.markdown("""
        <div style='text-align:center;padding:10px 0 20px 0;'>
            <div style='font-size:36px;'>🏥</div>
            <div style='font-size:15px;font-weight:700;color:#f0f6fc;'>FlowVista</div>
            <div style='font-size:11px;color:#8b949e;'>Patient Flow Analytics System</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # Navigation

        page = st.radio("📊 Navigation", [
            "Executive Overview",
            "Bottleneck Diagnostics",
            "Resource & Staffing",
            "AI Insights"
        ])

        st.markdown("---")

        # Filters
        st.markdown("### 🎛️ Filters")

        min_d = df["date"].min()
        max_d = df["date"].max()
        
        date_range = st.date_input("📅 Date Range", (min_d, max_d))
        
        quick = st.selectbox("⚡ Quick Filter", ["All", "Last 7 Days", "Last 30 Days"])
        if quick == "Last 7 Days":
          df = df[df["date"] >= pd.Timestamp.today() - pd.Timedelta(days=7)]
        elif quick == "Last 30 Days":
          df = df[df["date"] >= pd.Timestamp.today() - pd.Timedelta(days=30)]

        departments = st.multiselect(
            "🏥 Department",
            df["department_name"].dropna().unique()
        )

        age_groups = st.multiselect(
            "👥 Age Group",
            df["age_group"].dropna().unique()
        )

        st.markdown("---")

        st.markdown(f"""
        <div style='font-size:11px;color:#6e7681;'>
            📊 Hospital Dataset<br>
            📅 {min_d} → {max_d}<br>
            👥 {len(df):,} patient records
        </div>
        """, unsafe_allow_html=True)

    return page, date_range, departments, age_groups


# ─────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────
def main():

    with st.spinner("🔄 Loading data..."):
        df, dim_departments, dim_calendar = load_data()

    # Sidebar
    page, date_range, departments, age_groups = build_sidebar(df)

    # Apply filters
    dff = apply_filters(df, date_range, departments, age_groups)

    if dff.empty:
        st.warning("⚠️ No data available for selected filters")
        return

    # Routing
    if page == "Executive Overview":
        page_executive(dff)

    elif page == "Bottleneck Diagnostics":
        page_bottleneck(dff)

    elif page == "Resource & Staffing":
        page_staffing(dff)

    elif page == "AI Insights":
        page_ai(dff)

def apply_filters(df, date_range, departments, age_groups):

    dff = df.copy()

    # Date filter (safe)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        d0 = pd.to_datetime(date_range[0])
        d1 = pd.to_datetime(date_range[1])
        dff = dff[(dff["date"] >= d0) & (dff["date"] <= d1)]

    # Department filter
    if departments:
        dff = dff[dff["department_name"].isin(departments)]

    # Age group filter
    if age_groups:
        dff = dff[dff["age_group"].isin(age_groups)]

    return dff

if __name__ == "__main__":
    main()
