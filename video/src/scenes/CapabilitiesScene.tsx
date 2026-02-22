import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";

const capabilities = [
    { icon: "👁️", label: "Sees", desc: "Vision via WebRTC", color: "#7c3aed" },
    { icon: "🎙️", label: "Speaks", desc: "Gemini Live Voice", color: "#38bdf8" },
    { icon: "🔍", label: "Searches", desc: "Firestore Vector Search", color: "#10b981" },
    { icon: "📊", label: "Observes", desc: "Telemetry & Tracing", color: "#f59e0b" },
];

export const CapabilitiesScene: React.FC = () => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();

    // Title
    const titleOpacity = interpolate(frame, [0, fps], [0, 1], { extrapolateRight: "clamp" });

    // Badge label 
    const levelOpacity = interpolate(frame, [1.5 * fps, 2.5 * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const levelScale = spring({ frame: Math.max(0, frame - 1.5 * fps), fps, config: { damping: 10, mass: 0.5 }, durationInFrames: fps });

    // Fade out
    const fadeOut = interpolate(frame, [10.5 * fps, 12 * fps], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

    return (
        <AbsoluteFill
            style={{
                background: "#06070d",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                opacity: fadeOut,
            }}
        >
            {/* Glow */}
            <div
                style={{
                    position: "absolute",
                    width: 500,
                    height: 500,
                    borderRadius: "50%",
                    background: "radial-gradient(circle, rgba(124, 58, 237, 0.2) 0%, transparent 70%)",
                    filter: "blur(100px)",
                }}
            />

            {/* Level 5 Badge */}
            <div
                style={{
                    fontFamily: "Inter, sans-serif",
                    fontSize: 18,
                    fontWeight: 700,
                    color: "#7c3aed",
                    textTransform: "uppercase",
                    letterSpacing: 6,
                    opacity: titleOpacity,
                    marginBottom: 10,
                }}
            >
                Level 5 Agentic AI
            </div>

            <div
                style={{
                    fontFamily: "Inter, sans-serif",
                    fontSize: 52,
                    fontWeight: 800,
                    color: "#edf0f8",
                    opacity: levelOpacity,
                    transform: `scale(${levelScale})`,
                    marginBottom: 60,
                    zIndex: 1,
                }}
            >
                What Synapse Can Do
            </div>

            {/* Capability badges */}
            <div style={{ display: "flex", gap: 40, zIndex: 1 }}>
                {capabilities.map((cap, i) => {
                    const badgeDelay = (3 + i * 1.5) * fps;
                    const badgeSpring = spring({
                        frame: Math.max(0, frame - badgeDelay),
                        fps,
                        config: { damping: 12, mass: 0.6 },
                        durationInFrames: Math.round(1.5 * fps),
                    });
                    const badgeOpacity = interpolate(frame, [badgeDelay, badgeDelay + fps], [0, 1], {
                        extrapolateLeft: "clamp",
                        extrapolateRight: "clamp",
                    });

                    return (
                        <div
                            key={i}
                            style={{
                                opacity: badgeOpacity,
                                transform: `scale(${badgeSpring}) translateY(${(1 - badgeSpring) * 40}px)`,
                                background: "rgba(22, 26, 42, 0.85)",
                                border: `2px solid ${cap.color}`,
                                borderRadius: 20,
                                padding: "30px 36px",
                                textAlign: "center",
                                width: 220,
                                boxShadow: `0 0 30px ${cap.color}33`,
                            }}
                        >
                            <div style={{ fontSize: 48, marginBottom: 12 }}>{cap.icon}</div>
                            <div style={{ fontFamily: "Inter, sans-serif", fontSize: 24, fontWeight: 800, color: cap.color }}>{cap.label}</div>
                            <div style={{ fontFamily: "Inter, sans-serif", fontSize: 14, color: "#8892b0", marginTop: 6 }}>{cap.desc}</div>
                        </div>
                    );
                })}
            </div>
        </AbsoluteFill>
    );
};
