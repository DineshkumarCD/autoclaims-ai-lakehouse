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



## 🏗️ Overall Architecture

<p align="center">
  <img src="images/overall-architecture.png" alt="AutoClaims AI Overall Architecture" width="100%">
</p>
