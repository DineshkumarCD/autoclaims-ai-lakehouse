# 🚗 AutoClaims AI

> ### ☁️ Serverless Insurance Data Lakehouse & Ingestion Pipeline
>
> **“Transforming manual, fragmented motor insurance claims into an automated, zero-disk, intelligent data lakehouse ecosystem.”**

---

## 📌 Project Overview

**AutoClaims AI** is a **cloud-native insurance data lakehouse and adjudication platform** built on **Google Cloud Platform (GCP)**.

The platform automates the **end-to-end motor insurance claim lifecycle** — from capturing field-level documents at regional sub-branches to centralized data synchronization, analytics, and claim adjudication at corporate headquarters.

### 🔄 End-to-End Claim Lifecycle

```text
📄 Field Document Capture
        │
        ▼
🧠 In-Memory OCR Extraction
        │
        ▼
⚡ Automated Data Processing
        │
        ▼
☁️ Centralized BigQuery Lakehouse
        │
        ▼
📊 Loss Ratio Analytics
        │
        ▼
🏢 Corporate Adjudication
```

## 🎯 Key Objective

AutoClaims AI is designed to replace **manual, fragmented, and disk-dependent claim-processing workflows** with a:

* ☁️ **Cloud-native** architecture
* ⚡ **Automated** ingestion and processing pipeline
* 💾 **Zero-disk** document-processing approach
* 🧠 **Intelligent OCR-driven** data extraction
* 🏗️ **Centralized BigQuery lakehouse** architecture
* 📊 **Automated insurance analytics**
* 🔐 **Scalable and enterprise-ready** data platform

## 🏢 Business Flow

The platform connects **regional insurance sub-branches** with **corporate headquarters**, creating a unified data ecosystem for motor insurance claims.

```text
👨‍💼 Field / Sub-Branch
        │
        │ 📸 Claim Documents
        ▼
🧠 OCR & Data Extraction
        │
        │ ⚡ In-Memory Processing
        ▼
☁️ GCP Data Ingestion Layer
        │
        ▼
🏞️ BigQuery Data Lakehouse
        │
        ├── 📈 Loss Ratio Analytics
        ├── 🔍 Claim Analysis
        └── ⚖️ Automated Adjudication
        │
        ▼
🏢 Corporate Headquarters
```

### 💡 Core Vision

> **Capture once → Process in memory → Ingest automatically → Analyze centrally → Adjudicate intelligently.**

AutoClaims AI establishes a **single, automated data foundation** for motor insurance operations while reducing manual intervention, eliminating unnecessary disk-based processing, and enabling near-real-time analytical decision-making.


## 🏗️ Overall Architecture

<p align="center">
  <img src="images/overall-architecture.png" alt="AutoClaims AI Overall Architecture" width="100%">
</p>


# 🎯 Business Problem & Solution Scope

## 🚧 The Operational Bottlenecks

Traditional motor insurance claim processing often involves **manual data entry, disconnected systems, and locally stored sensitive documents**. These limitations create operational delays, data-quality issues, and security risks.

### 📝 1. Manual Document Entry

Regional branch officers manually enter **Vehicle Registration Certificate (RC)** details into operational systems.

This introduces:

* ❌ **Transcription errors**
* ⏳ **Processing latency**
* 👤 **High dependency on manual intervention**
* 🔁 **Repetitive data-entry workflows**

---

### 🗂️ 2. Fragmented Data Silos

Policy transactions, claims information, and executive reporting frequently exist across **disconnected data sources**.

```text
🗄️ Policy Database
       │
       │ ❌ Disconnected
       ▼
📊 Claims Spreadsheets
       │
       │ ❌ Manual Reconciliation
       ▼
📈 Executive Reporting Mart
```

This fragmentation makes it difficult to establish a **single, consistent view of insurance operations** and increases the effort required for reconciliation and reporting.

---

### 🔐 3. Compliance & Security Vulnerabilities

Scanned **identity documents and vehicle RC documents** stored on local disks create additional security and compliance exposure.

Potential risks include:

* 💾 Persistent local file storage
* 🔓 Unauthorized access to sensitive documents
* 🗃️ Uncontrolled document copies
* ⚠️ Increased data-privacy compliance exposure

---

# ⚙️ Engineering Solution

AutoClaims AI addresses these operational challenges through a **serverless, zero-disk, cloud-native architecture**.

## 💨 1. Zero-Disk Document Extraction

Raw RC smart-card uploads are processed through **volatile RAM buffers** before being submitted to **Google Cloud Vision API** for OCR extraction.

```text
📄 RC Smart Card
      │
      ▼
⚡ RAM Buffer
      │
      ▼
🧠 Google Cloud Vision API
      │
      ▼
🔤 Extracted Structured Data
      │
      ▼
☁️ Cloud Data Layer
```

The workflow avoids persistent local file caching during document processing, supporting a **zero-disk ingestion model** for sensitive claim documents.

---

## ☁️ 2. Serverless Analytical Core

The centralized analytical foundation is built on **Google Cloud BigQuery**.

The platform uses a normalized dual-ledger model consisting of:

| Dataset / Table   | Primary Purpose                                |
| ----------------- | ---------------------------------------------- |
| `policies_master` | Centralized policy and vehicle information     |
| `claims_ledger`   | Centralized motor insurance claim transactions |

This provides a unified analytical foundation for **claim processing, reconciliation, reporting, and loss-ratio analysis**.

---

## 👥 3. Dual-Tier Role Routing

AutoClaims AI separates operational responsibilities into two distinct application workflows while maintaining a unified deployment architecture.

```text
                    ☁️ Cloud Run
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
     🏢 Sub-Branch Desk      🏛️ Main HQ Console
             │                     │
             ▼                     ▼
    👨‍💼 Field Claim Officer    👨‍💼 Claims Adjuster
             │                     │
             ▼                     ▼
      📄 Claim Intake        ⚖️ Adjudication
```

### 🏢 Sub-Branch Desk

Designed for **field claim officers** to:

* 📸 Capture RC and claim documents
* 🧠 Extract information using OCR
* 📝 Initiate claim records
* ⚡ Submit structured claim data

### 🏛️ Main HQ Console

Designed for **claims adjusters** to:

* 🔍 Review centralized claims
* 📊 Analyze claim information
* ⚖️ Perform adjudication workflows
* 📈 Access centralized analytical insights

---

## 🏆 Engineering Outcome

The solution transforms a fragmented, manual workflow into a **centralized and automated insurance data platform**:

```text
Manual Entry       → 🧠 Automated OCR
Local Files        → ⚡ Zero-Disk Processing
Data Silos         → ☁️ Centralized BigQuery
Disconnected Roles → 👥 Dual-Tier Role Routing
Manual Analytics   → 📊 Automated Insights
```

> **AutoClaims AI converts operational complexity into a scalable, secure, and analytics-ready cloud architecture.**

# 🏗️ End-to-End System Architecture

> The **AutoClaims AI** platform is structured as a **three-tier, cloud-native data lakehouse architecture** designed to process motor insurance claims from regional branch ingestion through centralized enterprise analytics — while minimizing manual processing latency and eliminating persistent local document storage.

---

## 🔄 Architecture Overview

<p align="center">
  <img 
    src="images/operational_ingestion_tier.png" 
    alt="AutoClaims AI Overall Architecture"
    width="100%"
  >
</p>


---

# 1️⃣ Operational Ingestion Tier

### 🏪 Sub-Branch Operations

Field agents handle customer-facing insurance transactions at regional branches.

Key responsibilities include:

* 📝 **Motor Policy Underwriting & Issuance**
* 💰 **Insured Declared Value (IDV) Calculation**
* 🚗 **Motor Damage Claim Registration**
* 📄 **Vehicle RC Smart Card Upload**
* 🧠 **Zero-Disk OCR Processing Initiation**

The Sub-Branch Desk acts as the primary **operational entry point** for policy and claim information.

### 🏛️ Main HQ Operations

Headquarters claim adjusters operate through a secured adjudication workspace:

```text
`admin_hq`
```

The HQ workspace enables adjusters to:

* 🔍 Review itemized workshop repair estimates
* 📉 Apply depreciation adjustments
* ♻️ Apply salvage deductions
* 💰 Review settlement amounts
* ✅ Approve claim payouts
* ❌ Reject claims where applicable

### 🔐 Network & Security Boundary

All user interactions and application payloads pass through:

**HTTPS → TLS Termination → Cloud Application**

This provides encrypted communication while protecting sensitive policyholder and claim information **in transit**.

---

# 2️⃣ Compute & OCR Processing Layer

## ☁️ Google Cloud Run

The core application is packaged inside a **multi-stage Docker container** and deployed on **Google Cloud Run**.

Cloud Run provides:

* ⚡ Request-based autoscaling
* 📈 Automatic capacity management
* 💤 Scale-to-zero when idle
* 💰 Reduced idle infrastructure costs
* 🐳 Containerized application execution

```text
User Request
     │
     ▼
☁️ Cloud Run
     │
     ├── 🖥️ Streamlit Application
     ├── 📊 Plotly Analytics
     └── 🧠 OCR Processing
```

---

## 🖥️ Streamlit Core Engine

The **Streamlit Engine** provides the application interface for branch and headquarters users.

It manages:

* 🧭 Role-based navigation
* 📝 Policy forms
* 📄 Claim registration
* 📤 RC document uploads
* 👥 Branch/HQ workflows
* 🔄 Application state

---

## 📊 Plotly Analytics Mart

The integrated **Plotly Analytics Mart** provides real-time portfolio visualizations.

Example analytical metric:

> **📈 Incurred Loss Ratio**

These visualizations allow HQ users to monitor portfolio-level claim exposure and loss performance.

---

## 🧠 Zero-Disk OCR Pipeline

One of the key engineering features of AutoClaims AI is its **zero-disk document-processing architecture**.

RC smart-card documents are processed directly from **volatile memory** using:

```python
io.BytesIO
```

The document lifecycle is:

```text
📄 RC Smart Card
       │
       ▼
⚡ RAM Buffer
       │
       ▼
🧠 Google Cloud Vision API
       │
       ▼
🔤 Raw OCR Text
       │
       ▼
🔎 Regex Parsing
       │
       ├── 🚗 Registration Number
       ├── ⚙️ Engine Number
       ├── 🔩 Chassis Number
       └── 🚙 Vehicle Class
```

### 🛡️ Zero-Disk Principle

The uploaded RC document is **not intentionally persisted to local disk** during the OCR workflow.

Instead:

```text
Upload → RAM → Vision API → OCR Text → Structured Data
```

This minimizes persistent exposure of sensitive vehicle and identity documentation.

---

# 3️⃣ Data Lakehouse Storage Layer

## ☁️ Google Cloud BigQuery

The centralized analytical core is built on **Google Cloud BigQuery**.

The project uses the:

```text
autoclaims_lakehouse
```

dataset as the centralized storage and analytical foundation.

---

## 🔐 IAM-Authenticated Data Access

The compute layer communicates with BigQuery through **IAM-authenticated service accounts**.

```text
☁️ Cloud Run
      │
      │ 🔐 IAM Authentication
      ▼
☁️ BigQuery
      │
      ├── SQL DDL
      └── SQL DML
```

This architecture avoids embedding traditional database passwords or hardcoded credentials inside the application.

---

## 📋 `policies_master` Entity

`policies_master` functions as the primary **policy dimension table**.

It tracks:

| Attribute             | Purpose                                   |
| --------------------- | ----------------------------------------- |
| `policy_id`           | Unique policy identifier                  |
| Customer details      | Policyholder information                  |
| Vehicle parameters    | Vehicle identification and classification |
| IDV valuation         | Insured Declared Value                    |
| Gross Written Premium | Premium information                       |
| Policy lifecycle      | Policy status and timestamps              |

---

## 📑 `claims_ledger` Entity

`claims_ledger` functions as the central **transactional claim fact table**.

It captures:

| Attribute               | Purpose                          |
| ----------------------- | -------------------------------- |
| `claim_id`              | Unique claim identifier          |
| `policy_id`             | Associated policy reference      |
| `branch_id`             | Regional claim origin            |
| Workshop classification | Cashless Network / Reimbursement |
| Repair estimate         | Estimated repair cost            |
| Approved settlement     | Final approved payout            |

---

## 🔗 Relational Lakehouse Synchronization

The two core entities are logically connected through:

```text
policies_master
       │
       │ policy_id
       │
       ▼
claims_ledger
```

This relationship enables centralized:

* 🔍 **Claim history lookups**
* 📊 **Loss ratio aggregation**
* 💰 **Settlement analysis**
* 📈 **Portfolio analytics**
* ⚖️ **Adjudication workflows**

---

# 🚀 End-to-End Data Journey

The complete AutoClaims AI workflow can be summarized as:

```text
📄 Customer / Vehicle Document
              │
              ▼
🏪 Sub-Branch Desk
              │
              ▼
🔐 HTTPS / TLS
              │
              ▼
☁️ Google Cloud Run
              │
       ┌──────┴──────┐
       ▼             ▼
🖥️ Streamlit     📊 Plotly
       │
       ▼
⚡ RAM / io.BytesIO
       │
       ▼
🧠 Google Cloud Vision
       │
       ▼
🔎 Regex Extraction
       │
       ▼
🔐 IAM Authentication
       │
       ▼
☁️ Google BigQuery
       │
       ├── 📋 policies_master
       │
       └── 📑 claims_ledger
              │
              ▼
📈 Loss Ratio Analytics
              │
              ▼
🏛️ Main HQ Adjudication
              │
              ▼
✅ Approve / ❌ Reject
```

> ### 💡 Architecture Principle
> **Capture → Process in Memory → Extract → Ingest → Analyze → Adjudicate**
>
> AutoClaims AI brings these stages together into a **serverless, zero-disk, cloud-native insurance data lakehouse ecosystem**.

## 🔬 Module-by-Module Technical Deep Dive

### 1️⃣ Module 1: Data Modeling & Lakehouse Core

> **Technology:** ☁️ Google Cloud BigQuery
> **Dataset:** `autoclaims_lakehouse`

The **Data Modeling & Lakehouse Core** serves as the centralized data foundation of AutoClaims AI. It separates relatively stable policy information from transactional claim events, enabling reliable claim processing, analytics, and loss-ratio calculations.

---

### 📋 `policies_master` — Policy Entity

The **`policies_master`** table acts as the primary policy entity within the lakehouse.

It stores:

* 🆔 `policy_id`
* 👤 Customer demographics
* 🚗 Vehicle parameters
* 💰 Insured Declared Value (IDV)
* 💵 Annual gross premium
* 📅 Policy validity and lifecycle status

---

### 📑 `claims_ledger` — Claims Transaction Entity

The **`claims_ledger`** acts as the central transactional entity for motor insurance claims.

It tracks the complete claim lifecycle:

```text
📝 Submitted
      │
      ▼
🔍 Under Review
      │
      ├───────────────┐
      ▼               ▼
  ✅ Approved       ❌ Rejected
      │
      ▼
💰 Settlement
```

It captures:

* 🆔 `claim_id`
* 🔗 `policy_id`
* 📍 Regional branch origin
* 🏭 Workshop classification
* 🔧 Itemized repair estimates
* 💰 Approved settlement amount
* 📊 Claim status

---

### 🔗 Policy-to-Claim Relationship

The two core entities are connected through `policy_id`:

```text
policies_master.policy_id
          │
          │ 1 : N
          ▼
claims_ledger.policy_id
```

This relationship enables:

* 🔍 Policy-level claim history
* 📊 Loss-ratio calculations
* 💰 Premium vs. claim-cost analysis
* 📍 Branch-level analytics
* ⚖️ Centralized adjudication

---

### 🌱 Synthetic Seeding Pipeline

A **deterministic Python seeder** was developed to populate the BigQuery lakehouse with a consistent baseline dataset for development, testing, and demonstration.

| Entity      | Initial Records |
| ----------- | --------------: |
| 📋 Policies |       **1,000** |
| 📑 Claims   |         **250** |

The records are distributed across three regional branch codes:

```text
📍 BR-CHENNAI-01
📍 BR-COIMBATORE-02
📍 BR-MADURAI-03
```

### ⚙️ Seeding Flow

```text
🐍 Python Seeder
       │
       ▼
🎲 Deterministic Synthetic Data
       │
       ├───────────────┐
       ▼               ▼
📋 1,000 Policies   📑 250 Claims
       │               │
       └───────┬───────┘
               ▼
        ☁️ BigQuery
               │
               ▼
    `autoclaims_lakehouse`
```

### 🎯 Why Deterministic Seeding?

Deterministic data generation provides a **reproducible development environment**, making it easier to:

* 🧪 Perform repeatable testing
* 🔄 Rebuild the baseline dataset
* 📊 Validate analytical queries
* 🐛 Reproduce and debug issues
* 🚀 Demonstrate the platform consistently

**Module 1 establishes the centralized data foundation on which the remaining AutoClaims AI modules operate.**

<p align="center">
  <img 
    src="images/Module_1.png" 
    alt="AutoClaims AI Overall Architecture"
    width="100%"
  >
</p>





