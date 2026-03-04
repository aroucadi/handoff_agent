import { useNavigate } from 'react-router-dom';
import { Play, Star } from 'lucide-react';
import BackgroundVideo from './BackgroundVideo';
import Navbar from './Navbar';

export default function LandingPage() {
    const navigate = useNavigate();

    return (
        <div className="relative min-h-screen text-white font-manrope selection:bg-primary-purple/30">
            {/* Background Video Spec: 120% scale handled in component */}
            <BackgroundVideo
                src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260215_121759_424f8e9c-d8bd-4974-9567-52709dfb6842.mp4"
            />

            {/* Navbar Spec: 102px height, 1440px max-width */}
            <Navbar />

            {/* Hero Section Spec: max-width 871px, top-margin 162px */}
            <main className="relative pt-[162px] pb-20 px-6 max-w-[871px] mx-auto flex flex-col items-center text-center z-[2]">

                {/* Trusted Badge Spec: Similar to image reference */}
                <div className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 mb-10 backdrop-blur-sm animate-fade-in">
                    <div className="flex -space-x-2">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="w-6 h-6 rounded-full border-2 border-black bg-white/10 flex items-center justify-center overflow-hidden">
                                <span className="text-[10px]"><Star size={10} className="fill-white" /></span>
                            </div>
                        ))}
                    </div>
                    <span className="text-sm font-medium text-white/80">Trusted by over <span className="text-white font-bold">12,000+</span> CS teams globally</span>
                </div>

                {/* Heading Block Spec: 10px gap, 76px size, 1.15 line-height */}
                <div className="flex flex-col gap-2.5 mb-10 transition-all duration-700">
                    <h1 className="text-5xl md:text-[76px] font-medium font-inter leading-[1.15] tracking-[-2px] text-white">
                        Restore memory.
                    </h1>
                    <h1 className="text-5xl md:text-[76px] font-normal font-serif italic leading-[1.15] tracking-[-2px] text-white opacity-90">
                        Focus on the briefing.
                    </h1>
                </div>

                {/* Subtitle Spec: Manrope max-width 613px, 18px size, 26px line-height */}
                <p className="text-[18px] leading-[26px] text-[#f6f7f9] opacity-90 max-w-[613px] mb-12 font-regular">
                    Synapse handles deal context extraction and knowledge grounding, so your CSMs can walk into every kickoff fully informed.
                </p>

                {/* CTA Buttons Spec: 22px gap, vertically centered */}
                <div className="flex flex-col sm:flex-row items-center gap-[22px] mb-20 animate-fade-in-up">
                    <button
                        className="w-full sm:w-auto px-[24px] py-[14px] bg-primary-purple text-white rounded-[10px] font-cabin font-medium text-[16px] leading-[1.7] hover:bg-primary-purple-hover transition-all hover:scale-105 shadow-xl shadow-primary-purple/20 flex items-center justify-center gap-2"
                        onClick={() => navigate('/roles')}
                    >
                        Get Started Free
                    </button>
                    <button
                        className="w-full sm:w-auto px-[24px] py-[14px] bg-[#2b2344] text-[#f6f7f9] rounded-[10px] font-cabin font-medium text-[16px] leading-[1.7] hover:bg-[#352b54] transition-all hover:scale-105 border border-white/5 flex items-center justify-center gap-2 group"
                        onClick={() => navigate('/roles')}
                    >
                        <Play size={16} className="fill-current group-hover:scale-110 transition-transform" />
                        Watch 2min Demo
                    </button>
                </div>

                {/* Dashboard Showcase Spec: 1163px wide, 24px radius, glassmorphic */}
                <div className="w-full max-w-[1163px] md:w-[1163px] md:max-w-[90vw] mt-20 relative p-[22.5px] rounded-[24px] border-[1.5px] border-white/10 bg-white/5 backdrop-blur-[10px] animate-fade-in">
                    <div className="absolute top-8 left-1/2 -translate-x-1/2 px-12 py-3 bg-black/40 border border-white/10 rounded-full text-white/40 text-[11px] font-black uppercase tracking-[0.4em] backdrop-blur-3xl z-20">
                        Synapse Dashboard
                    </div>
                    <div className="absolute inset-0 bg-gradient-to-br from-primary-purple/10 to-transparent rounded-[24px] pointer-events-none" />
                    <img
                        src="/synapse_dashboard_mockup.png"
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
