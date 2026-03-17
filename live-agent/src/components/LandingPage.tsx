import { Play } from 'lucide-react';
import Navbar from './Navbar';

export default function LandingPage() {

    const globalWithStatic = globalThis as typeof globalThis & {
        __REMOTION_STATIC_FILE__?: (path: string) => string;
    };
    const assetResolver = globalWithStatic.__REMOTION_STATIC_FILE__;
    const dashboardImageSrc = typeof assetResolver === "function"
        ? assetResolver("synapse_dashboard_mockup.png")
        : "/synapse_dashboard_mockup.png";

    return (
        <div className="relative min-h-screen text-white font-manrope selection:bg-primary-purple/30 bg-[#0f0a1e]">
            {/* Background Mesh Gradient */}
            <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary-purple/20 blur-[120px] rounded-full" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-500/10 blur-[120px] rounded-full" />
            </div>

            {/* Navbar Spec: 102px height, 1440px max-width */}
            <Navbar />

            {/* Hero Section Spec: max-width 871px, top-margin 162px */}
            <main className="relative pt-[162px] pb-20 px-6 max-w-[871px] mx-auto flex flex-col items-center text-center z-[2]">

                {/* Trusted Badge Spec: Similar to image reference */}
                <div className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 mb-10 backdrop-blur-sm animate-fade-in text-[10px] font-black uppercase tracking-widest text-[#f6f7f9]/50">
                    Unified Relationship Intelligence
                </div>

                {/* Heading Block Spec: 10px gap, 76px size, 1.15 line-height */}
                <div className="flex flex-col gap-2.5 mb-10 transition-all duration-700">
                    <h1 className="text-5xl md:text-[76px] font-medium font-inter leading-[1.15] tracking-[-2px] text-gradient">
                        Live Voice Intelligence.
                    </h1>
                    <h1 className="text-5xl md:text-[76px] font-normal font-serif italic leading-[1.15] tracking-[-2px] text-white opacity-90">
                        Grounded in your Graph.
                    </h1>
                </div>

                {/* Subtitle Spec: Manrope max-width 613px, 18px size, 26px line-height */}
                <p className="text-[18px] leading-[26px] text-[#f6f7f9] opacity-90 max-w-[750px] mb-12 font-regular">
                    Experience the first multimodal, voice-first briefing engine. Synapse transforms your CRM data into a living Knowledge Graph, empowering Sales, Success, and Win-back teams with real-time intelligence from Salesforce, HubSpot, and Dynamics.
                </p>

                {/* CTA Buttons Spec: 22px gap, vertically centered */}
                <div className="flex flex-col sm:flex-row items-center gap-[22px] mb-20 animate-fade-in-up">
                    <button
                        className="w-full sm:w-auto px-[24px] py-[14px] bg-primary-purple text-white rounded-[10px] font-cabin font-medium text-[16px] leading-[1.7] hover:bg-primary-purple-hover transition-all hover:scale-105 shadow-xl shadow-primary-purple/20 flex items-center justify-center gap-2"
                        onClick={() => window.location.href = '/dashboard?role=csm&tenant_id=9049d8ec'}
                    >
                        Go to Dashboard
                    </button>
                    <button
                        className="w-full sm:w-auto px-[24px] py-[14px] bg-[#2b2344] text-[#f6f7f9] rounded-[10px] font-cabin font-medium text-[16px] leading-[1.7] hover:bg-[#352b54] transition-all hover:scale-105 border border-white/5 flex items-center justify-center gap-2 group"
                        onClick={() => window.open('https://github.com/aroucadi/handoff_agent', '_blank')}
                    >
                        <Play size={16} className="fill-current group-hover:scale-110 transition-transform" />
                        View on GitHub
                    </button>
                </div>

                {/* Dashboard Showcase Spec: 1163px wide, 24px radius, glassmorphic */}
                <div className="w-full max-w-[1163px] md:w-[1163px] md:max-w-[90vw] mt-20 relative p-[22.5px] rounded-[24px] border-[1.5px] border-white/10 bg-white/5 backdrop-blur-[10px] animate-fade-in">
                    <div className="absolute top-8 left-1/2 -translate-x-1/2 px-12 py-3 bg-black/40 border border-white/10 rounded-full text-white/40 text-[11px] font-black uppercase tracking-[0.4em] backdrop-blur-3xl z-20">
                        Synapse Live Agent
                    </div>
                    <div className="absolute inset-0 bg-gradient-to-br from-primary-purple/10 to-transparent rounded-[24px] pointer-events-none" />
                    <img
                        src={dashboardImageSrc}
                        alt="Synapse Dashboard Preview"
                        className="w-full h-auto rounded-[8px] object-cover shadow-2xl relative z-10"
                    />
                </div>

                {/* Simple Footer */}
                <footer className="w-full mt-32 py-12 border-t border-white/5 text-sm text-white/30">
                    <p>© 2026 Synapse. Real-time Customer Intelligence grounded in your data.</p>
                </footer>
            </main>
        </div>
    );
}
