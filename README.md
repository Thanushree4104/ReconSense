# ReconSense

> AI-powered financial reconciliation and investigation platform for payment operations.

ReconSense is a production-oriented AI system designed to help payment and finance teams detect, investigate, and resolve reconciliation issues across payment transactions and settlement records.

The system combines deterministic financial rules with an AI investigation agent to identify discrepancies, gather supporting evidence, explain likely causes, and recommend bounded next actions.

---

## Problem

Payment operations generate large volumes of transactions across multiple systems.

Discrepancies can occur because of:

- Missing or delayed settlements
- Amount mismatches
- Duplicate transactions
- Partial or split settlements
- Refund-related differences
- Failed or reversed payments
- Timing differences between transaction and settlement records

Investigating these issues manually requires analysts to compare records across systems, identify the discrepancy, collect evidence, determine the likely cause, and decide what action should be taken.

ReconSense aims to reduce this investigation effort while keeping financial decisions explainable, auditable, and controlled.

---

## Proposed Solution

ReconSense provides an AI-assisted reconciliation and investigation workflow:

```text
Payment / Settlement Data
          |
          v
   Data Normalization
          |
          v
 Deterministic Reconciliation
          |
          v
   Discrepancy Detection
          |
          v
    Evidence Collection
          |
          v
   AI Investigation Agent
          |
          v
 Cause + Confidence + Evidence
          |
          v
    Bounded Recommendation
          |
          v
     Policy & Risk Check
          |
          v
 Human Approval / Permitted Action
          |
          v
       Audit Trail'''