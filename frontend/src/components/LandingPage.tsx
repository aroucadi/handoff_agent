import { useNavigate } from 'react-router-dom';
import { Github, Zap, Shield, Cpu, Layout, ArrowRight, ExternalLink } from 'lucide-react';

export default function LandingPage() {
    const navigate = useNavigate();

    return (
        <div className="web3-landing">
            {/* Background Video */}
            <video
                className="web3-bg-video"
                src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260217_030345_246c0224-10a4-422c-b324-070b7c0eceda.mp4"
                autoPlay
                loop
                muted
                playsInline
            />

            {/* 50% Black Overlay */}
            <div className="web3-overlay" />

            <div className="web3-content">
                {/* Navbar */}
                <nav className="web3-nav">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '30px' }}>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', letterSpacing: '-0.03em', cursor: 'pointer' }} onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
                            Synapse
                        </div>
                        <div className="web3-nav-links">
                            <a href="#features" style={{ color: '#fff', textDecoration: 'none', fontSize: '14px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '8px', opacity: 0.9 }}>
                                Features
                            </a>
                            <a href="#hub" style={{ color: '#fff', textDecoration: 'none', fontSize: '14px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '8px', opacity: 0.9 }}>
                                The Hub
                            </a>
                            <a href="#how-it-works" style={{ color: '#fff', textDecoration: 'none', fontSize: '14px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '8px', opacity: 0.9 }}>
                                How it Works
                            </a>
                        </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                        {import.meta.env.VITE_HUB_URL && (
                            <a
                                href={import.meta.env.VITE_HUB_URL}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="web3-nav-link-secondary"
                                style={{ color: 'rgba(255,255,255,0.7)', textDecoration: 'none', fontSize: '14px', fontWeight: 500 }}
                            >
                                Tenant Hub
                            </a>
                        )}
                        <button className="web3-pill-btn" onClick={() => navigate('/roles')}>
                            Launch App
                        </button>
                    </div>
                </nav>

                {/* Hero Content */}
                <main style={{
                    paddingTop: 'clamp(100px, 20vh, 280px)',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '40px',
                    textAlign: 'center',
                    paddingLeft: '24px',
                    paddingRight: '24px'
                }}>

                    {/* Badge */}
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        padding: '6px 14px',
                        background: 'rgba(255,255,255,0.1)',
                        border: '1px solid rgba(255,255,255,0.2)',
                        borderRadius: '20px',
                        fontSize: '13px',
                        fontWeight: 500
                    }}>
                        <div style={{ width: '4px', height: '4px', background: '#fff', borderRadius: '50%' }} />
                        <span style={{ opacity: 0.6 }}>Early access available from</span>
                        <span>May 1, 2026</span>
                    </div>

                    {/* Heading */}
                    <h1 className="web3-hero-heading" style={{
                        margin: 0,
                        maxWidth: '800px',
                        fontSize: 'clamp(36px, 5vw, 64px)',
                        fontWeight: 700,
                        lineHeight: 1.1,
                        letterSpacing: '-0.02em',
                        paddingBottom: '8px'
                    }}>
                        AI Intelligence at the Speed of Experience
                    </h1>

                    {/* Subtitle */}
                    <p style={{
                        margin: 0,
                        maxWidth: '680px',
                        fontSize: '16px',
                        fontWeight: 400,
                        color: 'rgba(255,255,255,0.7)',
                        lineHeight: 1.6,
                        marginTop: '-16px'
                    }}>
                        Powering seamless experiences and real-time connections, Synapse is the multimodal voice agent for teams who move with purpose, leveraging sub-second latency and dynamic skill graphs to shape the future of CRM.
                    </p>

                    {/* CTA Row */}
                    <div style={{
                        display: 'flex',
                        gap: '16px',
                        alignItems: 'center',
                        flexWrap: 'wrap',
                        justifyContent: 'center'
                    }}>
                        <button className="web3-pill-btn web3-pill-btn--light" onClick={() => navigate('/roles')}>
                            Start Briefing <ArrowRight size={16} />
                        </button>
                        {import.meta.env.VITE_HUB_URL && (
                            <a href={import.meta.env.VITE_HUB_URL} target="_blank" rel="noopener noreferrer" className="web3-pill-btn web3-pill-btn--outline">
                                <Layout size={16} /> Open Hub
                            </a>
                        )}
                        <a href="https://github.com/aroucadi/synapse_agent" target="_blank" rel="noopener noreferrer" className="web3-pill-btn web3-pill-btn--outline">
                            <Github size={16} /> View on GitHub
                        </a>
                    </div>

                    <div style={{ height: '20vh' }} />

                    {/* Features Section */}
                    <section id="features" className="landing-section">
                        <div className="section-header">
                            <span className="section-badge">Capabilities</span>
                            <h2 className="section-title">Beyond the Text Box</h2>
                        </div>
                        <div className="features-grid">
                            <div className="feature-card glass-card">
                                <Zap className="feature-icon" color="#22d3ee" />
                                <h3>Living Memory</h3>
                                <p>Synapse replaces disjointed text-chat with real-time, grounded voice and vision collaboration that understands your topology.</p>
                            </div>
                            <div className="feature-card glass-card">
                                <Shield className="feature-icon" color="#a855f7" />
                                <h3>Zero Hallucination</h3>
                                <p>Grounded graph traversal ensures the agent never guesses—it literally moves through historical and product data topography.</p>
                            </div>
                            <div className="feature-card glass-card">
                                <Layout className="feature-icon" color="#fb7185" />
                                <h3>Multi-tenant Hub</h3>
                                <p>A central management layer where different companies configure branding, personas, and account data seamlessly.</p>
                            </div>
                            <div className="feature-card glass-card">
                                <Cpu className="feature-icon" color="#34d399" />
                                <h3>Delta Knowledge</h3>
                                <p>Automatic deal-oriented extraction weaves new information into existing Account Knowledge Graphs with Gemini 3.1 Pro.</p>
                            </div>
                        </div>
                    </section>

                    {/* The Hub Section */}
                    <section id="hub" className="landing-section hub-showcase">
                        <div className="showcase-content">
                            <span className="section-badge">The Hub</span>
                            <h2 className="section-title">Command Central for Tenants</h2>
                            <p>Configure personas (CSM, Sales, Support), manage multi-tenant metadata, and track deal life-cycle transitions through the Synapse Hub interface.</p>
                            <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
                                <button className="web3-pill-btn web3-pill-btn--light" onClick={() => window.open(import.meta.env.VITE_HUB_URL || '#', '_blank')}>
                                    Go to Hub <ExternalLink size={16} />
                                </button>
                            </div>
                        </div>
                        <div className="showcase-visual glass-card">
                            {/* Placeholder for Hub UI preview */}
                            <div className="visual-mockup">
                                <div className="mock-header" />
                                <div className="mock-body">
                                    <div className="mock-sidebar" />
                                    <div className="mock-main">
                                        <div className="mock-stat" />
                                        <div className="mock-list" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* How it Works */}
                    <section id="how-it-works" className="landing-section">
                        <div className="section-header">
                            <span className="section-badge">Pipeline</span>
                            <h2 className="section-title">The Synapse Loop</h2>
                        </div>
                        <div className="pipeline-steps">
                            {[
                                { title: 'CRM Trigger', desc: 'Deal moves to "Closed Won" in Salesforce or our mock CRM.' },
                                { title: 'Graph Gen', desc: 'Cloud Run Job reads transcripts and contracts to build a 20-node graph.' },
                                { title: 'Live Briefing', desc: 'CSM talks to Gemini Live, which traverses the graph in real-time.' }
                            ].map((step, i) => (
                                <div key={i} className="pipeline-step">
                                    <div className="step-num">{i + 1}</div>
                                    <div className="step-content">
                                        <h4>{step.title}</h4>
                                        <p>{step.desc}</p>
                                    </div>
                                    {i < 2 && <div className="step-line" />}
                                </div>
                            ))}
                        </div>
                    </section>

                    <footer style={{ padding: '80px 0 40px', opacity: 0.5, fontSize: '12px', borderTop: '1px solid rgba(255,255,255,0.1)', width: '100%', maxWidth: '1200px', alignSelf: 'center' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>© 2026 Synapse Multimodal. Built for the Gemini Live Challenge.</span>
                            <div style={{ display: 'flex', gap: '24px' }}>
                                <span>Privacy</span>
                                <span>Terms</span>
                                <span>Security</span>
                            </div>
                        </div>
                    </footer>
                </main>
            </div>
        </div>
    );
}
