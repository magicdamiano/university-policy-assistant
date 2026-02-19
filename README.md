# University Policy Assistant (Arden University – Proof of Concept)

A policy-safe, evidence-based question answering system designed to help users
navigate official university regulations without hallucination or speculation.

## Purpose

This project demonstrates how a retrieval-based AI assistant can be built to
support questions about university policies while maintaining institutional
standards for accuracy, traceability, and safety.

The system is intentionally conservative:
- It answers only when relevant policy evidence exists
- It avoids guessing or inventing rules
- It clearly refuses when a question falls outside available documentation

## Key Features

- Uses only official university policy documents as sources
- Retrieves policy text at line level for precise evidence
- Groups answers by policy with metadata (title, code, effective date)
- Applies intent-based filtering (complaints, attendance, misconduct, etc.)
- Includes a safety override for dangerous or criminal topics
- Displays confidence based on strength of evidence
- Provides direct links to source PDFs where available

## How It Works (High Level)

1. The user submits a question
2. The system detects the topic (e.g. complaints, attendance, safety)
3. Dangerous or criminal topics are handled immediately and safely
4. Relevant policy text is retrieved from official documents
5. Irrelevant policies are filtered out
6. An answer is generated strictly from retrieved evidence
7. Sources and confidence are shown to the user


## Running the Application

Activate the virtual environment: python app.py 

## Disclaimer

This project is a proof of concept for educational and demonstrative purposes.
It does not represent official advice from Arden University.
