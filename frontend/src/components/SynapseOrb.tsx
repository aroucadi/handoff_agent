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
    // Colors matching the new Synapse brand
    const purple = "#a855f7";
    const cyan = "#22d3ee";
    const magenta = "#ec4899";

    return (
        <div className="synapse-orb-container" style={{ width: 120, height: 120, position: 'relative' }}>
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: '100%' }}>
                <defs>
                    <radialGradient id="orbGlow" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" stopColor={cyan} stopOpacity="0.9">
                            {state === 'speaking' && (
                                <animate attributeName="stop-opacity" values="0.9; 1; 0.9" dur="0.4s" repeatCount="indefinite" />
                            )}
                        </stop>
                        <stop offset="40%" stopColor={purple} stopOpacity="0.7">
                            {state === 'speaking' && (
                                <animate attributeName="stop-opacity" values="0.7; 1; 0.7" dur="0.6s" repeatCount="indefinite" />
                            )}
                        </stop>
                        <stop offset="70%" stopColor={magenta} stopOpacity="0.5">
                            {state === 'speaking' && (
                                <animate attributeName="stop-opacity" values="0.5; 0.9; 0.5" dur="0.8s" repeatCount="indefinite" />
                            )}
                        </stop>
                        <stop offset="100%" stopColor={purple} stopOpacity="0" />
                    </radialGradient>
                </defs>

                {/* Background Core Glow */}
                <circle cx="50" cy="50" r="35" fill="url(#orbGlow)">
                    {state === 'idle' && (
                        <animate attributeName="r" values="32; 38; 32" dur="4s" repeatCount="indefinite" />
                    )}
                    {(state === 'listening' || state === 'thinking') && (
                        <animate attributeName="r" values="34; 42; 34" dur="2s" repeatCount="indefinite" />
                    )}
                    {state === 'speaking' && (
                        <animate attributeName="r" values="35; 45; 38; 48; 35" dur="0.8s" repeatCount="indefinite" />
                    )}
                </circle>

                {/* Core Inner Dot */}
                <circle cx="50" cy="50" r="12" fill="#fff" opacity={state === 'idle' ? 0.4 : 0.9} filter="blur(1px)">
                    {state === 'speaking' && (
                        <animate attributeName="r" values="10; 18; 12; 20; 10" dur="0.6s" repeatCount="indefinite" />
                    )}
                    {state === 'thinking' && (
                        <animate attributeName="opacity" values="0.9; 0.4; 0.9" dur="1s" repeatCount="indefinite" />
                    )}
                </circle>

                {/* Listening Ripples */}
                {state === 'listening' && (
                    <>
                        <circle cx="50" cy="50" r="35" fill="none" stroke={cyan} strokeWidth="1.5" opacity="0">
                            <animate attributeName="r" values="35; 55" dur="2s" repeatCount="indefinite" />
                            <animate attributeName="opacity" values="1; 0" dur="2s" repeatCount="indefinite" />
                        </circle>
                        <circle cx="50" cy="50" r="35" fill="none" stroke={purple} strokeWidth="1.5" opacity="0">
                            <animate attributeName="r" values="35; 55" dur="2s" begin="1s" repeatCount="indefinite" />
                            <animate attributeName="opacity" values="1; 0" dur="2s" begin="1s" repeatCount="indefinite" />
                        </circle>
                    </>
                )}

                {/* Speaking Wave Nodes */}
                {state === 'speaking' && (
                    <g fill="none" strokeWidth="2.5" strokeLinecap="round">
                        <circle cx="50" cy="50" r="42" strokeDasharray="12 24" stroke={cyan} opacity="0.8">
                            <animateTransform attributeName="transform" type="rotate" from="0 50 50" to="360 50 50" dur="3s" repeatCount="indefinite" />
                            <animate attributeName="stroke-dasharray" values="12 24; 24 12; 12 24" dur="0.8s" repeatCount="indefinite" />
                        </circle>
                        <circle cx="50" cy="50" r="48" strokeDasharray="18 36" stroke={purple} opacity="0.6">
                            <animateTransform attributeName="transform" type="rotate" from="360 50 50" to="0 50 50" dur="5s" repeatCount="indefinite" />
                            <animate attributeName="stroke-dasharray" values="18 36; 36 18; 18 36" dur="1.2s" repeatCount="indefinite" />
                        </circle>
                        <circle cx="50" cy="50" r="54" strokeDasharray="6 48" stroke="#fff" opacity="0.3">
                            <animateTransform attributeName="transform" type="rotate" from="0 50 50" to="360 50 50" dur="2.5s" repeatCount="indefinite" />
                            <animate attributeName="r" values="52; 56; 52" dur="0.4s" repeatCount="indefinite" />
                        </circle>
                    </g>
                )}
            </svg>
        </div>
    );
}
