# 🤖 Synapse AI Agents Architecture

Synapse relies on a suite of **specialized, purpose-driven AI Agents** powered by Google's Gemini models. By dividing cognitive labor between asynchronous data extraction models and sub-second real-time conversational models, Synapse achieves its "Level 5 Agent" status.

---

## 1. The Graph Generator (Asynchronous Multi-Agent)
**Model Usage:** `gemini-3.1-pro`

When a deal transitions to "Closed Won," the webhook triggers the Graph Generator pipeline. Producing a highly accurate, structured skill graph from unstructured transcripts and PDFs is too complex for a single zero-shot prompt. Thus, we utilize a **Multi-Agent pattern**:

### Phase A: The Extractor Agents
- **CRM Extractor**: Parses strictly structured JSON payload data (Account names, MRR, Stakeholders).
- **Transcript Extractor**: Summarizes raw sales call transcripts, identifying technical requirements and objections.
- **Contract Extractor**: Extracts line-items, SLAs, and technical deliverables from the signed PDF.

### Phase B: Generator vs. Reviewer (Account-Oriented Delta)
1. **The Generator Pass**: The primary agent takes the compiled extractions from Phase A and drafts an array of "Nodes". In the latest evolution, this is **Account-Oriented**: it pulls historical deals and existing account context to generate "Delta" nodes that only reflect new changes or deep-dive specifics.
2. **The Reviewer Pass**: A secondary agent acting as a "Critic" evaluates the delta. It ensures wikilinks correctly point to both new delta nodes and existing core account nodes (e.g., [[account-profile]]).

---

## 2. The Semantic Indexer
**Model Usage:** `text-embedding-004` (via Vertex Vector Search)

Before the Live Agent can query the graph, Synapse generates high-dimensional vector embeddings for the content of every generated node. These embeddings are stored alongside the node metadata in **Google Firestore**. 

When a CSM asks a vague question ("What were their security concerns?"), the system converts the query to an embedding and performs a fast ANN (Approximate Nearest Neighbor) vector search in Firestore to retrieve the exact nodes required, bypassing exact-keyword dependencies.

---

## 3. The Vision Live Agent (Real-Time WebRTC)
**Model Usage:** `gemini-2.0-flash-exp`

The crown jewel of Synapse is the interactive Voice Agent. When a CSM clicks "Start Briefing", the browser connects a bidirectional WebRTC audio/video stream directly to the Gemini Live endpoint via the backend Python broker.

### WebRTC Architecture
- **Audio Input:** The CSM speaks naturally into their microphone. No push-to-talk.
- **Audio Output:** The agent responds with a natural, synthesized human voice.
- **Vision Input:** The React frontend captures `<canvas>` snapshots of the CSM's screen (the interactive skill graph) and streams them as `image/jpeg` frames over WebRTC. The agent literally **sees** what the user is looking at or hovering their mouse over.

### Function Calling (Tools)
To make the agent capable of taking action, its system prompt assigns it three server-side tools:
1. `search_graph(query)`: Invokes the Semantic Indexer to find relevant nodes across product, industry, and account layers.
2. `follow_link(source_id)`: Fetches the connected child nodes to explore a topic deeply (e.g., from an account-level risk to a specific deal requirement).
3. `escalate_risk(client_id, reason)`: Directly hits the CRM Simulator API to flag a customer account as "At Risk".

### Multi-Role Support
Synapse now supports dynamic personas based on the user's role:
- **CSM**: Focused on customer health, success metrics, and long-term ROI.
- **Sales (Account Executive)**: Focused on expansion opportunities, historical deal context, and stakeholder mapping.
- **Customer Support**: Focused on technical requirements, SLAs, and resolved/open issues.
- **Win Back**: Specialized persona for at-risk accounts, focusing on resolving pain points and historical objections.

The Hub allows per-tenant configuration of these roles, ensuring the agent adopts the correct tone and knowledge-retrieval strategy for each session.
