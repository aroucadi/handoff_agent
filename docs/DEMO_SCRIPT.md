# Synapse: "Golden Run" Demo Script

**Target Length:** 4 minutes
**Goal:** Prove the Level 5 Multimodal Agent architecture (Vision + Voice + Tooling) without any "text box" interactions. Prove hallucination-free grounding via the dynamic React Flow skill graph.

---

### Phase 1: The Hook (0:00 - 0:30)
* **Visual:** Browser showing the new `/` landing page. Dark theme, animated particles, "The Living Memory of Your Customer Journey".
* **Narrator:** *"80% of customer knowledge is lost between Sales and Customer Success. Synapse fixes this immediately. It's a Level 5 Multimodal AI Live Agent. Watch what happens when a deal closes."*
* **Action:** Click "🚀 Launch Dashboard".
* **Visual:** Dashboard loads. Click "Simulate Deal Won".
* **Narrator:** *"A webhook fires. Our backend Cloud Run service uses Gemini 3.1 Pro to automatically extract entities from the CRM notes into a navigable skill graph stored in Firestore."*

### Phase 2: Live Conversation & Graph Traversal (0:30 - 2:00)
* **Action:** Click "Start Briefing" next to the new client.
* **Visual:** Split-screen loads. **Orb starts pulsing (Standing by).** React Flow topology loads on the right.
* **Action:** Press the Spacebar (Mic On).
* **You (Voice):** *"Synapse, I'm taking over the Acme Corp account. What's the main implementation blocker?"*
* **Visual:** Watch the **Synapse Orb** spin up into the multi-ring "speaking" state as the agent replies via WebRTC audio. **CRUCIAL:** Point the mouse to the React Flow graph. You will see the agent call the `follow_link` tool and the nodes literally **pulse cyan** as the agent reads the data.
* **Synapse (Voice):** *"Acme Corp is blocked by legacy AS/400 integration. They need single sign-on before Q3."*
* **Narrator:** *"Notice the graph. The agent isn't hallucinating. It is restricted to reading the skill graph using strict tool calls. You see exactly what it's thinking."*

### Phase 3: The Vision Flex (2:00 - 3:00)
* **Action:** Click the "Share Vision (💻)" button. A screen-share picker appears. Select a window showing a mock technical architecture diagram or an angry customer email.
* **You (Voice):** *"Synapse, look at this architecture diagram I'm sharing. Does this match the requirements we discussed during the sales cycle?"*
* **Visual:** The agent uses `read_index` tool to scan the graph for architecture requirements, comparing it in real-time to the video frames streamed to Gemini 2.0 Flash Exp.
* **Synapse (Voice):** *"I see the diagram includes a Postgres database, but my graph shows the client specifically requested an Oracle integration in the initial scoping call. This might be a mismatch."*
* **Narrator:** *"This is true multimodal capability. Screen sharing paired with deeply grounded, customer-specific knowledge."*

### Phase 4: Cinematic Outro (3:00 - 4:00)
* **Narrator:** *"Synapse is deployed via one-click Terraform on Google Cloud. We built this from scratch for the Gemini Live Agent Challenge."*
* **Video Edit:** Cut from the live demo to the **Remotion Brand Video** (`frontend/public/synapse-brand.mp4`) to play out the final 60 seconds of the video, showcasing the animations, Level 5 capabilities recap, and the final hackathon badge.
