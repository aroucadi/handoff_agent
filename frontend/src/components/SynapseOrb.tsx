/**
 * Synapse — Agent Orb (Animated SVG)
 *
 * A highly dynamic, multi-state SVG representing the agent's voice state.
 * Uses native SVG animations (<animate>, <animateTransform>) for fluid, 60fps rendering
 * without complex JS orchestration.
 */

export type OrbState = 'idle' | 'listening' | 'speaking' | 'thinking';

interface SynapseOrbProps {
    state: OrbState;
}

export default function SynapseOrb({ state }: SynapseOrbProps) {
    // Colors matching the Synapse brand
    const purple = "#7c3aed";
    const cyan = "#38bdf8";

    return (
        <div className="synapse-orb-container" style={{ width: 80, height: 80, position: 'relative' }}>
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: '100%' }}>
                <defs>
                    <radialGradient id="orbGlow" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" stopColor={cyan} stopOpacity="0.8">
                            {state === 'speaking' && (
                                <animate attributeName="stop-opacity" values="0.8; 1; 0.8" dur="0.5s" repeatCount="indefinite" />
                            )}
                        </stop>
                        <stop offset="60%" stopColor={purple} stopOpacity="0.6">
                            {state === 'speaking' && (
                                <animate attributeName="stop-opacity" values="0.6; 0.9; 0.6" dur="0.8s" repeatCount="indefinite" />
                            )}
                        </stop>
                        <stop offset="100%" stopColor={purple} stopOpacity="0" />
                    </radialGradient>

                    <radialGradient id="ringGrad" cx="50%" cy="50%" r="50%">
                        <stop offset="80%" stopColor={cyan} stopOpacity="0" />
                        <stop offset="95%" stopColor={cyan} stopOpacity="0.8" />
                        <stop offset="100%" stopColor={cyan} stopOpacity="0" />
                    </radialGradient>
                </defs>

                {/* Background Core */}
                <circle cx="50" cy="50" r="30" fill="url(#orbGlow)">
                    {state === 'idle' && (
                        <animate attributeName="r" values="28; 32; 28" dur="4s" repeatCount="indefinite" />
                    )}
                    {(state === 'listening' || state === 'thinking') && (
                        <animate attributeName="r" values="29; 35; 29" dur="2s" repeatCount="indefinite" />
                    )}
                    {state === 'speaking' && (
                        <animate attributeName="r" values="30; 38; 32; 40; 30" dur="1s" repeatCount="indefinite" />
                    )}
                </circle>

                {/* Core Inner Dot */}
                <circle cx="50" cy="50" r="10" fill="#fff" opacity={state === 'idle' ? 0.3 : 0.8}>
                    {state === 'speaking' && (
                        <animate attributeName="r" values="8; 14; 10; 16; 8" dur="0.75s" repeatCount="indefinite" />
                    )}
                    {state === 'thinking' && (
                        <animate attributeName="opacity" values="0.8; 0.3; 0.8" dur="1s" repeatCount="indefinite" />
                    )}
                </circle>

                {/* Listening Ripples */}
                {state === 'listening' && (
                    <>
                        <circle cx="50" cy="50" r="30" fill="none" stroke={cyan} strokeWidth="1" opacity="0">
                            <animate attributeName="r" values="30; 45" dur="1.5s" repeatCount="indefinite" />
                            <animate attributeName="opacity" values="0.8; 0" dur="1.5s" repeatCount="indefinite" />
                        </circle>
                        <circle cx="50" cy="50" r="30" fill="none" stroke={purple} strokeWidth="1" opacity="0">
                            <animate attributeName="r" values="30; 45" dur="1.5s" begin="0.75s" repeatCount="indefinite" />
                            <animate attributeName="opacity" values="0.8; 0" dur="1.5s" begin="0.75s" repeatCount="indefinite" />
                        </circle>
                    </>
                )}

                {/* Speaking Wave Nodes */}
                {state === 'speaking' && (
                    <g fill="none" stroke={cyan} strokeWidth="2" strokeLinecap="round">
                        <circle cx="50" cy="50" r="36" strokeDasharray="10 20" stroke={cyan}>
                            <animateTransform attributeName="transform" type="rotate" from="0 50 50" to="360 50 50" dur="3s" repeatCount="indefinite" />
                            <animate attributeName="stroke-dasharray" values="10 20; 20 10; 10 20" dur="1s" repeatCount="indefinite" />
                        </circle>
                        <circle cx="50" cy="50" r="42" strokeDasharray="15 30" stroke={purple}>
                            <animateTransform attributeName="transform" type="rotate" from="360 50 50" to="0 50 50" dur="4s" repeatCount="indefinite" />
                            <animate attributeName="stroke-dasharray" values="15 30; 30 15; 15 30" dur="1.5s" repeatCount="indefinite" />
                        </circle>
                        <circle cx="50" cy="50" r="48" strokeDasharray="5 40" stroke="#fff" opacity="0.4">
                            <animateTransform attributeName="transform" type="rotate" from="0 50 50" to="360 50 50" dur="2s" repeatCount="indefinite" />
                            <animate attributeName="r" values="46; 50; 46" dur="0.5s" repeatCount="indefinite" />
                        </circle>
                    </g>
                )}
            </svg>
        </div>
    );
}
