# AGENTS.md

This file guides AI coding agents on how to interact with the **Agentic SDR SolarPrime** project.

## Agentic SDR SolarPrime

The **Agentic SDR SolarPrime** is a conversational AI system designed to act as a Sales Development Representative (SDR) for SolarPrime. The agent, named **Helen Vieira**, interacts with leads via WhatsApp to qualify them, present solar energy solutions, respond to objections, and schedule meetings.

## Architecture

The system's core is its **stateless architecture**, implemented in the `AgenticSDRStateless` class (`app/agents/agentic_sdr_stateless.py`).

-   **Request-based Isolation:** Each user message creates a **new agent instance**. No state (like conversation history or lead information) is stored in the agent's memory between interactions.
-   **Explicit Context:** All necessary context for processing (history, lead data, etc.) is loaded from the database (Supabase) with each new message and passed to the agent through an `execution_context`.

This approach ensures the system is thread-safe, horizontally scalable, and robust, as there's no risk of state contamination between concurrent conversations.

## Commands

-   **Run the application:** `uvicorn main:app --host 0.0.0.0 --port 8000`
-   **Install dependencies:** `pip install -r requirements.txt`
-   **Run with Docker:** `docker-compose up`
