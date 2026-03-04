# DevPost Submission: Synapse

## Elevator Pitch
**Synapse – The Living Memory of Your Customer Journey.** 
A Level 5 Multimodal Customer Success Agent that replaces disjointed text-chat with real-time, grounded voice and vision collaboration. 

## The Inspiration
In enterprise software, **80% of critical customer context is lost** during the messy synapse from Sales to Customer Success. CRM notes are buried, technical requirements are forgotten, and new CSMs start blind. We wanted to build an agent that *actually understands* the customer topology and can brief a CSM through a natural, human-like voice conversation while literally looking at their screen.

## What it does
Synapse completely breaks the "text box" paradigm. It is an immersive, split-screen briefing environment for CSMs. 
1. **Synapse Hub (Multi-tenant Portal):** A central management layer where different companies (Tenants) configure their branding, agent personas (CSM, Sales, Support, WinBack), and account data.
2. **Account-Oriented Delta ETL:** When a new deal closes, Synapse uses **Gemini 3.1 Pro** to weave a "Delta" into the existing Account Knowledge Graph, preserving historical deal continuity and risk evolution.
3. **Multimodal Live Briefings:** CSMs open the multi-role portal and talk to the agent using the **Gemini Live API** (Gemini 2.5 Flash Native Audio).
4. **Zero-Hallucination Design:** Grounded graph traversal ensures the agent never guesses—it literally moves through the account's historical and product data topography.

## How we built it
We engineered Synapse as a production-grade, enterprise application:
- **Models:** Gemini 3.1 Pro (Delta Graph Gen), Gemini 2.5 Flash Native Audio (Live Vision & Voice), Gemini Embedding 001 (Multi-tenant Semantic Search).
- **Frontend:** Multi-role React Portal + Synapse Hub + Custom animated SVGs and React Flow topography.
- **Backend:** Multi-tenant Python microservices on **Google Cloud Run**, **Firestore Native** with
* **`synapse-hub`**: The multi-tenant configuration portal and metadata API.
* **`synapse-api`**: Core Voice service handling multi-role sessions and WebRTC bridging.
* **`synapse-graph-generator`**: Account-oriented delta knowledge pipe (Timeout: `900s`).
* **`synapse-crm-simulator`**: SalesClaw mock CRM for deal life-cycle simulation.

## Challenges we ran into
Connecting a Live Agent to an evolving knowledge graph without inducing latency or hallucinations was incredibly difficult. We initially tried injecting the entire context into the system prompt, but that didn't scale. We solved this by forcing the LLM to use structured tool calls to traverse the graph one node at a time, ensuring strict, deterministic data retrieval.

## Accomplishments that we're proud of
We are incredibly proud of the UX. Building the **Synapse Orb** (a purely animated, 60fps radial SVG that reacts to the agent's voice state) and wiring the backend tool invocations to visually animate the React Flow nodes on the screen creates a magical experience. You don't just get an answer; you see the agent's exact "train of thought" mapped over your customer's data topography.

## What's next for Synapse
Expanding the telemetry observability pipeline and integrating direct hooks into Salesforce and Jira to make Synapse a bidirectional agent that can not only brief CSMs, but actively log action items and tickets during live calls.
