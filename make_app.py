with open("app.py", "w") as f:
    f.write('''import time
import re
from datetime import date
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

st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 8px; height: 44px; font-weight: 600; }
    .status-badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-active { background-color: #dcfce7; color: #166534; }
    .badge-expired { background-color: #fee2e2; color: #991b1b; }
    .info-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .kpi-title { font-size: 13px; color: #64748b; font-weight: 600; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_bq_client():
    return bigquery.Client()

@st.cache_resource
def get_vision_client():
    return vision.ImageAnnotatorClient()

bq_client = get_bq_client()
vision_client = get_vision_client()

# Sidebar Navigation
st.sidebar.title("🛡️ AutoClaims AI")
st.sidebar.caption("Two-Wheeler Multi-Branch Operations")

branch_role = st.sidebar.radio(
    "Select Operational Desk:",
    ["🏢 Sub Branch (Intake & Filing)", "🏛️ Main Branch (Review & Dashboard)"]
)

st.sidebar.divider()
st.sidebar.info("💡 **Sub Branch** handles onboarding & claim intimation. **Main Branch** reviews, approves settlements, and tracks live policy metrics.")

# =========================================================
# 1. SUB BRANCH WORKSPACE
# =========================================================
if branch_role == "🏢 Sub Branch (Intake & Filing)":
    st.title("🏢 Sub Branch Operations Desk")
    st.caption("Register new policyholders, run AI document checks, and dispatch claims to Main Branch.")
    
    sub_tab1, sub_tab2 = st.tabs(["🚀 File & Dispatch Claim", "➕ Onboard Customer & Issue Policy"])
    
    # SUB TAB 1: FILE CLAIM
    with sub_tab1:
        sub_branch_name = st.selectbox("Submitting Sub Branch:", [
            "Theni Regional Sub Branch",
            "Madurai South Sub Branch",
            "Chennai Central Sub Branch",
            "Coimbatore West Sub Branch"
        ])
        
        pol_query = f"""
        SELECT policy_id, policyholder_name, registration_no, bike_model_year, engine_cc, insurance_type, idv_amount, policy_status 
        FROM `{bq_client.project}.two_wheeler_insurance.policies_master` 
        ORDER BY created_timestamp DESC;
        """
        try:
            pol_df = bq_client.query(pol_query).to_dataframe()
        except Exception:
            pol_df = pd.DataFrame()

        if not pol_df.empty:
            col_l, col_r = st.columns([1, 1], gap="large")
            with col_l:
                st.markdown("#### 1️⃣ Select Customer Policy")
                chosen_pid = st.selectbox(
                    "Policy Number:",
                    options=pol_df['policy_id'].tolist(),
                    format_func=lambda x: f"{x} - {pol_df[pol_df['policy_id']==x]['policyholder_name'].values[0]} ({pol_df[pol_df['policy_id']==x]['registration_no'].values[0]})"
                )
                
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
                        with st.spinner("Analyzing document via Vision AI..."):
                            img_data = up_rc.getvalue()
                            v_img = vision.Image(content=img_data)
                            v_resp = vision_client.text_detection(image=v_img)
                            full_txt = v_resp.text_annotations[0].description if v_resp.text_annotations else ""
                            
                            patterns = [
                                r'[A-Z]{2}[-\s]?[0-9]{1,2}[-\s]?[A-Z]{1,3}[-\s]?[0-9]{4}',
                                r'[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}',
                                r'TN[0-9]{2}[A-Z]{1,2}[0-9]{4}'
                            ]
                            clean_str = " ".join(full_txt.split()).upper()
                            detected_plate = "NOT_SCANNED"
                            for pat in patterns:
                                m = re.search(pat, clean_str)
                                if m:
                                    detected_plate = m.group(0).replace(" ", "").replace("-", "")
                                    break
                            
                            target_plate = str(sel_pol['registration_no']).replace("-", "").replace(" ", "").upper()
                            if detected_plate != "NOT_SCANNED" and (detected_plate in target_plate or target_plate in detected_plate):
                                st.success(f"✅ Extracted Plate: **{detected_plate}** (Matches Policy Master)")
                            else:
                                st.warning(f"⚠️ Extracted: **{detected_plate}** (Please verify manually)")

            with col_r:
                st.markdown("#### 3️⃣ Repair Estimatics & Intimation")
                loc_txt = st.text_input("Accident Location", f"{sub_branch_name.split()[0]} Main Road")
                g_type = st.radio("Garage Category", ["NETWORK (Cashless)", "NON_NETWORK (Reimbursement)"], horizontal=True)
                g_name = st.text_input("Workshop Name", "City Speed Auto Service")
                
                c_p1, c_p2 = st.columns(2)
                with c_p1:
                    m_cost = st.number_input("Metal / Frame Parts (₹)", value=6000, step=500)
                    p_cost = st.number_input("Plastic Parts (50% Dep.) (₹)", value=4000, step=500)
                with c_p2:
                    l_cost = st.number_input("Labour & Painting (₹)", value=2500, step=500)
                    deductible = 1000
                
                settlement_est = max(0.0, (m_cost * 0.90) + (p_cost * 0.50) + l_cost - deductible)
                
                st.markdown(f"""
                <div class="info-card" style="background:#ecfdf5; border-color:#a7f3d0; margin-top:8px;">
                    <span class="kpi-title" style="color:#065f46;">Calculated Net Claim Payout</span>
                    <h2 style="color:#047857; margin:4px 0;">₹{settlement_est:,.2f}</h2>
                    <small style="color:#047857;">Factoring standard 50% plastic depreciation & ₹1,000 policy deductible.</small>
                </div>
                """, unsafe_allow_html=True)
                
                notes = st.text_area("Sub Branch Surveyor Remarks", "Survey completed. Damages verified against customer intimation.")
                
                if st.button("🚀 Dispatch Claim to Main Branch", type="primary"):
                    new_claim_id = f"CLM-{int(time.time()) % 10000}"
                    clean_g = "NETWORK" if "NETWORK" in g_type and "NON" not in g_type else "NON_NETWORK"
                    
                    insert_claim_sql = f"""
                    INSERT INTO `{bq_client.project}.two_wheeler_insurance.claims_ledger`
                    (claim_id, policy_id, sub_branch, incident_location, incident_description, garage_type, garage_name, estimated_amount, claim_status, created_timestamp)
                    VALUES (@claim_id, @policy_id, @sub_branch, @incident_location, @incident_description, @garage_type, @garage_name, @estimated_amount, 'PENDING_MAIN_BRANCH_REVIEW', CURRENT_TIMESTAMP());
                    """
                    job_cfg = bigquery.QueryJobConfig(
                        query_parameters=[
                            bigquery.ScalarQueryParameter("claim_id", "STRING", new_claim_id),
                            bigquery.ScalarQueryParameter("policy_id", "STRING", str(chosen_pid)),
                            bigquery.ScalarQueryParameter("sub_branch", "STRING", sub_branch_name),
                            bigquery.ScalarQueryParameter("incident_location", "STRING", str(loc_txt or "Sub Branch Area")),
                            bigquery.ScalarQueryParameter("incident_description", "STRING", str(notes or "Survey verified")),
                            bigquery.ScalarQueryParameter("garage_type", "STRING", clean_g),
                            bigquery.ScalarQueryParameter("garage_name", "STRING", str(g_name or "Authorized Garage")),
                            bigquery.ScalarQueryParameter("estimated_amount", "NUMERIC", float(settlement_est))
                        ]
                    )
                    bq_client.query(insert_claim_sql, job_config=job_cfg).result()
                    st.balloons()
                    st.success(f"🎉 Claim **#{new_claim_id}** dispatched to **Main Branch** for review!")
        else:
            st.info("No policy records found. Please issue a policy first.")

    # SUB TAB 2: ONBOARD CUSTOMER
    with sub_tab2:
        st.markdown("#### ➕ New Customer Policy Registration")
        st.caption("Add customer name, bike RC number, Aadhaar reference, bike model & year, and insurance plan.")
        
        in_col1, in_col2 = st.columns(2, gap="large")
        with in_col1:
            cust_name = st.text_input("Customer Name", placeholder="e.g. Ramesh Kumar")
            rc_no = st.text_input("Bike RC Number", placeholder="e.g. TN-57-AZ-1122")
            aadhaar_ref = st.text_input("Aadhaar Number", placeholder="12-Digit Identification Number", type="password")
            
        with in_col2:
            bike_model_yr = st.text_input("Bike Model & Year", placeholder="e.g. TVS Apache RTR 160 (2024)")
            bike_cc = st.number_input("Engine Capacity (CC)", value=150, min_value=50, max_value=1200, step=10)
            ins_type = st.selectbox("Insurance Type", ["Comprehensive", "Full Coverage (Zero Dep)"])
            idv_val = st.number_input("Insured Declared Value (IDV in ₹)", value=125000, step=5000)
            
        st.divider()
        if st.button("📋 Issue & Activate Policy", type="primary"):
            final_name = cust_name.strip() if cust_name.strip() else "New Policyholder"
            final_rc = rc_no.strip().upper() if rc_no.strip() else f"TN-57-TMP-{int(time.time())%1000}"
            final_model = bike_model_yr.strip() if bike_model_yr.strip() else "Standard Two-Wheeler"
            masked_id = "[Aadhaar Redacted]"
            new_pid = f"POL-TN-{int(time.time()) % 10000}"
            
            insert_pol_sql = f"""
            INSERT INTO `{bq_client.project}.two_wheeler_insurance.policies_master`
            (policy_id, policyholder_name, registration_no, id_reference, bike_model_year, engine_cc, insurance_type, idv_amount, policy_status, created_timestamp)
            VALUES (@policy_id, @policyholder_name, @registration_no, @id_reference, @bike_model_year, @engine_cc, @insurance_type, @idv_amount, 'ACTIVE', CURRENT_TIMESTAMP());
            """
            job_cfg = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("policy_id", "STRING", new_pid),
                    bigquery.ScalarQueryParameter("policyholder_name", "STRING", final_name),
                    bigquery.ScalarQueryParameter("registration_no", "STRING", final_rc),
                    bigquery.ScalarQueryParameter("id_reference", "STRING", masked_id),
                    bigquery.ScalarQueryParameter("bike_model_year", "STRING", final_model),
                    bigquery.ScalarQueryParameter("engine_cc", "INT64", int(bike_cc)),
                    bigquery.ScalarQueryParameter("insurance_type", "STRING", str(ins_type)),
                    bigquery.ScalarQueryParameter("idv_amount", "NUMERIC", float(idv_val))
                ]
            )
            try:
                bq_client.query(insert_pol_sql, job_config=job_cfg).result()
                st.balloons()
                st.success(f"🎉 New Policy **{new_pid}** successfully activated for **{final_name}** ({final_rc})!")
                st.info("The policy is live and ready for claims in the 'File & Dispatch Claim' tab.")
            except Exception as e:
                st.error(f"Error creating policy: {e}")

# =========================================================
# 2. MAIN BRANCH WORKSPACE
# =========================================================
elif branch_role == "🏛️ Main Branch (Review & Dashboard)":
    st.title("🏛️ Main Branch — Executive Dashboard & Adjudication")
    st.caption("Central review of sub branch claims and live portfolio intelligence.")
    
    # 1. Fetch All Policies
    all_policies_sql = f"""
    SELECT 
        policy_id AS `Policy ID`,
        policyholder_name AS `Customer Name`,
        registration_no AS `Bike RC No`,
        bike_model_year AS `Model & Year`,
        engine_cc AS `CC`,
        insurance_type AS `Insurance Plan`,
        idv_amount AS `IDV (₹)`,
        policy_status AS `Status`
    FROM `{bq_client.project}.two_wheeler_insurance.policies_master`
    ORDER BY created_timestamp DESC;
    """
    try:
        master_policies_df = bq_client.query(all_policies_sql).to_dataframe()
    except Exception:
        master_policies_df = pd.DataFrame()

    # 2. Fetch All Claims
    claims_sql = f"""
    SELECT 
        c.claim_id AS `Claim ID`,
        c.sub_branch AS `Sub Branch Origin`,
        c.policy_id AS `Policy ID`,
        p.policyholder_name AS `Customer Name`,
        p.registration_no AS `Bike RC No`,
        c.garage_type AS `Workshop Type`,
        c.estimated_amount AS `Loss Amount (₹)`,
        c.claim_status AS `Claim Status`,
        c.created_timestamp AS `Filed Timestamp`
    FROM `{bq_client.project}.two_wheeler_insurance.claims_ledger` c
    JOIN `{bq_client.project}.two_wheeler_insurance.policies_master` p ON c.policy_id = p.policy_id
    ORDER BY c.created_timestamp DESC;
    """
    try:
        claims_df = bq_client.query(claims_sql).to_dataframe()
    except Exception:
        claims_df = pd.DataFrame()

    # Core Metrics
    total_policies_count = len(master_policies_df)
    unique_policies_claimed = claims_df['Policy ID'].nunique() if not claims_df.empty else 0
    pending_count = len(claims_df[claims_df['Claim Status'] == 'PENDING_MAIN_BRANCH_REVIEW']) if not claims_df.empty else 0
    total_approved_payout = claims_df[claims_df['Claim Status'] == 'SETTLEMENT_APPROVED']['Loss Amount (₹)'].sum() if not claims_df.empty else 0.0

    # TOP KPI CARDS
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📋 Total Policies Registered", f"{total_policies_count}")
    k2.metric("📑 Policies with Claims", f"{unique_policies_claimed}")
    k3.metric("⏳ Awaiting Main Review", f"{pending_count}")
    k4.metric("💰 Total Approved Payout", f"₹{total_approved_payout:,.0f}")
    
    st.divider()
    
    main_tab1, main_tab2 = st.tabs(["⚖️ Adjudicate Sub Branch Claims", "📊 Executive Analytics & Ledgers"])
    
    # MAIN TAB 1: ADJUDICATION QUEUE
    with main_tab1:
        st.markdown("### 🔍 Incoming Claim Adjudication Queue")
        pending_claims = claims_df[claims_df['Claim Status'] == 'PENDING_MAIN_BRANCH_REVIEW'] if not claims_df.empty else pd.DataFrame()
        
        if not pending_claims.empty:
            col_adj1, col_adj2 = st.columns([1, 1], gap="large")
            with col_adj1:
                target_cid = st.selectbox("Select Pending Claim to Inspect:", pending_claims['Claim ID'].tolist())
                c_item = pending_claims[pending_claims['Claim ID'] == target_cid].iloc[0]
                
                risk_flag = "🟢 Standard Risk (Fast-Track Eligible)"
                if c_item['Loss Amount (₹)'] > 20000:
                    risk_flag = "🔴 High-Value Claim (> ₹20,000)"
                elif c_item['Workshop Type'] == "NON_NETWORK":
                    risk_flag = "🟡 Non-Network Workshop Claim"
                
                st.markdown(f"""
                <div class="info-card">
                    <b>Claim ID:</b> {c_item['Claim ID']}<br>
                    <b>Originating Unit:</b> {c_item['Sub Branch Origin']}<br>
                    <b>Customer:</b> {c_item['Customer Name']}<br>
                    <b>Vehicle:</b> <code>{c_item['Bike RC No']}</code><br>
                    <b>Garage Category:</b> {c_item['Workshop Type']}<br>
                    <b>Estimated Loss:</b> <b style="color:#047857; font-size:16px;">₹{c_item['Loss Amount (₹)']:,.2f}</b><br>
                    <b>Risk Assessment:</b> <b>{risk_flag}</b>
                </div>
                """, unsafe_allow_html=True)
                
            with col_adj2:
                decision = st.radio("Main Branch Verdict", [
                    "SETTLEMENT_APPROVED", 
                    "REFERRED_TO_INVESTIGATION", 
                    "REJECTED_CLAIM"
                ], format_func=lambda x: {
                    "SETTLEMENT_APPROVED": "✅ Approve Settlement",
                    "REFERRED_TO_INVESTIGATION": "🔍 Flag for Field Investigation",
                    "REJECTED_CLAIM": "❌ Reject Claim"
                }[x])
                
                verdict_notes = st.text_input("Main Branch Adjudication Remarks", "Damage and coverage terms verified. Settlement approved.")
                
                if st.button("⚖️ Commit Final Verdict to Lakehouse", type="primary"):
                    upd_sql = f"""
                    UPDATE `{bq_client.project}.two_wheeler_insurance.claims_ledger`
                    SET claim_status = @claim_status
                    WHERE claim_id = @claim_id;
                    """
                    job_cfg = bigquery.QueryJobConfig(
                        query_parameters=[
                            bigquery.ScalarQueryParameter("claim_status", "STRING", decision),
                            bigquery.ScalarQueryParameter("claim_id", "STRING", target_cid)
                        ]
                    )
                    bq_client.query(upd_sql, job_config=job_cfg).result()
                    st.success(f"Claim **{target_cid}** updated to **{decision}**!")
                    time.sleep(1)
                    st.rerun()
        else:
            st.success("🎉 All Sub Branch claims have been processed! No pending claims in the queue.")

    # MAIN TAB 2: EXECUTIVE ANALYTICS & 2 DEDICATED TABLES
    with main_tab2:
        st.markdown("### 📊 Portfolio Charts & Visual Distribution")
        
        if not claims_df.empty:
            ch_col1, ch_col2 = st.columns(2)
            with ch_col1:
                st.caption("Claims Distribution by Status")
                fig_donut = px.pie(
                    claims_df, 
                    names='Claim Status', 
                    hole=0.45,
                    color_discrete_sequence=['#f59e0b', '#10b981', '#ef4444', '#0284c7']
                )
                fig_donut.update_layout(height=240, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_donut, use_container_width=True)
                
            with ch_col2:
                st.caption("Claims Volume by Sub Branch (₹)")
                sub_data = claims_df.groupby('Sub Branch Origin')['Loss Amount (₹)'].sum().reset_index()
                fig_bar = px.bar(
                    sub_data, x='Sub Branch Origin', y='Loss Amount (₹)',
                    labels={'Sub Branch Origin': 'Sub Branch', 'Loss Amount (₹)': 'Loss (₹)'},
                    color='Loss Amount (₹)', color_continuous_scale='Blues'
                )
                fig_bar.update_layout(height=240, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_bar, use_container_width=True)
                
        st.divider()
        
        # TABLE 1: ALL REGISTERED POLICIES
        st.markdown("### 📑 1. Registered Policies Master Table")
        st.caption("Complete database of all active and historical policies issued across sub branches.")
        if not master_policies_df.empty:
            st.dataframe(master_policies_df, use_container_width=True)
        else:
            st.info("No policy records registered in Lakehouse yet.")
            
        st.write("")
        
        # TABLE 2: ALL CLAIMS LEDGER
        st.markdown("### 📜 2. All Submitted Claims Ledger")
        st.caption("Live lifecycle ledger of all claims intimations, review statuses, and payouts.")
        if not claims_df.empty:
            st.dataframe(claims_df, use_container_width=True)
        else:
            st.info("No claims filed in Lakehouse yet.")
''')
print("app.py updated with dual data tables!")
