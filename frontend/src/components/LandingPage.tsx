/**
 * Synapse — Landing Page Component
 *
 * Premium hero section with brand video, features, and CTA.
 * The entry point for the hackathon demo experience.
 */

import { useNavigate } from 'react-router-dom';

export default function LandingPage() {
    const navigate = useNavigate();

    return (
        <div className="landing">
            {/* ── Hero Section ────────────────────────── */}
            <section className="landing__hero">
                <div className="landing__glow" />
                <div className="landing__particles">
                    {Array.from({ length: 20 }).map((_, i) => (
                        <span key={i} className="particle" style={{
                            left: `${(i * 7.3) % 100}%`,
                            top: `${(i * 5.1 + 10) % 90}%`,
                            animationDelay: `${(i * 0.3) % 4}s`,
                            width: `${3 + (i % 3)}px`,
                            height: `${3 + (i % 3)}px`,
                        }} />
                    ))}
                </div>
                <h1 className="landing__logo">Synapse</h1>
                <p className="landing__tagline">The Living Memory of Your Customer Journey</p>
                <p className="landing__desc">
                    A Level 5 Multimodal AI Agent that transforms CRM deal closures into
                    real-time, grounded customer success briefings — with voice and vision.
                </p>
                <div className="landing__cta-row">
                    <button className="btn btn--hero" onClick={() => navigate('/dashboard')}>
                        🚀 Launch Dashboard
                    </button>
                    <a className="btn btn--hero-outline" href="https://github.com/aroucadi/synapse_agent" target="_blank" rel="noopener noreferrer">
                        ⭐ View on GitHub
                    </a>
                </div>
            </section>

            {/* ── Video Section ────────────────────────── */}
            <section className="landing__video-section">
                <h2 className="landing__section-title">See Synapse in Action</h2>
                <div className="landing__video-frame">
                    <video
                        className="landing__video"
                        src="/synapse-brand.mp4"
                        controls
                        poster=""
                        playsInline
                    >
                        Your browser does not support the video tag.
                    </video>
                    <p className="landing__video-hint">
                        Video not loading? Render it with: <code>cd video && npm run render</code> then copy <code>out/synapse-brand.mp4</code> to <code>frontend/public/</code>
                    </p>
                </div>
            </section>

            {/* ── Features Grid ────────────────────────── */}
            <section className="landing__features">
                <h2 className="landing__section-title">Level 5 Capabilities</h2>
                <div className="landing__features-grid">
                    {[
                        { icon: '👁️', title: 'Sees', desc: 'Screen-sharing via WebRTC — the agent sees your CRM in real time.', color: '#7c3aed' },
                        { icon: '🎙️', title: 'Speaks', desc: 'Gemini Live voice streaming with sub-second latency.', color: '#38bdf8' },
                        { icon: '🧠', title: 'Reasons', desc: 'Skill graph navigation — grounded, zero-hallucination answers.', color: '#10b981' },
                        { icon: '🔍', title: 'Searches', desc: 'Firestore Native Vector Search for semantic retrieval.', color: '#f59e0b' },
                        { icon: '📊', title: 'Observes', desc: 'Async telemetry traces for full agent observability.', color: '#f43f5e' },
                        { icon: '☁️', title: 'Deploys', desc: 'One-click Terraform IaC — entire stack on GCP in minutes.', color: '#a78bfa' },
                    ].map((f, i) => (
                        <div key={i} className="feature-card" style={{ borderColor: f.color }}>
                            <span className="feature-card__icon">{f.icon}</span>
                            <h3 className="feature-card__title" style={{ color: f.color }}>{f.title}</h3>
                            <p className="feature-card__desc">{f.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* ── How It Works ────────────────────────── */}
            <section className="landing__how">
                <h2 className="landing__section-title">How It Works</h2>
                <div className="landing__steps">
                    {[
                        { num: '1', title: 'Deal Closes', desc: 'A CRM webhook fires when a deal moves to "Closed Won".' },
                        { num: '2', title: 'Graph Generates', desc: 'Gemini 3.1 Pro extracts entities into a navigable skill graph.' },
                        { num: '3', title: 'CSM Briefs', desc: 'Talk to Synapse. Ask anything. Get grounded, instant answers.' },
                    ].map((s, i) => (
                        <div key={i} className="step-card">
                            <div className="step-card__num">{s.num}</div>
                            <h3 className="step-card__title">{s.title}</h3>
                            <p className="step-card__desc">{s.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* ── Footer ────────────────────────── */}
            <footer className="landing__footer">
                <p>Built for the <span style={{ color: '#38bdf8' }}>Gemini Live Agent Challenge</span></p>
                <p className="landing__footer-models">
                    Powered by Gemini 3.1 Pro · Gemini 2.0 Flash Exp · Embedding 001 · Firestore Vector Search
                </p>
            </footer>
        </div>
    );
}
