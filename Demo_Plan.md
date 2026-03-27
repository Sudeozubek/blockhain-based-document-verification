# Demo Plan: Blockchain-Based Document Integrity Verification System

This document outlines the step-by-step plan for the live project demonstration to showcase all requirements.

## 1. Project Overview & GitHub Repository (2 mins)
- **Goal:** Showcase the codebase, MVP, and documentation.
- **Action:** Open the GitHub repository in the browser.
- **Talking Points:**
  - Briefly introduce the project objective (document integrity using simulated blockchain).
  - Walk through the repository structure outlining Frontend, Backend, tests, and documentation (`README.md`, PDFs).
  - Show the **Sprint Board** to prove Agile/Scrum methodology and task tracking.

## 2. CI/CD Pipeline Demonstration (2 mins)
- **Goal:** Prove the existence of an automated build & test pipeline.
- **Action:** Open the `Actions` tab on GitHub.
- **Talking Points:**
  - Show the `.github/workflows/ci-cd.yml` file.
  - Show a recently successful build (or trigger one manually).
  - Explain that every commit/push automatically runs unit tests (`pytest`) and checks code quality before deployment.

## 3. Live System Demonstration (MVP) (5 mins)
- **Goal:** Demonstrate the working application and core features.
- **Action:** Open the running application at `http://localhost:5001`.
- **Step-by-Step Flow:**
  1. **Upload:** Go to the "Upload" page. Select a clean PDF contract and upload it. Show the resulting Block Index and Hash.
  2. **Verify (Original):** Go to the "Verify" page. Upload the *same* PDF again to show that the system successfully identifies it as **ORIGINAL** and securely stored.
  3. **Verify (Tampered):** Make a tiny invisible change to the PDF, or upload a different PDF with the same expected file name. The system must catch this and show **TAMPERED**, proving the blockchain hash validation works.
  4. **Blockchain Integrity:** Show the "Blockchain Validation" or "History/Dashboard" pages, demonstrating that the entire chain structure is intact and valid.

## 4. Risk Updates & Closing (1 min)
- **Goal:** Discuss risk management in Agile SDLC.
- **Talking Points:** 
  - Briefly touch upon the Risks identified in the project documentation (`Blockchain_Project_HW3.pdf` or `Project_Plan_Final.xlsx`).
  - Summarize how these risks were mitigated during the Sprints.
  - Final Q&A.
