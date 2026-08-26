import time
import re
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
from google.cloud import bigquery
from google.cloud import vision

st.set_page_config(
    page_title="AutoClaims AI | Multi-Branch Lakehouse",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

PROJECT_ID = "project-da31f5f4-7cad-4b47-a17"
DATASET_ID = f"{PROJECT_ID}.two_wheeler_insurance"

st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 8px; height: 44px; font-weight: 600; }
    .status-badge { padding: 4px 10px; border-radius: 6px; font-size: 13px; font-weight: 600; display: inline-block; }
    .badge-active { background-color: #dcfce7; color: #166534; }
    .badge-expired { background-color: #fee2e2; color: #991b1b; }
    .info-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

bq_client = bigquery.Client(project=PROJECT_ID)
vision_client = vision.ImageAnnotatorClient()

if "hq_authenticated" not in st.session_state:
    st.session_state.hq_authenticated = False

st.sidebar.title("🛡️ AutoClaims AI")
st.sidebar.caption("Two-Wheeler Multi-Branch Operations")

branch_role = st.sidebar.radio(
    "Select Operational Desk:",
    ["🏢 Sub Branch (Intake & Filing)", "🏛️ Main Branch (Admin Protected)"]
)

# 1. SUB BRANCH DESK
if branch_role == "🏢 Sub Branch (Intake & Filing)":
    st.title("🏢 Sub Branch Operations Desk")
    st.caption("Register new policyholders, run AI document checks, and dispatch claims to Main Branch.")
    
    sub_tab1, sub_tab2 = st.tabs(["🚀 File & Dispatch Claim", "➕ Onboard Customer & Issue Policy"])
    
    with sub_tab1:
        sub_branch_name = st.selectbox("Submitting Sub Branch:", [
            "Theni Regional Sub Branch",
            "Madurai South Sub Branch",
            "Chennai Central Sub Branch",
            "Coimbatore West Sub Branch"
        ])
        
        pol_df = bq_client.query(f"SELECT policy_id, policyholder_name, registration_no, bike_model_year, engine_cc, insurance_type, idv_amount, policy_status FROM `{DATASET_ID}.policies_master` ORDER BY created_timestamp DESC LIMIT 1000;").to_dataframe()

        if not pol_df.empty:
            col_l, col_r = st.columns([1, 1], gap="large")
            with col_l:
                st.markdown("#### 1️⃣ Select Customer Policy")
                chosen_pid = st.selectbox("Policy Number:", pol_df['policy_id'].tolist()[:200], format_func=lambda x: f"{x} - {pol_df[pol_df['policy_id']==x]['policyholder_name'].values[0]} ({pol_df[pol_df['policy_id']==x]['registration_no'].values[0]})")
                sel_pol = pol_df[pol_df['policy_id'] == chosen_pid].iloc[0]
                status_class = "badge-active" if sel_pol['policy_status'] == "ACTIVE" else "badge-expired"
                
                st.markdown(f"""
                <div class="info-card">
                    <b>Customer:</b> {sel_pol['policyholder_name']}<br>
                    <b>Bike:</b> {sel_pol['bike_model_year']} ({sel_pol['engine_cc']} CC)<br>
                    <b>Plate / RC:</b> <code>{sel_pol['registration_no']}</code><br>
                    <b>Coverage:</b> {sel_pol['insurance_type']} &nbsp;|&nbsp; <b>IDV:</b> ₹{sel_pol['idv_amount']:,}<br>
                    <b>Status:</b> <span class="status-badge {status_class}">{sel_pol['policy_status']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 2️⃣ AI Document Verification (RC Card)")
                up_rc = st.file_uploader("Upload RC Photo / Scan", type=["png", "jpg", "jpeg"])
                if up_rc is not None:
                    st.image(up_rc, caption="Uploaded Document", width=220)
                    if st.button("🔍 Run In-Memory AI OCR Scan", type="secondary"):
                        with st.spinner("Analyzing document..."):
                            img_data = up_rc.getvalue()
                            v_resp = vision_client.text_detection(image=vision.Image(content=img_data))
                            full_txt = v_resp.text_annotations[0].description if v_resp.text_annotations else ""
                            patterns = [r'[A-Z]{2}[-\s]?[0-9]{1,2}[-\s]?[A-Z]{1,3}[-\s]?[0-9]{4}', r'[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}', r'TN[0-9]{2}[A-Z]{1,2}[0-9]{4}']
                            clean_str = " ".join(full_txt.split()).upper()
                            detected_plate = "NOT_SCANNED"
                            for pat in patterns:
                                m = re.search(pat, clean_str)
                                if m:
                                    detected_plate = m.group(0).replace(" ", "").replace("-", "")
                                    break
                            st.info(f"Extracted Plate: {detected_plate}")

            with col_r:
                st.markdown("#### 3️⃣ Repair Estimatics & Intimation")
                loc_txt = st.text_input("Accident Location", f"{sub_branch_name.split()[0]} Main Road")
                g_type = st.radio("Garage Category", ["NETWORK (Cashless)", "NON_NETWORK (Reimbursement)"], horizontal=True)
                g_name = st.text_input("Workshop Name", "City Speed Auto Service")
                
                c_p1, c_p2 = st.columns(2)
                with c_p1:
                    m_cost = st.number_input("Metal Parts (₹)", value=6000, step=500)
                    p_cost = st.number_input("Plastic Parts (50% Dep.) (₹)", value=4000, step=500)
                with c_p2:
                    l_cost = st.number_input("Labour & Paint (₹)", value=2500, step=500)
                    deductible = 1000
                
                settlement_est = max(0.0, (m_cost * 0.90) + (p_cost * 0.50) + l_cost - deductible)
                st.markdown(f"**Net Calculated Payout:** ₹{settlement_est:,.2f}")
                notes = st.text_area("Sub Branch Remarks", "Survey verified against damages.")
                
                if st.button("🚀 Dispatch Claim to Main Branch", type="primary"):
                    new_claim_id = f"CLM-{int(time.time()) % 10000}"
                    clean_g = "NETWORK" if "NETWORK" in g_type and "NON" not in g_type else "NON_NETWORK"
                    sql = f"""
                    INSERT INTO `{DATASET_ID}.claims_ledger`
                    (claim_id, policy_id, sub_branch, incident_location, incident_description, garage_type, garage_name, estimated_amount, claim_status, created_timestamp)
                    VALUES ('{new_claim_id}', '{chosen_pid}', '{sub_branch_name}', '{loc_txt}', '{notes}', '{clean_g}', '{g_name}', {settlement_est}, 'PENDING_MAIN_BRANCH_REVIEW', CURRENT_TIMESTAMP());
                    """
                    bq_client.query(sql).result()
                    st.success(f"🎉 Claim #{new_claim_id} dispatched to Main Branch!")

    with sub_tab2:
        st.markdown("#### ➕ New Customer Policy Registration")
        in1, in2 = st.columns(2)
        with in1:
            cust_name = st.text_input("Customer Name", "Ramesh Kumar")
            rc_no = st.text_input("Bike RC Number", "TN-57-AZ-1122")
            aadhaar_ref = st.text_input("National ID Reference", type="password")
        with in2:
            bike_model_yr = st.text_input("Bike Model & Year", "TVS Apache RTR 160 (2024)")
            bike_cc = st.number_input("Engine CC", value=160, step=10)
            ins_type = st.selectbox("Insurance Type", ["Comprehensive", "Full Coverage (Zero Dep)"])
            idv_val = st.number_input("IDV Amount (₹)", value=125000, step=5000)
            
        if st.button("📋 Issue & Activate Policy", type="primary"):
            new_pid = f"POL-TN-{int(time.time()) % 10000}"
            insert_sql = f"""
            INSERT INTO `{DATASET_ID}.policies_master`
            (policy_id, policyholder_name, registration_no, id_reference, bike_model_year, engine_cc, insurance_type, idv_amount, policy_status, created_timestamp)
            VALUES ('{new_pid}', '{cust_name}', '{rc_no.upper()}', '[ID Redacted]', '{bike_model_yr}', {bike_cc}, '{ins_type}', {idv_val}, 'ACTIVE', CURRENT_TIMESTAMP());
            """
            bq_client.query(insert_sql).result()
            st.success(f"🎉 Policy #{new_pid} issued successfully!")

# 2. MAIN BRANCH DESK
elif branch_role == "🏛️ Main Branch (Admin Protected)":
    if not st.session_state.hq_authenticated:
        st.title("🏛️ Main Branch Access Gate")
        st.caption("Central Adjudication & Executive Intelligence Console")
        
        col_auth1, col_auth2, col_auth3 = st.columns([1, 1.5, 1])
        with col_auth2:
            st.markdown("""
            <div class="info-card">
                <h4 style="margin:0 0 6px 0;">🔐 Main Branch Authentication</h4>
                <small style="color:#64748b;">Restricted to Central HQ Adjudicators and Audit Officers.</small>
            </div>
            """, unsafe_allow_html=True)
            
            hq_uid = st.text_input("Main Branch Admin ID", "admin_hq")
            hq_pwd = st.text_input("Secret Password", "hq2026", type="password")
            
            if st.button("🚀 Access Main Branch Workspace", type="primary"):
                if hq_uid.strip() == "admin_hq" and hq_pwd.strip() == "hq2026":
                    st.session_state.hq_authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
            
            with st.expander("🔑 View Main Branch Credentials"):
                st.markdown("* **Admin ID:** `admin_hq` | **Password:** `hq2026`")
        st.stop()

    st.title("🏛️ Main Branch — Executive Dashboard & Adjudication")
    
    with st.sidebar:
        st.divider()
        st.success("🔓 Logged in: `admin_hq`")
        if st.button("🚪 Lock & Sign Out", type="secondary"):
            st.session_state.hq_authenticated = False
            st.rerun()

    # Load Full Datasets
    master_policies_df = bq_client.query(f"""
        SELECT policy_id, policyholder_name, registration_no, bike_model_year, engine_cc, insurance_type, idv_amount, policy_status, created_timestamp 
        FROM `{DATASET_ID}.policies_master` 
        ORDER BY created_timestamp DESC;
    """).to_dataframe()

    claims_df = bq_client.query(f"""
        SELECT c.claim_id, c.sub_branch, c.policy_id, COALESCE(p.policyholder_name, 'Unknown') AS policyholder_name, COALESCE(p.registration_no, 'Unknown') AS registration_no, c.garage_type, c.estimated_amount, c.claim_status, c.created_timestamp
        FROM `{DATASET_ID}.claims_ledger` c
        LEFT JOIN `{DATASET_ID}.policies_master` p ON c.policy_id = p.policy_id
        ORDER BY c.created_timestamp DESC;
    """).to_dataframe()

    total_policies = len(master_policies_df)
    unique_claimed = claims_df['policy_id'].nunique() if not claims_df.empty else 0
    pending_count = len(claims_df[claims_df['claim_status'] == 'PENDING_MAIN_BRANCH_REVIEW']) if not claims_df.empty else 0
    approved_count = len(claims_df[claims_df['claim_status'] == 'SETTLEMENT_APPROVED']) if not claims_df.empty else 0
    rejected_count = len(claims_df[claims_df['claim_status'] == 'REJECTED_CLAIM']) if not claims_df.empty else 0
    approved_payout = claims_df[claims_df['claim_status'] == 'SETTLEMENT_APPROVED']['estimated_amount'].sum() if not claims_df.empty else 0.0

    # EXPANDED 6-KPI EXECUTIVE STRIP
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("📋 Total Policies", f"{total_policies:,}")
    k2.metric("📑 Claim Intimations", f"{unique_claimed:,}")
    k3.metric("⏳ Awaiting Review", f"{pending_count:,}")
    k4.metric("✅ Claims Approved", f"{approved_count:,}")
    k5.metric("❌ Claims Rejected", f"{rejected_count:,}")
    k6.metric("💰 Approved Payout", f"₹{approved_payout:,.0f}")
    
    st.divider()
    
    main_tab1, main_tab2 = st.tabs(["⚖️ Adjudicate Sub Branch Claims", "📊 Executive Analytics & Ledgers"])
    
    with main_tab1:
        st.markdown("### 🔍 Incoming Claim Adjudication Queue")
        pending_claims = claims_df[claims_df['claim_status'] == 'PENDING_MAIN_BRANCH_REVIEW'] if not claims_df.empty else pd.DataFrame()
        if not pending_claims.empty:
            col_a1, col_a2 = st.columns([1, 1], gap="large")
            with col_a1:
                target_cid = st.selectbox("Select Pending Claim to Inspect:", pending_claims['claim_id'].tolist())
                c_item = pending_claims[pending_claims['claim_id'] == target_cid].iloc[0]
                
                risk_flag = "🟢 Standard Risk (Fast-Track)"
                if c_item['estimated_amount'] > 20000:
                    risk_flag = "🔴 High-Value Claim (> ₹20,000)"
                elif c_item['garage_type'] == "NON_NETWORK":
                    risk_flag = "🟡 Non-Network Workshop"
                
                st.markdown(f"""
                <div class="info-card">
                    <b>Claim ID:</b> {c_item['claim_id']}<br>
                    <b>Origin:</b> {c_item['sub_branch']}<br>
                    <b>Customer:</b> {c_item['policyholder_name']}<br>
                    <b>Vehicle:</b> <code>{c_item['registration_no']}</code><br>
                    <b>Workshop:</b> {c_item['garage_type']}<br>
                    <b>Requested Loss:</b> <b style="color:#047857; font-size:16px;">₹{c_item['estimated_amount']:,.2f}</b><br>
                    <b>Risk Assessment:</b> <b>{risk_flag}</b>
                </div>
                """, unsafe_allow_html=True)
                
            with col_a2:
                decision = st.radio("Main Branch Verdict", [
                    "SETTLEMENT_APPROVED", 
                    "REFERRED_TO_INVESTIGATION", 
                    "REJECTED_CLAIM"
                ], format_func=lambda x: {
                    "SETTLEMENT_APPROVED": "✅ Approve Settlement",
                    "REFERRED_TO_INVESTIGATION": "🔍 Flag for Field Investigation",
                    "REJECTED_CLAIM": "❌ Reject Claim"
                }[x])
                
                if st.button("⚖️ Commit Verdict to Lakehouse", type="primary"):
                    bq_client.query(f"UPDATE `{DATASET_ID}.claims_ledger` SET claim_status = '{decision}' WHERE claim_id = '{target_cid}';").result()
                    st.success("Verdict recorded successfully!")
                    time.sleep(1)
                    st.rerun()
        else:
            st.success("🎉 All claims have been adjudicated. No pending claims in queue.")

    with main_tab2:
        # TIME HORIZON TREND ANALYSIS (1 Week, 1 Month, 3 Months, 6 Months, 1 Year)
        st.markdown("### 📈 Time Horizon Portfolio Activity")
        time_horizon = st.radio(
            "Select Analysis Horizon:",
            ["1 Week", "1 Month", "3 Months", "6 Months", "1 Year (Full 1,000 Records)"],
            horizontal=True
        )
        
        # Determine cutoff date
        horizon_days_map = {
            "1 Week": 7,
            "1 Month": 30,
            "3 Months": 90,
            "6 Months": 180,
            "1 Year (Full 1,000 Records)": 365
        }
        days_back = horizon_days_map[time_horizon]
        cutoff_date = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=days_back)
        
        # Convert created_timestamp to datetime
        master_policies_df['ts_clean'] = pd.to_datetime(master_policies_df['created_timestamp'])
        filtered_pol_df = master_policies_df[master_policies_df['ts_clean'] >= cutoff_date]
        
        if not filtered_pol_df.empty:
            filtered_pol_df['date_only'] = filtered_pol_df['ts_clean'].dt.date
            daily_policy_counts = filtered_pol_df.groupby('date_only').size().reset_index(name='New Policies Issued')
            
            fig_trend = px.line(
                daily_policy_counts,
                x='date_only',
                y='New Policies Issued',
                markers=True,
                title=f"Policy Issuance Volume Over Selected Horizon ({time_horizon}) — {len(filtered_pol_df):,} Policies Displayed",
                labels={'date_only': 'Timeline Date', 'New Policies Issued': 'Policies Issued'},
                color_discrete_sequence=['#0284c7']
            )
            fig_trend.update_layout(height=280, margin=dict(t=35, b=10, l=10, r=10))
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No policy records found within this specific timeframe.")
            
        st.divider()
        st.markdown("### 📊 Status & Regional Distribution")
        
        if not claims_df.empty:
            ch_col1, ch_col2 = st.columns(2)
            with ch_col1:
                st.caption("Claims Distribution by Status")
                fig_donut = px.pie(claims_df, names='claim_status', hole=0.45, color_discrete_sequence=['#10b981', '#ef4444', '#f59e0b', '#0284c7'])
                fig_donut.update_layout(height=240, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_donut, use_container_width=True)
                
            with ch_col2:
                st.caption("Claims Volume by Sub Branch (₹)")
                sub_data = claims_df.groupby('sub_branch')['estimated_amount'].sum().reset_index()
                fig_bar = px.bar(sub_data, x='sub_branch', y='estimated_amount', labels={'sub_branch': 'Sub Branch', 'estimated_amount': 'Loss (₹)'}, color='estimated_amount', color_continuous_scale='Blues')
                fig_bar.update_layout(height=240, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_bar, use_container_width=True)
                
        st.divider()
        
        policies_display_df = master_policies_df.drop(columns=['ts_clean', 'date_only'], errors='ignore').rename(columns={
            'policy_id': 'Policy ID',
            'policyholder_name': 'Customer Name',
            'registration_no': 'Bike RC No',
            'bike_model_year': 'Model & Year',
            'engine_cc': 'CC',
            'insurance_type': 'Insurance Plan',
            'idv_amount': 'IDV Amount (₹)',
            'policy_status': 'Status',
            'created_timestamp': 'Created Timestamp'
        })
        
        claims_display_df = claims_df.rename(columns={
            'claim_id': 'Claim ID',
            'sub_branch': 'Sub Branch Origin',
            'policy_id': 'Policy ID',
            'policyholder_name': 'Customer Name',
            'registration_no': 'Bike RC No',
            'garage_type': 'Workshop Type',
            'estimated_amount': 'Loss Amount (₹)',
            'claim_status': 'Claim Status',
            'created_timestamp': 'Filed Timestamp'
        })
        
        st.markdown("### 📑 1. Registered Policies Master Table (1,000 Records)")
        st.dataframe(policies_display_df, use_container_width=True)
        st.write("")
        st.markdown("### 📜 2. All Submitted Claims Ledger (250 Records)")
        st.dataframe(claims_display_df, use_container_width=True)
