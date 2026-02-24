# UniC – University Policy Assistant

UniC is a policy-focused academic assistant designed to provide clear, structured guidance based exclusively on official Arden University regulations and procedures.

The system combines document-based retrieval with a locally hosted large language model to answer student queries while avoiding speculation, opinion-based responses, or non-policy advice.

---

## Key Features

- Answers questions using **official university policy documents only**
- Prevents out-of-scope, subjective, or non-university-related responses
- Safety-aware handling of sensitive or prohibited topics
- Structured answers with confidence indication
- Transparent fallback responses when no policy applies
- Web-based interface built using Flask

---

## How It Works (High Level)

1. The user submits a question via the web interface  
2. The system determines whether the question is within university scope  
3. Dangerous or prohibited topics are intercepted and handled safely  
4. Relevant policy text is retrieved from official documents  
5. Irrelevant or unrelated policy content is filtered out  
6. A response is generated strictly from retrieved policy evidence  
7. A confidence level and clear explanation are presented to the user  

This design prioritises accuracy, transparency, and avoidance of hallucinated answers.

---

## Policy Coverage

UniC provides answers strictly based on official Arden University policy documents.

Included Tier-1 policies:

- Arden Regulatory Framework
- Academic Integrity and Misconduct Policy
- Attendance and Engagement Policy
- Student Complaints Procedure
- Safeguarding and Prevent Policy
- Fitness to Study Policy
- Disability and Reasonable Adjustments Policy
- Withdrawal Policy
- Academic Appeals Process
- Extenuating Circumstances Policy

All documents are sourced from publicly available Arden University publications
and processed into structured text for retrieval-augmented generation (RAG).

## Policy Documents and Data Handling

This repository does **not** include raw policy PDF files.

Official Arden University policy documents are treated as **external source data**
and are intentionally excluded from version control for the following reasons:

- copyright and redistribution restrictions  
- academic data governance best practice  
- separation of code and institutional content  

### Using Policy Documents Locally

To run the ingestion and retrieval pipeline:

1. Create a folder named `raw_policies/` in the project root
2. Place official Arden University policy PDFs inside this folder
3. Run the document extraction and chunking scripts
4. Start the Flask application as normal

The system processes policy documents into structured text and uses
retrieval-augmented generation (RAG) to ensure responses are grounded
strictly in official policy content.

---

## Model and Architecture

- **Language Model:** LLaMA 3 (8 billion parameters)
- **Inference:** Local, CPU-based inference
- **Retrieval:** Keyword- and intent-filtered document search (RAG)
- **Prompting:** Policy-constrained responses with explicit safety fallbacks

A smaller model was deliberately selected to match realistic on-premise university hardware constraints while maintaining acceptable performance and reliability.

---

## System & Environment

The UniC application is deployed on a Linux-based server using a stable Long-Term Support (LTS) environment.

- **Operating System:** Ubuntu 24.04 LTS  
- **Kernel:** Linux 6.8 (generic)  
- **CPU:** Intel Core i5-9400 (6 cores)  
- **Memory:** 16 GB RAM  
- **GPU:** Integrated Intel UHD Graphics 630  

The default Ubuntu LTS kernel was retained, as it already provides all required security, stability, and performance characteristics. No experimental or custom kernel modifications were applied.

---

## Running the Application

1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
