# DevPost Submission: Synapse

## Elevator Pitch
**Synapse – The Living Memory of Your Customer Journey.** 
A Level 5 Multimodal Customer Success Agent that replaces disjointed text-chat with real-time, grounded voice and vision collaboration. 

## The Inspiration
In enterprise software, **80% of critical customer context is lost** during the messy synapse from Sales to Customer Success. CRM notes are buried, technical requirements are forgotten, and new CSMs start blind. We wanted to build an agent that *actually understands* the customer topology and can brief a CSM through a natural, human-like voice conversation while literally looking at their screen.

## What it does
Synapse completely breaks the "text box" paradigm. It is an immersive, split-screen briefing environment for CSMs. 
1. **Automated ETL:** When a deal is marked "Closed Won", Synapse uses **Gemini 3.1 Pro** to parse all sales documents and generate a semantic "Skill Graph" stored in Firestore Native.
2. **Multimodal Live Briefings:** CSMs open the Synapse portal and talk to the agent using the **Gemini Live API** (Gemini 2.0 Flash Exp).
3. **Screen-sharing (Vision):** CSMs can share their screen via WebRTC, and Synapse can "see" what they are working on, cross-referencing visual data with the grounded skill graph.
4. **Zero-Hallucination Design:** You can watch the AI "think". The agent is strictly constrained to specific traversal tools (`follow_link`, `search_graph`). As the agent reasons, the UI visually highlights the nodes it is scanning in a dynamic React Flow graph. 

## How we built it
We engineered Synapse as a production-grade, enterprise application:
- **Models:** Gemini 3.1 Pro (Graph Generation), Gemini 2.0 Flash Exp (Live Vision & Voice), Gemini Embedding 001 (Semantic Search).
- **Frontend:** React + Vite + Custom animated SVGs and React Flow for the visual topography. Remotion for cinematic brand video generation.
- **Backend Infrastructure:** Fully declarative IaC using **Terraform**. We deploy Python microservices to **Google Cloud Run**, leverage **Firestore Native** with Vector extensions for memory, and use **GCS** for media processing.
- **Protocol:** Real-time WebSockets over FastAPI to maintain the ultra-low latency Gemini live connection.

## Challenges we ran into
Connecting a Live Agent to an evolving knowledge graph without inducing latency or hallucinations was incredibly difficult. We initially tried injecting the entire context into the system prompt, but that didn't scale. We solved this by forcing the LLM to use structured tool calls to traverse the graph one node at a time, ensuring strict, deterministic data retrieval.

## Accomplishments that we're proud of
We are incredibly proud of the UX. Building the **Synapse Orb** (a purely animated, 60fps radial SVG that reacts to the agent's voice state) and wiring the backend tool invocations to visually animate the React Flow nodes on the screen creates a magical experience. You don't just get an answer; you see the agent's exact "train of thought" mapped over your customer's data topography.

## What's next for Synapse
Expanding the telemetry observability pipeline and integrating direct hooks into Salesforce and Jira to make Synapse a bidirectional agent that can not only brief CSMs, but actively log action items and tickets during live calls.
