# 🏥 Patient Flow Optimization BI System

A complete **Business Intelligence (BI) Dashboard** built using **Streamlit**, designed to analyze hospital patient flow, identify bottlenecks, optimize staffing, and improve operational efficiency.

---

## 📌 Overview

The **Patient Flow Optimization System** provides:

* 📊 Executive-level KPIs
* 🔍 Bottleneck detection
* 👨‍⚕️ Staffing & resource optimization
* 🤖 AI-powered chatbot for insights
* ⭐ Star Schema-based data modeling

This system helps hospital administrators make **data-driven decisions** to reduce wait times and improve patient care.

---

## 🧱 Architecture

### ⭐ Data Model (Star Schema)

**Fact Tables:**

* `Fact_DeptLogs` → Patient movement & timestamps
* `Fact_Staffing` → Staff availability

**Dimension Tables:**

* `Dim_Patients` → Patient details
* `Dim_Visits` → Visit-level info
* `Dim_Departments` → Department metadata
* `Dim_Calendar` → Date & time hierarchy

---

## 🚀 Features

### 1️⃣ Executive Overview

* Active Patients
* Capacity Utilization %
* Average Wait Time
* Nurse-to-Patient Ratio
* ALOS (Average Length of Stay)
* Patient Load Classification

📈 Visualizations:

* Funnel chart (Stage-wise flow)
* Department demand analysis
* Age-group analysis

---

### 2️⃣ Bottleneck Diagnostics

* Throughput Rate
* Time-based Heatmap (Day vs Hour)
* Department Efficiency (Bubble Chart)

🎯 Identifies:

* Peak delay hours
* High-wait departments
* Workflow inefficiencies

---

### 3️⃣ Resource & Staffing

* Staff-to-Patient Ratio
* Staffing vs Wait Time Trends
* Bed Occupancy Gauge

📊 Insights:

* Understaffing / Overstaffing detection
* Monthly performance trends
* Capacity optimization

---

### 4️⃣ 🤖 AI Chatbot

Interactive assistant to answer:

* Occupancy
* Wait times
* Department load
* Staff availability
* Doctor/Nurse insights

---

## ⚙️ Tech Stack

* **Frontend**: Streamlit
* **Backend/Data Processing**: Python (Pandas, NumPy)
* **Visualization**: Plotly
* **Environment Management**: dotenv

---

## 📂 Project Structure

```
📁 project/
│
├── app.py
├── .env
├── Fact_DeptLogs.csv
├── Fact_Staffing.csv
├── Dim_Patients.csv
├── Dim_Visits.csv
├── Dim_Departments.csv
├── Dim_Calendar.csv
└── README.md
```

---

## 🔧 Installation & Setup

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd project
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables

Create `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

### 4. Run Application

```bash
streamlit run app.py
```

---

## 📊 Key KPIs Explained

| KPI             | Description                      |
| --------------- | -------------------------------- |
| Active Patients | Unique patient visits            |
| Capacity %      | Utilization of hospital capacity |
| Avg Wait Time   | Average waiting duration         |
| Nurse Ratio     | Staff availability efficiency    |
| ALOS            | Avg length of stay (hours)       |
| Throughput      | Patients processed per day       |

---

## 🔍 Insights & Recommendations Engine

The system automatically generates:

* ⚠️ Alerts (Low capacity, high wait time)
* ✅ Optimization suggestions
* 🚨 Risk detection (Overcrowding, delays)

---

## 🎯 Use Cases

* Hospital Operations Management
* Patient Flow Optimization
* Healthcare Analytics
* Resource Planning
* Performance Monitoring

---

## ⚠️ Known Improvements

* Replace rule-based chatbot with LLM integration
* Add real-time data streaming
* Improve predictive analytics (ML models)
* Deploy on cloud (AWS / Azure / GCP)

---

## ⭐ Conclusion

This project demonstrates:

* End-to-end **Data Analytics Pipeline**
* **Star Schema Modeling**
* **Interactive BI Dashboard**
* **Actionable Healthcare Insights**

---

💡 *Transform hospital data into smarter decisions.*

