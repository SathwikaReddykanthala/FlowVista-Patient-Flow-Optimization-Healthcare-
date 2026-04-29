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



from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
#GROQ_API_KEY="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"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key="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")


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


def generate_ai_insights(df):

    # =========================
    # BASIC CLEANING
    # =========================
    df = df.copy()
    df = df.dropna(subset=["visit_id"])

    df["total_staff"] = df["total_staff"].fillna(0)
    df["wait_duration_min"] = df["wait_duration_min"].fillna(0)

    # =========================
    # AGE GROUP CREATION
    # =========================
    bins = [0, 18, 60, 100]
    labels = ["Child", "Adult", "Senior"]
    df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels)


        # =========================
    # TOTAL PATIENTS vs TOTAL STAFF (DEPT + AGE)
    # =========================

    group_df = df.groupby(["department_name", "age_group"]).agg(
        total_patients=("visit_id", "count"),
        total_staff=("total_staff", "mean")   # 🔥 TOTAL staff (not mean)
    ).reset_index()

    # Safe ratio
    group_df["patient_staff_ratio"] = group_df.apply(
        lambda x: x["total_patients"] / x["total_staff"]
        if x["total_staff"] > 0 else None,
        axis=1
    )

    st.dataframe(
        group_df.style.format({
            "patient_staff_ratio": "{:.2f}"
        }),
        width="stretch"
    )



    ratio_text = ""

    for _, row in group_df.iterrows():
        if pd.isna(row["patient_staff_ratio"]):
            ratio_text += (
                f"{row['department_name']} - {row['age_group']}: "
                f"{row['total_patients']} patients, NO STAFF AVAILABLE\n"
            )
        else:
            ratio_text += (
                f"{row['department_name']} - {row['age_group']}: "
                f"{row['total_patients']} patients, "
                f"{row['total_staff']:.1f} staff, "
                f"ratio {row['patient_staff_ratio']:.2f}\n"
            )
    # =========================
    # METRICS + RANGES
    # =========================
    wait = df["wait_duration_min"]
    wait_avg = wait.mean()
    wait_p25 = wait.quantile(0.25)
    wait_p75 = wait.quantile(0.75)

    staff_ratio = df.apply(
        lambda x: x["total_staff"] / x["visit_id"] if x["visit_id"] != 0 else 0,
        axis=1
    )
    staff_avg = staff_ratio.mean()
    staff_p25 = staff_ratio.quantile(0.25)
    staff_p75 = staff_ratio.quantile(0.75)

    visits = df.groupby("date")["visit_id"].count()
    visit_avg = visits.mean()
    visit_p25 = visits.quantile(0.25)
    visit_p75 = visits.quantile(0.75)

    stage_counts = df.groupby("stage")["visit_id"].count()
    bottleneck = stage_counts.idxmax()

    dept_counts = df.groupby("department_name")["visit_id"].count()
    top_dept = dept_counts.idxmax()

    

    # =========================
    # PATIENT vs STAFF (ENHANCED)
    # =========================

    ratio_df = df.groupby(["department_name", "age_group"]).agg(
        total_patients=("visit_id", "count"),
        total_staff=("total_staff", "mean")
    ).reset_index()

    dept_totals = df.groupby("department_name").agg(
        dept_total_patients=("visit_id", "count"),
        dept_total_staff=("total_staff", "mean")
    ).reset_index()

    ratio_df = ratio_df.merge(dept_totals, on="department_name", how="left")

    ratio_df["patient_staff_ratio"] = ratio_df.apply(
        lambda x: x["total_patients"] / x["total_staff"]
        if x["total_staff"] > 0 else None,
        axis=1
    )

    ratio_df["dept_patient_staff_ratio"] = ratio_df.apply(
        lambda x: x["dept_total_patients"] / x["dept_total_staff"]
        if x["dept_total_staff"] > 0 else None,
        axis=1
    )
    

    variation_df = group_df.groupby("department_name").agg(
        min_ratio=("patient_staff_ratio", "min"),
        max_ratio=("patient_staff_ratio", "max")
    ).reset_index()

    variation_df["range"] = variation_df["max_ratio"] - variation_df["min_ratio"]

    variation_text = ""

    for _, row in variation_df.iterrows():
        variation_text += (
            f"{row['department_name']}: "
            f"min {row['min_ratio']:.2f}, "
            f"max {row['max_ratio']:.2f}, "
            f"variation {row['range']:.2f}\n"
        )

    # =========================
    # CONVERT TO TEXT FOR AI
    # =========================
    ratio_text = ""

    for _, row in ratio_df.iterrows():

        if pd.isna(row["patient_staff_ratio"]):
            age_text = (
                f"{row['department_name']} - {row['age_group']}: "
                f"{row['total_patients']} patients, NO STAFF AVAILABLE"
            )
        else:
            age_text = (
                f"{row['department_name']} - {row['age_group']}: "
                f"{row['total_patients']} patients, "
                f"{row['total_staff']:.1f} staff, "
                f"ratio {row['patient_staff_ratio']:.2f}"
            )

        if pd.isna(row["dept_patient_staff_ratio"]):
            dept_text = (
                f" | Department Total: {row['dept_total_patients']} patients, NO STAFF"
            )
        else:
            dept_text = (
                f" | Department Total: {row['dept_total_patients']} patients, "
                f"{row['dept_total_staff']:.1f} staff, "
                f"ratio {row['dept_patient_staff_ratio']:.2f}"
            )

        # ✅ FIXED: always append
        ratio_text += age_text + dept_text + "\n"

    # =========================
    # PROMPT (moved outside loop)
    # =========================
    prompt = f"""
    You are a hospital analytics expert.


    DATA:
    Patient Volume Avg: {visit_avg:.2f} | Range: {visit_p25:.2f}-{visit_p75:.2f}
    Wait Time Avg: {wait_avg:.2f} | Range: {wait_p25:.2f}-{wait_p75:.2f}
    Staff Ratio Avg: {staff_avg:.2f} | Range: {staff_p25:.2f}-{staff_p75:.2f}

    Bottleneck Stage: {bottleneck}
    Top Department: {top_dept}

    Patient vs Staff by Department & Age:
    {ratio_text}

    IMPORTANT RULES:
    - Strictly follow the format below
    - Each label MUST be on a new line
    - DO NOT combine Insight, Why, Recommendations in one line
    - Use bullet points for recommendations
    - Return in MARKDOWN format only

    OUTPUT:

    ## 📊 Patient Volume
    Insight:

    Why:

    Recommendations:
    - Point 1
    - Point 2

    ## ⏳ Wait Time
    Insight:

    Why:

    Recommendations:
    - Point 1
    - Point 2

    ## 👩‍⚕️ Staffing Efficiency
    Insight:

    Why:

    Recommendations:
    - Point 1
    - Point 2

    ## 🚦 Bottleneck Analysis
    Insight:

    Why:

    Recommendations:
    - Point 1
    - Point 2

    ## 🏥 Department Demand
    Insight:

    Why:

    Recommendations:
    - Point 1
    - Point 2

    ## 👥 Patient-Staff Distribution (Dept + Age)
    Insight:

    Why:
    
    Recommendations:
    - Point 1
    - Point 2

    Patient vs Staff:
    {ratio_text}

    Variation across age groups:
    {variation_text}

    IMPORTANT:
    - Mention actual numbers

    - Do NOT say just "varies"
    
    - Show min, max, and difference

    ## 📌 Summary
    Provide a short overall summary
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Healthcare analytics expert"},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ Error: {e}"


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
    #TOTAL_CAPACITY = 246
    #capacity_pct = (active_patients / TOTAL_CAPACITY) * 100

    nurse_ratio = df["total_staff"] / df["visit_id"].replace(0, 1)
    nurse_ratio = nurse_ratio.mean()

    alos = df["wait_duration_min"].mean() / 60  # convert to hours

    # KPI ROW 1
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(kpi_card("Active Patients", f"{int(active_patients)}"), unsafe_allow_html=True)

    with c2:
        st.markdown(kpi_card("Nurse ratio", f"{nurse_ratio:.2f}"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Avg Wait Time", f"{avg_wait:.2f}"), unsafe_allow_html=True)

    #with c4:
        #st.markdown(kpi_card("Capacity %", f"{capacity_pct:.2f}%"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # KPI ROW 2
    c4, c5 = st.columns(2)

    with c4:
        st.markdown(kpi_card("ALOS (Hours)", f"{alos:.2f}"), unsafe_allow_html=True)

    if active_patients < 5000:
        load = "Low"
    elif active_patients < 12000:
        load = "Normal"
    else:
        load = "High"

    with c5:
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
 

    avg_staff = dff["total_staff"].mean()

    staff_ratio = avg_staff / active_patients if active_patients else 0

    st.markdown(kpi_card("Staff-Patient Ratio", f"{staff_ratio:.2f}"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ───────────── STAFF vs WAIT TIME ─────────────


    section("Impact of Staffing on Wait Time")

    # =========================
    # 🧪 Generate Wait Time
    # =========================

    # Normalize factors
    load_factor = dff["visit_id"] / dff["visit_id"].max()
    staff_factor = dff["total_staff"] / dff["total_staff"].max()

    noise = np.random.normal(0, 12, len(dff))

    dff["wait_duration_min"] = (
        15 + (load_factor * 50) - (staff_factor * 25) + noise
    )

    dff["wait_duration_min"] = dff["wait_duration_min"].clip(5, 120)

    # =========================
    # 📅 Create Month Column
    # =========================
    dff["month"] = pd.to_datetime(dff["date"]).dt.month_name()

    month_order = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]

    # =========================
    # 📊 CREATE grp (IMPORTANT)
    # =========================
    grp = dff.groupby("month", as_index=False).agg(
        total_staff=("total_staff", "mean"),
        avg_wait=("wait_duration_min", "mean")
    )

    grp["month"] = pd.Categorical(grp["month"], categories=month_order, ordered=True)
    grp = grp.sort_values("month")

    # =========================
    # 💡 BUBBLE CHART (FIXED)
    # =========================
    fig = px.scatter(
        grp,
        x="total_staff",
        y="avg_wait",
        size="avg_wait",
        color="month",
        text="month",
        title="💡 Impact of Staffing on Wait Time"
    )

    fig.update_traces(textposition="top center")

    st.plotly_chart(fig, use_container_width=True)




    # ───────────── BED OCCUPANCY GAUGE ─────────────
    section("Bed Occupancy %")

    # =========================
    # 📊 Capacity Calculation
    # =========================
    capacity = dff["department_capacity"].sum()

    # Avoid division error
    occupancy = (active_patients / capacity) * 100 if capacity > 0 else 0

    # Cap at 100% for UI
    occupancy = min(occupancy, 100)

    # =========================
    # 📈 Gauge Chart
    # =========================
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=occupancy,
        title={"text": "Bed Occupancy %"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "blue"},
            "steps": [
                {"range": [0, 50], "color": "#90EE90"},   # green
                {"range": [50, 85], "color": "#FFD580"},  # orange
                {"range": [85, 100], "color": "#FF7F7F"}  # red
            ],
        }
    ))

    st.plotly_chart(fig_gauge, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────
# PAGE 4 — AI CHATBOT
# ─────────────────────────────────────────────────────────────────────
def page_ai(df):

    st.title("🤖 AI Hospital Insights")

    if "insights" not in st.session_state:
        st.session_state.insights = ""

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔍 Generate AI Insights", use_container_width=True):
            with st.spinner("Analyzing hospital data..."):
                st.session_state.insights = generate_ai_insights(df)

    with col2:
        if st.button("♻️ Clear Insights", use_container_width=True):
            st.session_state.insights = ""

    with col3:
        st.info("Powered by Cohere AI")

    if st.session_state.insights:
        st.markdown("### 📊 AI Analysis")
        st.write(st.session_state.insights)
    else:
        st.info("Click 'Generate AI Insights' to analyze data.")
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
