import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from PIL import Image as PILImage  
from collections import OrderedDict
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Image
import os

st.set_page_config(page_title="Energy Saver", layout="wide", page_icon="⚡")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #F6FAFA; }
[data-testid="stSidebar"] { background-color: #E6F4EF; padding-top: 25px; }
.sidebar-container { text-align: center; padding: 15px; }

/* CENTERED ENERGY SAVER TITLE */
.sidebar-title { 
    font-size: 24px; 
    font-weight: 800; 
    color: #1C4532; 
    margin-bottom: 25px;
    text-align: center; 
}

/* Center the logo image */
section[data-testid="stSidebar"] img {
    display: block;
    margin-left: auto;
    margin-right: auto;
}

section[data-testid="stSidebar"] div.stButton > button {
    background-color: #CDEAE1; color: #1C4532; font-weight: 600;
    height: 50px; width: 100%; border: none; border-radius: 12px;
    margin-bottom: 10px; transition: all 0.2s ease-in-out;
}
section[data-testid="stSidebar"] div.stButton > button:hover {
    background-color: #A8D5C8; color: #0F2E1D;
}
section[data-testid="stSidebar"] div.stButton > button:focus {
    background-color: #009688 !important; color: white !important;
    border: 2px solid #007F73 !important;
}
.metric-card {
    padding: 25px; border-radius: 15px; color: white; text-align: left;
    font-weight: 600; box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    display: flex; align-items: center; gap: 15px;
}
.metric-icon { font-size: 28px; }
.metric-text { display: flex; flex-direction: column; }
.metric-title { font-size: 15px; opacity: 0.9; }
.metric-value { font-size: 22px; font-weight: 700; }
.stForm {
    background-color: white; padding: 25px; border-radius: 15px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.small-muted { font-size:12px; color: #555; }
.report-card { background-color: #F7FFF7; padding: 18px; border-radius: 12px; }
.breakdown-row { display:flex; justify-content:space-between; padding:8px 0; }
.breakdown-title { font-weight:700; }
</style>
""", unsafe_allow_html=True)

if "appliances_by_month" not in st.session_state:
    st.session_state.appliances_by_month = {}

if "appliances" not in st.session_state:
    st.session_state.appliances = []

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "computed_result" not in st.session_state:
    st.session_state.computed_result = None

if "chart_type" not in st.session_state:
    st.session_state.chart_type = None

if "monthly_reports" not in st.session_state:
    st.session_state.monthly_reports = OrderedDict()

if "show_breakdown" not in st.session_state:
    st.session_state.show_breakdown = False

if "show_comparison" not in st.session_state:
    st.session_state.show_comparison = False

if "dashboard_month" not in st.session_state:
    st.session_state.dashboard_month = datetime.now().strftime("%B")

if "dashboard_year" not in st.session_state:
    st.session_state.dashboard_year = datetime.now().year

st.sidebar.markdown("<div class='sidebar-container'>", unsafe_allow_html=True)

col1, col2, col3 = st.sidebar.columns([1, 2, 1])
with col2:
    img = PILImage.open("images/4763.png")
    st.image(img, width=140)

st.sidebar.markdown("<div class='sidebar-title'>⚡ Energy Saver</div>", unsafe_allow_html=True)

menu_items = [
    "Dashboard",
    "Consumption Summary",
    "Monthly Report",
    "Energy Efficiency",
    "Carbon Footprint",
    "Work & Energy Analysis"
]

for item in menu_items:
    if st.sidebar.button(item, use_container_width=True):
        st.session_state.page = item
        st.session_state.chart_type = None
        st.session_state.show_breakdown = False
        st.session_state.show_comparison = False

st.sidebar.markdown("</div>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.subheader("🌿 Eco Tip")
st.sidebar.info("Unplug devices when not in use to reduce phantom energy consumption.")

def compute_energy(power, hours, provider):
    if "Meralco" in provider:
        rate = 13.4702
    elif "BATELEC I" in provider:
        rate = 9.7297
    else:
        rate = 8.7447  

    energy_kwh = (power * hours) / 1000.0
    cost = energy_kwh * rate
    return energy_kwh, cost

def update_stats():
    appliances = st.session_state.appliances
    total_appliances = len(appliances)
    daily_energy = sum(a["energy_kwh"] for a in appliances)
    daily_cost = sum(a["cost"] for a in appliances)
    monthly_est = daily_cost * 30
    return total_appliances, daily_energy, daily_cost, monthly_est

def breakdown_components(total_cost, provider):
    if provider == "Meralco":
        comps = OrderedDict([
            ("Generation Charge", 59.79),
            ("Transmission Charge", 8.49),
            ("System Loss", 5.22),
            ("Distribution (Meralco)", 13.05),
            ("Subsidies", -0.01),
            ("Government Taxes", 10.77),
            ("Universal Charges", 1.81),
            ("FiT-ALL (Renewable)", 0.89)
        ])

    elif provider == "BATELEC I":
        comps = OrderedDict([
            ("Generation Charge", 52.99),
            ("Transmission Charge", 7.72),
            ("System Loss", 9.19),
            ("Distribution Charges", 15.91),
            ("VAT", 10.57),
            ("Universal Charges", 2.43),
            ("FiT-ALL (Renewable)", 1.19)
        ])

    else:  
        comps = OrderedDict([
            ("Generation Charge", 56.20),
            ("Transmission Charge", 8.76),
            ("System Loss", 7.22),
            ("Distribution Charges", 11.43),
            ("Universal Charges", 3.91),
            ("CAPEX", 3.48),
            ("VAT", 9.00)
        ])
        
    items = []
    for k, pct in comps.items():
        amt = total_cost * (pct / 100.0)
        items.append((k, amt, pct))
    return items

def save_month_report(month_label, appliances_snapshot, total_energy, total_cost, provider):
    st.session_state.monthly_reports[month_label] = {
        "date_generated": datetime.now().isoformat(),
        "appliances": appliances_snapshot,
        "total_energy_kwh": total_energy,
        "total_cost": total_cost,
        "provider": provider
    }

def generate_green_bill(month_key, top_appliance, provider, monthly_energy, monthly_cost, breakdown):

    month_safe = month_key.replace(" ", "_")
    path = f"/mnt/data/Energy_Saver_Bill_{month_safe}.pdf"

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "title",
        parent=styles["Title"],
        fontSize=22,
        alignment=0,
        textColor=colors.HexColor("#1B5E20"),
        leading=26
    )

    subtitle = ParagraphStyle(
        "subtitle",
        parent=styles["BodyText"],
        fontSize=11,
        alignment=0,
        textColor=colors.HexColor("#2E7D32"),
        leading=14
    )

    section = ParagraphStyle(
        "section",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#2E7D32"),
        leading=18
    )

    body = ParagraphStyle(
        "body",
        parent=styles["BodyText"],
        fontSize=11
    )

    doc = SimpleDocTemplate(
        path,
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
    )

    flow = []

    logo_path = r"images/4763.png"   
    logo = Image(logo_path, width=60, height=60)

    title_block = [
        Paragraph("<b>ENERGY SAVER</b>", title),
        Paragraph(
            "A PHYSICS-INTEGRATED PYTHON SYSTEM FOR HOUSEHOLD ENERGY ESTIMATION AND EFFICIENCY OPTIMIZATION",
            subtitle,
        ),
    ]

    header_table = Table([[logo, title_block]], colWidths=[70, 400])

    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (0, 0), 0),
                ("RIGHTPADDING", (0, 0), (0, 0), 10),
            ]
        )
    )

    flow.append(header_table)
    flow.append(Spacer(1, 18))

    flow.append(Paragraph("<b>Billing Details</b>", section))
    flow.append(Spacer(1, 6))

    bill_info = [
        ["Month:", month_key],
        ["Most Used Appliance:", top_appliance],
        ["Electricity Provider:", provider],
        ["Total Monthly Energy:", f"{monthly_energy:,.2f} kWh"],
        ["Total Monthly Cost:", f"Php {monthly_cost:,.2f}"],
    ]

    bill_table = Table(bill_info, colWidths=[170, 260])
    bill_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CDEAE1")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8F5EE")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
            ]
        )
    )

    flow.append(bill_table)
    flow.append(Spacer(1, 18))

    flow.append(Paragraph("<b>Electricity Breakdown</b>", section))
    flow.append(Spacer(1, 6))

    breakdown_data = [["Charge Type", "Percentage", "Amount (Php)"]]

    for label, amt, pct in breakdown:
        breakdown_data.append([label, f"{pct:.2f}%", f"Php {amt:,.2f}"])

    bd_table = Table(breakdown_data, colWidths=[230, 90, 150])
    bd_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#C8E6C9")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1B5E20")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#A5D6A7")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
            ]
        )
    )

    flow.append(bd_table)
    flow.append(Spacer(1, 22))

    summary_data = [
        ["Total Monthly Energy (kWh):", f"{monthly_energy:,.2f}"],
        ["Total Monthly Cost (Php):", f"Php {monthly_cost:,.2f}"],
    ]

    summary_table = Table(summary_data, colWidths=[310, 170])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E8F5EE")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#A5D6A7")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ]
        )
    )

    flow.append(summary_table)
    flow.append(Spacer(1, 30))

    flow.append(
        Paragraph(
            "This is an autogenerated bill from the Energy Saver system. For accuracy, check meter readings and official utility statements.",
            body,
        )
    )
    flow.append(Spacer(1, 6))
    flow.append(Paragraph("<i>Thank you for using Energy Saver!</i>", body))

    doc.build(flow)
    return path

#------------Dashboard---------------
if st.session_state.page == "Dashboard":
    st.markdown("## 🏠 Dashboard")

    current_month = datetime.now().month
    current_year = datetime.now().year

    col_ms1, col_ms2 = st.columns([3, 1])
    with col_ms1:
        st.selectbox(
            "Select Month",
            [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ],
            index=current_month - 1,
            key="dashboard_month"
        )
    with col_ms2:
        st.number_input(
            "Year",
            min_value=2000,
            max_value=2100,
            value=current_year,
            step=1,
            key="dashboard_year"
        )

    month_key = f"{st.session_state.dashboard_month} {st.session_state.dashboard_year}"

    if month_key not in st.session_state.appliances_by_month:
        st.session_state.appliances_by_month[month_key] = []

    st.session_state.appliances = st.session_state.appliances_by_month[month_key]

    st.markdown("---")

    total_appliances, daily_energy, daily_cost, monthly_est = update_stats()

    col1, col2, col3, col4 = st.columns(4)
    cards = [
        ("#1C9E81", "🧰", "Total Appliances", f"{total_appliances}"),
        ("#0096E6", "⚡", "Daily Energy", f"{daily_energy:.2f} kWh/day"),
        ("#F79C1D", "💰", "Daily Cost", f"₱{daily_cost:.2f}"),
        ("#9336B4", "📅", "Monthly Estimate", f"₱{monthly_est:.2f}")
    ]

    for col, (color, icon, title, value) in zip([col1, col2, col3, col4], cards):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="background-color:{color};">
                <div class="metric-icon">{icon}</div>
                <div class="metric-text">
                    <div class="metric-title">{title}</div>
                    <div class="metric-value">{value}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("➕ Add New Appliance")

    if 'form_counter' not in st.session_state:
        st.session_state.form_counter = 0

    if 'temp_values' not in st.session_state:
        st.session_state.temp_values = {}

    with st.form(key=f"add_appliance_form_{st.session_state.form_counter}", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Appliance Name", 
                               value=st.session_state.temp_values.get('name', ''),
                               placeholder="e.g., Refrigerator")
            category = st.selectbox(
                "Category",
                ["", "Kitchen", "Entertainment", "Lighting", "Cooling & Heating", "Laundry", "Other"],
                index=st.session_state.temp_values.get('category_idx', 0))
            power = st.number_input("Power (Watts)", 
                                   min_value=0.0, 
                                   step=10.0, 
                                   value=st.session_state.temp_values.get('power', 0.0))

        with c2:
            hours = st.number_input("Hours per Day", 
                                   min_value=0.0, 
                                   step=0.5, 
                                   value=st.session_state.temp_values.get('hours', 0.0))
            provider = st.selectbox(
                "Electricity Provider",
                ["", "Meralco (₱13.4702/kWh)", "BATELEC I (₱9.7297/kWh)", "BATELEC II (₱8.7447/kWh)"],
                index=st.session_state.temp_values.get('provider_idx', 0))

        colA, colB = st.columns(2)
        with colA:
            compute_btn = st.form_submit_button("Compute Energy", use_container_width=True)
        with colB:
            add_btn = st.form_submit_button("Add Appliance", use_container_width=True)

        if compute_btn:
            if not name or not category or not provider:
                st.error("⚠️ Please fill out all fields.")
            else:
                categories = ["", "Kitchen", "Entertainment", "Lighting", "Cooling & Heating", "Laundry", "Other"]
                providers = ["", "Meralco (₱13.4702/kWh)", "BATELEC I (₱9.7297/kWh)", "BATELEC II (₱8.7447/kWh)"]

                st.session_state.temp_values = {
                    'name': name,
                    'category_idx': categories.index(category),
                    'power': power,
                    'hours': hours,
                    'provider_idx': providers.index(provider)
                }

                energy_kwh, cost = compute_energy(power, hours, provider)
                st.session_state.computed_result = (energy_kwh, cost)

                st.rerun()

        # ---------------- Add Appliance Button ----------------
        if add_btn:
            if not name or not category or not provider:
                st.error("Please fill out all fields.")
            else:
                energy_kwh, cost = compute_energy(power, hours, provider)
                if "Meralco" in provider:
                    provider_label = "Meralco"
                elif "BATELEC I" in provider:
                    provider_label = "BATELEC I"
                else:
                    provider_label = "BATELEC II"

                if 'pending_appliance' not in st.session_state:
                    st.session_state.pending_appliance = None

                st.session_state.pending_appliance = {
                    "name": name,
                    "category": category,
                    "power": power,
                    "hours": hours,
                    "provider": provider_label,
                    "energy_kwh": energy_kwh,
                    "cost": cost,
                    "month_key": month_key
                }

                st.session_state.temp_values = {}
                st.session_state.computed_result = None

                st.rerun()

    if 'computed_result' in st.session_state and st.session_state.computed_result:
        energy_kwh, cost = st.session_state.computed_result
        st.success(f"Estimated Energy: {energy_kwh:.2f} kWh/day | Cost: ₱{cost:.2f}/day")

    if 'pending_appliance' in st.session_state and st.session_state.pending_appliance:
        st.markdown("---")
        st.subheader("Pending Appliance")
        
        pending = st.session_state.pending_appliance
        
        preview_col1, preview_col2 = st.columns([3, 1])
        
        with preview_col1:
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 4px solid #0096E6;">
                <p style="margin: 5px 0;"><strong>Name:</strong> {pending['name']}</p>
                <p style="margin: 5px 0;"><strong>Category:</strong> {pending['category']}</p>
                <p style="margin: 5px 0;"><strong>Power:</strong> {pending['power']} Watts</p>
                <p style="margin: 5px 0;"><strong>Hours per Day:</strong> {pending['hours']} hours</p>
                <p style="margin: 5px 0;"><strong>Provider:</strong> {pending['provider']}</p>
                <p style="margin: 5px 0;"><strong>Energy Consumption:</strong> {pending['energy_kwh']:.2f} kWh/day</p>
                <p style="margin: 5px 0;"><strong>Estimated Cost:</strong> ₱{pending['cost']:.2f}/day</p>
            </div>
            """, unsafe_allow_html=True)
        
        with preview_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("""
            <style>
            div.stButton > button[kind="primary"] {
                background-color: #28a745;
                border-color: #28a745;
            }
            div.stButton > button[kind="primary"]:hover {
                background-color: #218838;
                border-color: #1e7e34;
            }
            </style>
            """, unsafe_allow_html=True)
            
            if st.button("Save", use_container_width=True, type="primary", key="save_pending"):
                st.session_state.appliances_by_month[pending['month_key']].append({
                    "name": pending['name'],
                    "category": pending['category'],
                    "power": pending['power'],
                    "hours": pending['hours'],
                    "provider": pending['provider'],
                    "energy_kwh": pending['energy_kwh'],
                    "cost": pending['cost']
                })
                st.success(f"Saved {pending['name']} to {pending['month_key']}")
                st.session_state.pending_appliance = None
                st.session_state.form_counter += 1
                st.rerun()
            
            if st.button("Edit", use_container_width=True, type="secondary"):
                categories = ["", "Kitchen", "Entertainment", "Lighting", "Cooling & Heating", "Laundry", "Other"]
                providers_list = ["Meralco", "BATELEC I", "BATELEC II"]
                if pending['provider'] == "Meralco":
                    provider_full = "Meralco (₱13.4702/kWh)"
                elif pending['provider'] == "BATELEC I":
                    provider_full = "BATELEC I (₱9.7297/kWh)"
                else:
                    provider_full = "BATELEC II (₱8.7447/kWh)"
                
                st.session_state.temp_values = {
                    'name': pending['name'],
                    'category_idx': categories.index(pending['category']),
                    'power': pending['power'],
                    'hours': pending['hours'],
                    'provider_idx': ["", "Meralco (₱13.4702/kWh)", "BATELEC I (₱9.7297/kWh)", "BATELEC II (₱8.7447/kWh)"].index(provider_full)
                }
                st.session_state.pending_appliance = None
                st.session_state.form_counter += 1
                st.rerun()
            
            if st.button("Delete", use_container_width=True, type="secondary"):
                st.session_state.pending_appliance = None
                st.session_state.form_counter += 1
                st.rerun()

# -------------------- Consumption Summary --------------------
elif st.session_state.page == "Consumption Summary":
    st.subheader("📊 Consumption Summary")

    month_key = f"{st.session_state.dashboard_month} {st.session_state.dashboard_year}"
    st.caption(f"Showing data for: **{month_key}**")

    if st.session_state.appliances:

        df = pd.DataFrame(st.session_state.appliances)
        st.dataframe(df, use_container_width=True)

        col1, col2 = st.columns([1, 2])

        # ---------------- SUMMARY CARD ----------------
        with col1:

            daily_energy = df["energy_kwh"].sum()
            daily_cost = df["cost"].sum()

            monthly_energy = daily_energy * 30
            monthly_cost = daily_cost * 30

            yearly_energy = daily_energy * 365
            yearly_cost = daily_cost * 365

            st.markdown(f"""
            <div style="background-color:#E8F5E9; padding:25px; border-radius:12px; text-align:center;">
                <h4 style="font-weight:bold;">Total Consumption</h4>
                <p>Daily</p>
                <h3 style="color:#2E7D32;">{daily_energy:.2f} kWh</h3>
                <p>₱{daily_cost:.2f}</p>
                <p>Monthly (×30)</p>
                <h3 style="color:#2E7D32;">{monthly_energy:.2f} kWh</h3>
                <p>₱{monthly_cost:.2f}</p>
                <p>Yearly (×365)</p>
                <h3 style="color:#2E7D32;">{yearly_energy:.2f} kWh</h3>
                <p>₱{yearly_cost:.2f}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("<h4 style='font-weight:bold;'>Visualizations</h4>", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📊 Show Bar Chart", use_container_width=True):
                    st.session_state.chart_type = "Bar Chart"

            with col_b:
                if st.button("🟣 Show Pie Chart (Cost)", use_container_width=True):
                    st.session_state.chart_type = "Pie Chart"

            if st.session_state.chart_type:

                names = df["name"].tolist()
                energies = df["energy_kwh"].tolist()
                costs = df["cost"].tolist()

                if st.session_state.chart_type == "Bar Chart":
                    fig = px.bar(
                        df,
                        x="name",
                        y="energy_kwh",
                        text_auto='.2f',
                        title="Energy Consumption by Appliance (kWh)"
                    )
                    fig.update_layout(
                        xaxis_title="Appliance",
                        yaxis_title="Energy (kWh)",
                        xaxis_tickangle=30,
                        height=450
                    )
                    st.plotly_chart(fig, use_container_width=True)

                else:
                    fig = px.pie(
                        df,
                        names="name",
                        values="cost",
                        title="Cost Distribution by Appliance (₱)"
                    )
                    fig.update_traces(textinfo="label+value", textposition="inside")
                    st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No appliances added yet. Add some on the Dashboard to view the summary.")

# -------------------- Monthly Report --------------------
elif st.session_state.page == "Monthly Report":

    st.subheader("📅 Monthly Report")

    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    col_m1, col_m2 = st.columns([3, 1])
    with col_m1:
        month_select = st.selectbox("Select Month to View", months, index=datetime.now().month - 1)
    with col_m2:
        year_select = st.number_input("Year", value=datetime.now().year, min_value=2000, max_value=2100)

    month_key = f"{month_select} {year_select}"

    if month_key not in st.session_state.appliances_by_month:
        st.session_state.appliances_by_month[month_key] = []

    appliances = st.session_state.appliances_by_month[month_key]

    cA, cB = st.columns(2)
    with cA:
        generate = st.button("Generate Report", use_container_width=True)
    with cB:
        comp = st.button("View Comparison", use_container_width=True)

    if generate:
        st.session_state.show_breakdown = True
        st.session_state.show_comparison = False

    if comp:
        st.session_state.show_breakdown = False
        st.session_state.show_comparison = True

    st.markdown(f"### Appliances for {month_key}")

    if appliances:

        df = pd.DataFrame(appliances)
        st.dataframe(df, use_container_width=True)

        daily_energy = df["energy_kwh"].sum()
        daily_cost = df["cost"].sum()

        monthly_energy = daily_energy * 30
        monthly_cost = daily_cost * 30

        if generate:
            provider = df["provider"].mode()[0]
            save_month_report(month_key, appliances.copy(), monthly_energy, monthly_cost, provider)
            st.success("Report saved.")

        # ---------------- SUMMARY CARDS ----------------
        c1, c2, c3, c4 = st.columns(4)
        cards = [
            ("#1C9E81", "🧰", "Appliances", len(df)),
            ("#0096E6", "⚡", "Energy", f"{monthly_energy:.2f} kWh"),
            ("#F79C1D", "💰", "Cost", f"₱{monthly_cost:.2f}"),
            ("#9336B4", "🏷️", "Provider", df["provider"].mode()[0])
        ]

        for col, (color, icon, title, value) in zip([c1, c2, c3, c4], cards):
            with col:
                st.markdown(f"""
                <div class="metric-card" style="background-color:{color};">
                    <div class='metric-icon'>{icon}</div>
                    <div class='metric-text'>
                        <div class='metric-title'>{title}</div>
                        <div class='metric-value'>{value}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        provider = df["provider"].mode()[0]
        breakdown = breakdown_components(monthly_cost, provider)

        if st.button("Save Receipt (TXT)", key="save_txt_receipt", use_container_width=True):
            top_appliance = df.loc[df["cost"].idxmax()]["name"]
            comps = breakdown
            receipt_text = f"""ENERGY SAVER: A PHYSICS-INTEGRATED PYTHON SYSTEM FOR HOUSEHOLD ENERGY ESTIMATION AND EFFICIENCY OPTIMIZATION

Month: {month_key}
Most Appliance Use for the Month: {top_appliance}

Total Monthly Energy: {monthly_energy:.2f} kWh
Total Monthly Cost: Php {monthly_cost:.2f}
Energy Provider: {provider}

---------------------------------------
Electricity Breakdown
---------------------------------------
"""
            for item, amt, pct in comps:
                receipt_text += f"{item} ({pct}%): Php {amt:.2f}\n"
            receipt_text += "\n---------------------------------------\nEnd of Receipt\n"

            st.download_button(
                label="📄 Download Bill Receipt (TXT)",
                data=receipt_text,
                file_name=f"Energy_Receipt_{month_key.replace(' ','_')}.txt",
                mime="text/plain"
            )

        if st.button("Download Bill Receipt (PDF)", key="download_pdf", use_container_width=True):

            top_appliance = df.loc[df["cost"].idxmax()]["name"]
            pdf_path = generate_green_bill(
                month_key=month_key,
                top_appliance=top_appliance,
                provider=provider,
                monthly_energy=monthly_energy,
                monthly_cost=monthly_cost,
                breakdown=breakdown
            )

            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="📄 Download PDF Bill",
                        data=pdf_file,
                        file_name=f"Energy_Bill_{month_key.replace(' ','_')}.pdf",
                        mime="application/pdf"
                    )
                st.success("PDF bill generated and ready to download.")
            else:
                st.error("Failed to create PDF. Please check server permissions for /mnt/data/.")

        st.markdown("---")

        # -------------------- BREAKDOWN VIEW --------------------
        if st.session_state.show_breakdown:

            comps = breakdown

            left, right = st.columns([1.2, 1])

            with left:
                total_cost = monthly_cost

                st.markdown(
                    f"""
                    <div style="
                        background:#FFF7E6;
                        padding:22px 24px;
                        border-radius:14px;
                        border:1px solid #F2D9A6;
                        display:flex;
                        justify-content:space-between;
                        align-items:center;
                        margin-bottom:18px;
                    ">
                        <h4 style="margin:0; font-weight:700; font-size:22px;">{provider} Bill Breakdown</h4>
                        <h4 style="margin:0; color:#C27B00; font-size:22px;">₱{total_cost:.2f}</h4>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                bg_colors = [
                    "#FFF2CC", "#E8FFEE", "#EAF2FF", "#F7E8FF",
                    "#FFE8E8", "#EBEEFF", "#FFEDE5"
                ]
                text_colors = [
                    "#C27B00", "#008C4C", "#1D3FAA", "#8A2EB8",
                    "#C72A3B", "#0031A8", "#C72A00"
                ]

                for i, (label, amt, pct) in enumerate(comps):
                    bg = bg_colors[i % len(bg_colors)]
                    color = text_colors[i % len(text_colors)]

                    st.markdown(
                        f"""
                        <div style="
                            background:{bg};
                            padding:16px 20px;
                            margin-bottom:12px;
                            border-radius:16px;
                            border:1px solid #e4e4e4;
                            display:flex;
                            justify-content:space-between;
                            align-items:center;
                            font-size:16px;
                            font-weight:600;
                            box-shadow:0 1px 3px rgba(0,0,0,0.06);
                        ">
                            <span>{label} ({pct}%)</span>
                            <span style="color:{color}; font-weight:700;">₱{amt:.2f}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            with right:
                labels = [c[0] for c in comps]
                values = [c[1] for c in comps]

                fig = px.pie(
                    names=labels,
                    values=values,
                    title="Bill Breakdown",
                    hole=0.28
                )

                fig.update_traces(
                    text=[
                        f"{label}<br>₱{value:,.2f}"
                        for label, value in zip(labels, values)
                    ],
                    textposition="inside",
                    insidetextorientation="auto",
                    hovertemplate="%{label}<br>₱%{value:,.2f}<extra></extra>",
                    textfont_size=13
                )

                fig.update_layout(
                    height=540,
                    width=540,
                    margin=dict(l=0, r=0, t=40, b=0),
                    showlegend=False
                )

                st.plotly_chart(fig, use_container_width=True)

        # -------------------- COMPARISON --------------------
        if st.session_state.show_comparison:
            st.markdown("### 📊 Monthly Cost Comparison")

            reports = st.session_state.monthly_reports

            if not reports:
                st.info("No saved monthly reports yet. Generate a report first.")
            else:
                months = []
                costs = []

                for m, data in reports.items():
                    months.append(m)
                    costs.append(data["total_cost"])

                df_comp = pd.DataFrame({
                    "Month": months,
                    "Cost (₱)": costs
                })

                fig = px.bar(
                    df_comp,
                    x="Month",
                    y="Cost (₱)",
                    title="Monthly Cost Comparison",
                    text_auto='.2f',
                    color="Cost (₱)",
                    color_continuous_scale="Teal"
                )

                fig.update_layout(
                    xaxis_title="Month",
                    yaxis_title="Cost (₱)",
                    height=520,
                    showlegend=False
                )

                st.plotly_chart(fig, use_container_width=True)

                if len(costs) >= 2:
                    current_cost = costs[-1]
                    previous_cost = costs[-2]
                    cost_diff = current_cost - previous_cost
                    percent_change = (cost_diff / previous_cost) * 100 if previous_cost != 0 else 0

                    if cost_diff > 0:
                        feedback_color = "#FFEBEE"
                        border_color = "#C62828"
                        icon = "📈"
                        status = "increased"
                        advice = "Consider reducing usage of high-consumption appliances or switching to more energy-efficient alternatives."
                    elif cost_diff < 0:
                        feedback_color = "#E8F5E9"
                        border_color = "#2E7D32"
                        icon = "📉"
                        status = "decreased"
                        advice = "Great job! Keep maintaining your energy-efficient habits."
                    else:
                        feedback_color = "#FFF3E0"
                        border_color = "#F57C00"
                        icon = "➡️"
                        status = "remained the same"
                        advice = "Your consumption is stable. Continue monitoring for optimization opportunities."

                    st.markdown(f"""
                    <div style="
                        background:{feedback_color};
                        padding:20px;
                        border-radius:12px;
                        border-left:6px solid {border_color};
                        margin-top:20px;
                    ">
                        <h4 style="margin-top:0;">{icon} Cost Change Analysis</h4>
                        <p style="font-size:16px;">
                            <b>Previous Month ({months[-2]}):</b> ₱{previous_cost:,.2f}<br>
                            <b>Current Month ({months[-1]}):</b> ₱{current_cost:,.2f}<br>
                            <b>Change:</b> ₱{abs(cost_diff):,.2f} ({abs(percent_change):.1f}%)
                        </p>
                        <p style="font-size:15px; margin-bottom:0;">
                            Your electricity cost has <b>{status}</b> compared to the previous month.<br>
                            💡 <i>{advice}</i>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("💡 Generate reports for at least 2 months to see cost change analysis.")

    else:
        st.info("No appliances to display for this month.")

# -------------------- Energy Efficiency --------------------
elif st.session_state.page == "Energy Efficiency":

    st.subheader("⚡ Energy Efficiency & Appliance Wattage Guide")

    st.markdown("""
    Knowing the wattage of your appliances helps you understand which devices consume the most energy.  
    Lower-wattage and inverter appliances are more efficient and cost less to operate.
    """)

    st.markdown("""
    <div style="
        background:#FFF8E1;
        padding:12px 18px;
        border-left:5px solid #F9A825;
        border-radius:8px;
        margin-bottom:20px;
        font-size:14px;">
    ⚠️ <b>Note:</b> Wattage values shown below are average estimates.  
    Actual wattage may be <b>higher or lower</b> depending on appliance model, age, and usage patterns.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background:#F1F8E9;
        padding:20px;
        border-radius:12px;
        border-left:6px solid #2E7D32;
        margin-bottom:20px;">
        <h4>💡 General Energy Efficiency Tips</h4>
        <ul>
            <li>Use LED bulbs instead of incandescent bulbs</li>
            <li>Unplug appliances when not in use to reduce phantom load</li>
            <li>Choose inverter models for refrigerators, AC units, and washing machines</li>
            <li>Limit the use of high-wattage cooking appliances when possible</li>
            <li>Clean air filters and maintain appliances regularly for optimal efficiency</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## Appliance Wattage Reference Tables")

    # -------------------- KITCHEN APPLIANCES --------------------
    st.markdown("""
    <div style="
        background:#FFF3E0;
        padding:12px 18px;
        border-left:5px solid #FB8C00;
        border-radius:8px;
        margin-bottom:10px;
        font-size:18px;">
     <b>Kitchen Appliances</b>
    </div>
    """, unsafe_allow_html=True)

    kitchen_data = {
        "Appliances": [
            "Refrigerator", "Freezer", "Electric Oven", "Microwave", "Dishwasher",
            "Toaster", "Electric Kettle", "Coffee Maker", "Blender",
            "Electric Stove Burner", "Toaster Oven", "Slow Cooker",
            "Food Processor", "Stand Mixer", "Hand Mixer",
            "Juicer", "Rice Cooker", "Deep Fryer", "Electric Grill"
        ],
        "Average Wattage (W)": [
            "150-200", "150-200", "1000-5000", "600-1200", "1200-2400",
            "800-1500", "1000-1500", "600-1200", "300-1000",
            "1000-3000 per burner", "1200-1800", "70-250",
            "400-1000", "250-500", "100-200",
            "500-1000", "450-1000", "1200-2200", "1200-2000"
        ]
    }
    st.dataframe(pd.DataFrame(kitchen_data), use_container_width=True)

    # -------------------- LAUNDRY APPLIANCES --------------------
    st.markdown("""
    <div style="
        background:#FFF3E0;
        padding:12px 18px;
        border-left:5px solid #FB8C00;
        border-radius:8px;
        margin-bottom:10px;
        font-size:18px;">
     <b>Laundry Appliances</b>
    </div>
    """, unsafe_allow_html=True)

    laundry_data = {
        "Appliances": [
            "Washing Machine", "Clothes Dryer (Electric)", "Clothes Dryer (Gas)",
            "Iron", "Steam Iron", "Clothes Steamer",
            "Sewing Machine", "Handheld Fabric Steamer"
        ],
        "Average Wattage (W)": [
            "500-1000", "1800-5000", "300-400 (electrical component)",
            "1000-1800", "1200-2000", "1200-1800",
            "75-100", "800-1200"
        ]
    }
    st.dataframe(pd.DataFrame(laundry_data), use_container_width=True)

    # -------------------- ENTERTAINMENT APPLIANCES --------------------
    st.markdown("""
    <div style="
        background:#FFF3E0;
        padding:12px 18px;
        border-left:5px solid #FB8C00;
        border-radius:8px;
        margin-bottom:10px;
        font-size:18px;">
     <b>Entertainment Appliances</b>
    </div>
    """, unsafe_allow_html=True)

    entertainment_data = {
        "Appliances": [
            "Television (LED)", "Television (LCD)", "Television (Plasma)",
            "DVD Player", "Blu-ray Player", "Game Console", "Soundbar",
            "Home Theater System", "Stereo Receiver", "Projector",
            "CD Player", "Radio", "Desktop Computer", "Laptop",
            "Modem/Router", "Streaming Device"
        ],
        "Average Wattage (W)": [
            "30-100", "50-200", "100-400", "10-20", "15-30",
            "30-200", "20-50", "200-500", "100-400", "150-800",
            "15-30", "50-200", "100-800", "20-75",
            "5-20", "2-15"
        ]
    }
    st.dataframe(pd.DataFrame(entertainment_data), use_container_width=True)

    # -------------------- ESSENTIAL HOME APPLIANCES --------------------
    st.markdown("""
    <div style="
        background:#FFF3E0;
        padding:12px 18px;
        border-left:5px solid #FB8C00;
        border-radius:8px;
        margin-bottom:10px;
        font-size:18px;">
     <b>Essential Home Appliances</b>
    </div>
    """, unsafe_allow_html=True)

    home_data = {
        "Appliances": [
            "Refrigerator", "Freezer", "Electric Oven", "Microwave", "Dishwasher",
            "Toaster", "Electric Kettle", "Coffee Maker", "Blender",
            "Electric Stove Burner", "Washing Machine", "Clothes Dryer",
            "Iron", "Hair Dryer", "Vacuum Cleaner",
            "Television", "Computer", "Laptop",
            "Air Conditioner", "Space Heater", "Ceiling Fan",
            "LED Light Bulb", "Incandescent Bulb"
        ],
        "Average Wattage (W)": [
            "150-200", "150-200", "1000-5000", "600-1200", "1200-2400",
            "800-1500", "1000-1500", "600-1200", "300-1000",
            "1000-3000", "500-1000", "1800-5000",
            "1000-1800", "1000-1875", "500-2000",
            "50-400", "100-800", "20-75",
            "900-5000", "750-1500", "65-175",
            "8-12", "60-100"
        ]
    }
    st.dataframe(pd.DataFrame(home_data), use_container_width=True)

    st.markdown("""
    <div style="
        margin-top:25px;
        padding:15px;
        background:#F5F5F5;
        border-left:5px solid #616161;
        border-radius:8px;
        font-size:14px;">
    <b>Reference:</b><br>
    cGuire, W. (2023, July 24). List Of All Electric Appliances And Their Wattage Usage ([cy]).</i><br>
    https://www.fypower.org/electric-appliances-and-their-wattage-usage/
    </div>
    """, unsafe_allow_html=True)

# -------------------- Carbon Footprint --------------------
elif st.session_state.page == "Carbon Footprint":
    st.title("🌍 Carbon Footprint")
    st.caption("Understand your environmental impact")

    st.markdown("### 🍃 Calculate Carbon Emissions")

    if st.button("Calculate Impact", use_container_width=True):
        st.session_state.calc_carbon = True

    if st.session_state.get("calc_carbon", False):

        if st.session_state.appliances:

            df = pd.DataFrame(st.session_state.appliances)

            CO2_PER_KWH = 0.62

            daily_energy = df["energy_kwh"].sum()
            monthly_energy = daily_energy * 30
            yearly_energy = daily_energy * 365

            daily_co2 = daily_energy * CO2_PER_KWH
            monthly_co2 = monthly_energy * CO2_PER_KWH
            yearly_co2 = yearly_energy * CO2_PER_KWH

            trees_needed = int(yearly_co2 / 21)  

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div style="background:#E8F5E9; padding:20px; border-radius:12px;">
                    <h5>Daily CO₂</h5>
                    <h2 style="color:#1B5E20;">{daily_co2:.2f}</h2>
                    <p>kg CO₂</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="background:#E3F2FD; padding:20px; border-radius:12px;">
                    <h5>Monthly CO₂</h5>
                    <h2 style="color:#0D47A1;">{monthly_co2:.2f}</h2>
                    <p>kg CO₂</p>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div style="background:#FFF3E0; padding:20px; border-radius:12px;">
                    <h5>Yearly CO₂</h5>
                    <h2 style="color:#BF360C;">{yearly_co2:.2f}</h2>
                    <p>kg CO₂</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#1B5E20; padding:30px; border-radius:15px; color:white; margin-top:20px;">
                <h4>🌲 Trees Needed to Offset</h4>
                <h1>{trees_needed}</h1>
                trees needed to absorb your yearly CO₂ emissions
                <p style="font-size:12px; margin-top:10px;">
                    * Based on average tree absorption of 21 kg CO₂/year
                </p>
            </div>
            """, unsafe_allow_html=True)

            # ---------- CO₂ EMISSIONS COMPARISON ----------
            st.markdown("""
                <div style="
                background:#FFFFFF;
                border:1px solid #C8DCD3;
                padding:10px 15px;
                border-radius:10px;
                margin-top:20px;
                margin-bottom:15px;
                ">
            """, unsafe_allow_html=True)

            labels = ["Daily", "Monthly", "Yearly"]
            values = [daily_co2, monthly_co2, yearly_co2]

            fig = px.bar(
                x=labels,
                y=values,
                text_auto='.2f',
                title="CO₂ Emissions (Daily vs Monthly vs Yearly)"
            )
            fig.update_layout(
                xaxis_title="Time Period",
                yaxis_title="kg CO₂",
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)


            # ---------- Carbon Offset Calculator ----------
            st.markdown("### 🌿 Carbon Offset Calculator")

            offset_actions = {
                "Increase AC Temperature by 1°C": 0.178,        
                "Use LED bulbs instead of incandescent": 0.465,  
                "Unplug idle devices (standby power reduction)": None,  
                "Turn off lights when not in use": None,
                "Plant a tree": 21 / 365,                        
            }

            selected_action = st.selectbox(
                "Choose an action to estimate your CO₂ reduction:",
                list(offset_actions.keys())
            )

            if selected_action == "Plant a tree":
                count = st.slider("How many trees will you plant?", 1, 50, 1)
                co2_saved = offset_actions[selected_action] * count

            elif selected_action == "Unplug idle devices (standby power reduction)":
                standby_power_per_device = 0.074  
                num_devices = st.slider("How many idle devices will you unplug?", 1, 10, 1)
                co2_saved = standby_power_per_device * num_devices

            elif selected_action == "Increase AC Temperature by 1°C":
                degrees = st.slider("Increase temperature by (°C):", 1, 5, 1)
                co2_saved = offset_actions[selected_action] * degrees

            elif selected_action == "Turn off lights when not in use":
                num_bulbs = st.slider("Number of bulbs to turn off:", 1, 20, 1)
                hours_saved = st.slider("Hours lights will be off per day:", 1, 12, 1)
                co2_saved = 0.01 * hours_saved * 0.62 * num_bulbs  

            else:
                count = st.slider("How many times will you apply this action?", 1, 10, 1)
                co2_saved = offset_actions[selected_action] * count

            daily_reduction = co2_saved
            monthly_reduction = daily_reduction * 30
            yearly_reduction = daily_reduction * 365

            st.markdown(f"""
            <div style="
                background:#E8F5E9;
                padding:25px;
                border-radius:12px;
                border-left: 6px solid #2E7D32;
                margin-top:15px;
            ">
                <h4>🌱 Estimated CO₂ Reduction</h4>
                <p><b>Daily reduction:</b> {daily_reduction:.2f} kg CO₂</p>
                <p><b>Monthly reduction:</b> {monthly_reduction:.2f} kg CO₂</p>
                <p><b>Yearly reduction:</b> {yearly_reduction:.2f} kg CO₂</p>
                <p style="font-size:1em; color:#666; margin-top:12px; font-style:italic;">
                    ⚠️ Note: These values are estimates based on average conditions. 
                    Actual CO₂ reductions may vary depending on factors such as climate, 
                    energy sources, equipment efficiency, and usage patterns.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="
                border: 2px solid #1B5E20;
                padding: 25px;
                border-radius: 12px;
                background-color: #F1F8E9;
                margin-top: 25px;
            ">
                <h3>💡 Ways to Reduce Your Carbon Footprint:</h3>
                <ul>
                    <li>Switch to renewable energy sources (solar panels)</li>
                    <li>Use energy-efficient appliances with high EER ratings</li>
                    <li>Reduce usage during peak hours</li>
                    <li>Implement smart home automation for better control</li>
                    <li>Regular maintenance of appliances for optimal efficiency</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.info("No appliances found. Add appliances first to calculate CO₂.")

# ===================== Work & Energy Calculator =====================
elif st.session_state.page == "Work & Energy Analysis":

    st.markdown("""
    <div style="
        background:#F1F8E9;
        padding:20px;
        border-radius:15px;
        border-left:6px solid #33691E;
        margin-bottom:20px;
    ">
        <h3 style="color:#1B5E20; margin-top:0;">
            🔍 Understanding How Work and Energy Affect Power Consumption
        </h3>
        <p style="font-size:16px;">
            Work and energy concepts help explain how appliances use electricity.<br>
            Greater work or power output requires more electrical energy.<br>
            By understanding how movement, lifting, and force demand energy,
            users can make smarter appliance choices and reduce unnecessary consumption.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # -------------------- WORK & POWER SECTION --------------------
    st.markdown("### 📘 Work & Power Calculator")

    col1WP, col2WP = st.columns(2)
    with col1WP:
        force = st.number_input("Force (Newtons)", min_value=0.0, step=1.0, key="force_wp")
        distance = st.number_input("Distance (meters)", min_value=0.0, step=0.1, key="dist_wp")
    with col2WP:
        time_wp = st.number_input("Time (seconds)", min_value=0.0, step=0.1, key="time_wp")

    if st.button("Calculate Work & Power", use_container_width=True, key="calc_wp"):
        if force == 0 or distance == 0 or time_wp == 0:
            st.warning("Please enter values greater than zero.")
        else:
            work = force * distance
            power = work / time_wp

            st.markdown(f"""
            <div style="
                background:#E8F5E9;
                padding:25px;
                border-radius:15px;
                border-left:6px solid #2E7D32;
                margin-top:15px;
            ">
                <h4 style="color:#1B5E20; margin-top:0;">📊 Work & Power Results</h4>
                <p><b>Work:</b> {work:.2f} Joules (J)</p>
                <p><b>Power:</b> {power:.2f} Watts (W)</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ===================== KINETIC & POTENTIAL ENERGY =====================
    st.markdown("### ⚡ Kinetic & Potential Energy Calculator")

    col3, col4 = st.columns(2)
    with col3:
        mass_ke = st.number_input("Mass (kg)", min_value=0.0, step=0.1, key="mass_ke")
        velocity_ke = st.number_input("Velocity (m/s)", min_value=0.0, step=0.1, key="vel_ke")

    with col4:
        mass_pe = st.number_input("Mass (kg) for PE", min_value=0.0, step=0.1, key="mass_pe")
        height_pe = st.number_input("Height (meters)", min_value=0.0, step=0.1, key="height_pe")
        g = 9.8

    if st.button("Calculate Energy", use_container_width=True, key="calc_kepe"):

        ke = None
        pe = None

        if mass_ke > 0 and velocity_ke > 0:
            ke = 0.5 * mass_ke * (velocity_ke ** 2)

        if mass_pe > 0 and height_pe > 0:
            pe = mass_pe * g * height_pe

        result_html = """
        <div style="
            background:#E8F5E9;
            padding:25px;
            border-radius:15px;
            border-left:6px solid #2E7D32;
            margin-top:15px;
        ">
            <h4 style="color:#1B5E20; margin-top:0;">⚡ Energy Results</h4>
        """

        if ke is not None:
            result_html += f"<p><b>Kinetic Energy (KE):</b> {ke:.2f} Joules</p>"
        else:
            result_html += "<p><b>Kinetic Energy (KE):</b> Not enough data</p>"

        if pe is not None:
            result_html += f"<p><b>Potential Energy (PE):</b> {pe:.2f} Joules</p>"
        else:
            result_html += "<p><b>Potential Energy (PE):</b> Not enough data</p>"

        result_html += "</div>"

        st.markdown(result_html, unsafe_allow_html=True)
