import os
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# MySQL Connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Kushu@123",
    database="roopadb"
)
cursor = conn.cursor(dictionary=True)

# Query for March & April
query = """
SELECT
    data_month,
    scenario_name,
    CAST(REPLACE(total_no_of_customers, 'M', '') AS DECIMAL(10,1)) AS customers,
    CAST(REPLACE(total_no_of_accounts, 'M', '') AS DECIMAL(10,1)) AS accounts,
    CAST(REPLACE(REPLACE(total_alert, ',', ''), 'K', '') AS UNSIGNED) AS alerts_generated,
    CAST(REPLACE(total_no_of_alert_closed, 'K', '') AS DECIMAL(10,1)) AS alerts_closed,
    fraud_typology_efm
FROM SIB
WHERE data_month IN ('March-25', 'April-25');
"""
cursor.execute(query)
data = pd.DataFrame(cursor.fetchall())
cursor.close()
conn.close()

# Fill NA
data.fillna(0, inplace=True)

# Open alerts calculation
data["open_alerts"] = data["alerts_generated"] - data["alerts_closed"]

# Summary for April
summary_april = data[data["data_month"] == "April-25"]
total_customers = round(summary_april["customers"].sum(), 1)
total_accounts = round(summary_april["accounts"].sum(), 1)
total_transactions = round(summary_april["alerts_generated"].sum(), 1)  # Assuming transactions ~ alerts_generated
total_alerts = int(summary_april["alerts_generated"].sum())

# Grouped data for comparison
summary_grouped = data.groupby("data_month").agg({
    "alerts_generated": "sum",
    "alerts_closed": "sum",
    "open_alerts": "sum"
}).reindex(["March-25", "April-25"])

# Top 5 scenarios for April
top_scenarios = (
    summary_april.groupby("scenario_name")["alerts_generated"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

# ---------------------- PLOT ----------------------
fig = plt.figure(figsize=(18, 12))
fig.suptitle("Enterprise Fraud Management\nSIB BANK CXO DASHBOARD - April-2025", fontsize=18, fontweight='bold')

# ---------------------- TOP ROW - SUMMARY BAR CHART ----------------------
ax_summary = plt.subplot2grid((4, 3), (0, 0), colspan=3)
labels = ["Customers", "Accounts", "Transactions"]
values = [total_customers, total_accounts, total_transactions]
colors = ["#1f77b4", "#2ca02c", "#ff7f0e"]

bars = ax_summary.barh(labels, values, color=colors)
ax_summary.set_title("April 2025 – Summary", fontsize=15, fontweight='bold', pad=20)
ax_summary.bar_label(bars, fmt="%.1fM", label_type="edge")
ax_summary.set_xlim(0, float(max(values)) * 1.2)

# ---------------------- MIDDLE ROW - BAR CHARTS ----------------------
months = ["March-25", "April-25"]
bar_width = 0.4
x = np.arange(len(months))

# Alerts Generated
ax4 = plt.subplot2grid((4, 3), (1, 0))
ax4.bar(x, summary_grouped["alerts_generated"], color=["#9999ff", "#1f4acc"], width=bar_width)
ax4.set_xticks(x)
ax4.set_xticklabels(months)
ax4.set_title("Alerts Generated", fontsize=12, fontweight='bold')
ax4.bar_label(ax4.containers[0], fmt="%.0f", label_type="edge")

# Alerts Closed
ax5 = plt.subplot2grid((4, 3), (1, 1))
ax5.bar(x, summary_grouped["alerts_closed"], color=["#b3ffb3", "#0e8a16"], width=bar_width)
ax5.set_xticks(x)
ax5.set_xticklabels(months)
ax5.set_title("Alerts Closed", fontsize=12, fontweight='bold')
ax5.bar_label(ax5.containers[0], fmt="%.0f", label_type="edge")

# Open Alerts
ax6 = plt.subplot2grid((4, 3), (1, 2))
ax6.bar(x, summary_grouped["open_alerts"], color=["#ff9999", "#cc3300"], width=bar_width)
ax6.set_xticks(x)
ax6.set_xticklabels(months)
ax6.set_title("Open Alerts", fontsize=12, fontweight='bold')
ax6.bar_label(ax6.containers[0], fmt="%.0f", label_type="edge")

# ---------------------- BOTTOM ROW - TOP SCENARIOS ----------------------
ax7 = plt.subplot2grid((4, 3), (2, 0), colspan=3, rowspan=2)
bars = ax7.bar(top_scenarios["scenario_name"], top_scenarios["alerts_generated"], color="#9933ff")
ax7.set_title("Top 5 Scenarios – Alert Counts", fontsize=14, fontweight='bold')
ax7.set_ylabel("Alert Count")
ax7.set_xlabel("Scenario Name", fontsize=12, fontweight='bold')
ax7.tick_params(axis='x', rotation=20)
ax7.bar_label(bars, fmt="%.0f", label_type="edge")

# ---------------------- SAVE & SHOW ----------------------
plt.tight_layout(rect=[0, 0, 1, 0.94])
output_dir = "pngs"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "summary_dashboard_april_2025.png")
plt.savefig(output_path)
print(f"✅ Dashboard saved as: {output_path}")
