import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from fpdf import FPDF
import io

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Pune Real Estate AI | Shubham Sharma", page_icon="🏠", layout="wide"
)

# --- CUSTOM CSS FOR UI/UX & OVERFLOW ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Container Padding */
    .main {
        padding: 2rem;
        background-color: #f8f9fa;
    }

    /* Metric Card Styling & Overflow Prevention */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 800;
        color: #1E3A8A;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Card Backgrounds */
    div[data-testid="column"] {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }

    /* Footer Styling */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6B7280;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- UTILITY FUNCTIONS ---
def format_indian_currency(num):
    """Formats number to Indian Currency System (Lakhs/Crores)"""
    num = round(num * 100000)  # Convert Lakhs to actual Rupee value
    s, temp = str(num), ""
    if len(s) <= 3:
        return "₹" + s
    last_three = s[-3:]
    other_parts = s[:-3]
    if other_parts != "":
        last_three = "," + last_three
    while len(other_parts) > 2:
        temp = "," + other_parts[-2:] + temp
        other_parts = other_parts[:-2]
    return "₹" + other_parts + temp + last_three


def generate_ai_insight(loc, mun, p_type, bhk, area, floor, age):
    """Dynamic Insight Engine"""
    insights = []

    # 1. Size Analysis
    avg_area_per_bhk = area / bhk
    if avg_area_per_bhk > 700:
        insights.append(
            f"This {bhk} BHK is exceptionally spacious compared to standard Pune configurations."
        )
    elif avg_area_per_bhk < 450:
        insights.append(
            f"The layout is compact; ideal for rental yield but may feel small for self-use."
        )

    # 2. Age & Maintenance
    if age <= 2:
        insights.append(
            "Being a 'New' property, expect modern amenities and higher appreciation in the first 5 years."
        )
    elif age > 10:
        insights.append(
            "The property is aging; ensure you check the society maintenance and renovation history."
        )

    # 3. Location Specifics
    if loc in ["Baner", "Viman Nagar", "Kothrud"]:
        insights.append(
            f"{loc} is a high-demand premium corridor in {mun}; resale liquidity here is excellent."
        )
    else:
        insights.append(
            f"{loc} in {mun} is a growing IT hub; great for steady rental income from working professionals."
        )

    # 4. Special Features
    if floor > 15:
        insights.append(
            "The high-floor placement adds a significant 'view premium' to the valuation."
        )
    if p_type == "Bungalow":
        insights.append(
            "Bungalows are rare in this area; you are paying for land value and long-term privacy."
        )

    return " ".join(insights[:3])  # Return top 3 relevant insights


def generate_pdf(data_summary, price, price_lakhs, insight):
    pdf = FPDF()
    pdf.add_page()

    # --- Professional Branding ---
    pdf.set_fill_color(30, 58, 138)  # Pune Navy Blue
    pdf.rect(0, 0, 210, 40, "F")

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 24)
    pdf.cell(0, 20, "VALUATION CERTIFICATE", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(
        0,
        5,
        f"Issued by Pune Estates AI Intelligence Terminal | {datetime.now().strftime('%d %b %Y')}",
        ln=True,
        align="C",
    )

    # --- Main Price Box ---
    pdf.ln(20)
    pdf.set_text_color(30, 58, 138)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "ESTIMATED MARKET VALUATION", ln=True, align="L")

    pdf.set_fill_color(240, 244, 248)
    pdf.set_font("Arial", "B", 28)
    clean_price = str(price).replace("₹", "Rs. ")
    pdf.cell(0, 25, f"{clean_price}", ln=True, align="C", fill=True)
    pdf.ln(10)

    # --- Property Specs Grid ---
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "PROPERTY CONFIGURATION", ln=1)
    pdf.set_draw_color(200, 200, 200)

    pdf.set_font("Arial", "", 11)
    col_width = 95
    for key, value in data_summary.items():
        clean_val = str(value).replace("₹", "Rs. ")
        pdf.set_font("Arial", "B", 10)
        pdf.cell(col_width, 10, f" {key.upper()}", border="B")
        pdf.set_font("Arial", "", 10)
        pdf.cell(col_width, 10, f" {clean_val}", border="B", ln=1)

    # --- AI Analysis Section ---
    pdf.ln(15)
    pdf.set_fill_color(232, 245, 233)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, " AI MARKET INSIGHTS", ln=True, fill=True)

    pdf.set_font("Arial", "I", 11)
    pdf.set_text_color(50, 50, 50)
    clean_insight = str(insight).replace("₹", "Rs. ")
    pdf.multi_cell(0, 10, clean_insight)

    # --- Footer Signature ---
    pdf.set_y(-40)
    pdf.set_draw_color(30, 58, 138)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 5, "Shubham Sharma", ln=True, align="R")
    pdf.set_font("Arial", "", 8)
    pdf.cell(0, 5, "Principal Developer & Data Architect", ln=True, align="R")

    return pdf.output(dest="S").encode("latin-1", "ignore")


@st.cache_resource
def load_assets():
    model = joblib.load("pune_real_estate_model.pkl")
    return model


# --- LOGIC ---
model = load_assets()

# --- HEADER ---
st.title("🏙️ Pune Premium Estates AI")
st.markdown(
    f"**Market Intelligence Engine** | Data-driven valuations for PMC & PCMC regions."
)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Property Inputs")
    locality = st.selectbox(
        "Locality", ["Kothrud", "Baner", "Viman Nagar", "Hinjewadi", "Wakad", "Pimpri"]
    )
    municipality = "PMC" if locality in ["Kothrud", "Baner", "Viman Nagar"] else "PCMC"

    prop_type = st.segmented_control(
        "Property Type", ["Flat", "Bungalow"], default="Flat"
    )
    bhk = st.slider("BHK Configuration", 1, 5, 2)
    carpet_area = st.number_input("Carpet Area (Sq.Ft)", 400, 5000, 1050)

    if prop_type == "Flat":
        floor = st.slider("Floor", 0, 25, 8)
    else:
        floor = 0

    parking = st.radio("Parking Slots", [1, 2, 3], horizontal=True)
    age = st.number_input("Age of Property (Years)", 0, 15, 2)

    predict_btn = st.button("Generate Valuation Report")


# --- DATA PREPARATION ---
input_df = pd.DataFrame(
    {
        "Locality": [locality],
        "Municipality": [municipality],
        "Property_Type": [prop_type],
        "BHK": [bhk],
        "Carpet_Area_SqFt": [carpet_area],
        "Floor_No": [floor],
        "Parking_Spaces": [parking],
        "Age_Years": [age],
    }
)

# --- PREDICTION ---
raw_pred = model.predict(input_df)[0]
price_lakhs = np.expm1(raw_pred)
human_readable_price = format_indian_currency(price_lakhs)

# --- MAIN DASHBOARD ---
col_main, col_stats = st.columns([3, 2], gap="large")

with col_main:
    st.subheader("Property Valuation")

    # Hero Metric
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric("Estimated Market Value", human_readable_price)
    with m_col2:
        psf = (price_lakhs * 100000) / carpet_area
        st.metric("Rate per Sq.Ft", f"₹{int(psf):,}")

    # Visual Gauge
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=price_lakhs,
            title={"text": "Market Position (Lakhs)", "font": {"size": 20}},
            gauge={
                "axis": {"range": [None, 800], "tickcolor": "#1E3A8A"},
                "bar": {"color": "#1E3A8A"},
                "steps": [
                    {"range": [0, 150], "color": "#D1FAE5"},
                    {"range": [150, 450], "color": "#FEF3C7"},
                    {"range": [450, 800], "color": "#FEE2E2"},
                ],
                "threshold": {
                    "line": {"color": "black", "width": 4},
                    "value": price_lakhs,
                },
            },
        )
    )
    fig.update_layout(height=400, margin=dict(t=50, b=0))
    st.plotly_chart(fig, use_container_width=True)

with col_stats:
    st.subheader("Asset Scorecard")

    # Feature Strength Radar
    categories = ["Area", "BHK", "Newness", "Parking"]
    # Normalizing values for 0-10 scale
    r_values = [
        (carpet_area / 5000) * 10,
        (bhk / 5) * 10,
        (1 - age / 15) * 10,
        (parking / 3) * 10,
    ]

    fig_radar = go.Figure(
        data=go.Scatterpolar(
            r=r_values, theta=categories, fill="toself", line_color="#1E3A8A"
        )
    )
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])), height=350
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # --- DYNAMIC AI INSIGHT ---
    dynamic_text = generate_ai_insight(
        locality, municipality, prop_type, bhk, carpet_area, floor, age
    )
    st.info(f"💡 **AI Insight for {locality}:** {dynamic_text}")


# --- INVESTMENT PROJECTION ---
st.subheader("📈 5-Year Appreciation Forecast")
years = [datetime.now().year + i for i in range(6)]
forecast = [price_lakhs * (1.085**i) for i in range(6)]  # Assuming 8.5% annual growth

fig_growth = px.area(
    x=years,
    y=forecast,
    labels={"x": "Year", "y": "Value (Lakhs)"},
    title="Projected Capital Appreciation",
)
fig_growth.update_traces(line_color="#10B981")
st.plotly_chart(fig_growth, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
current_year = datetime.now().year

footer_html = f"""
    <div class="footer">
        <p>Developed with ❤️ by <b>Shubham Sharma</b></p>
        <p>© {current_year} | Pune Estates Intelligence Terminal | All Rights Reserved</p>
    </div>
"""
st.markdown(footer_html, unsafe_allow_html=True)


# --- PDF GENERATION LOGIC (Add at bottom of file) ---
if predict_btn:
    # 1. Prepare data summary
    summary = {
        "Locality": locality,
        "Municipality": municipality,
        "Type": prop_type,
        "BHK": f"{bhk} BHK",
        "Area": f"{carpet_area} Sq.Ft",
        "Floor": floor,
        "Age": f"{age} Years",
        "Rate/Sq.Ft": f"Rs. {int((price_lakhs * 100000) / carpet_area):,}",
    }

    # 2. Generate PDF using the function we defined earlier
    try:
        pdf_bytes = generate_pdf(
            summary, human_readable_price, price_lakhs, dynamic_text
        )

        # 3. Place the download button BACK into the sidebar
        st.sidebar.success("✅ Report Generated!")
        st.sidebar.download_button(
            label="📥 Download PDF Report",
            data=pdf_bytes,
            file_name=f"Pune_Estates_{locality}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
        )
    except Exception as e:
        st.sidebar.error(f"Error generating PDF: {e}")
