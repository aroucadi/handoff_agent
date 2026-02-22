import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";

const steps = [
    { icon: "📊", title: "Deal Closes", desc: "CRM webhook fires automatically" },
    { icon: "🧠", title: "Graph Generates", desc: "Gemini 3.1 Pro extracts knowledge into a skill graph" },
    { icon: "🎙️", title: "CSM Talks", desc: "Multimodal Live Agent briefs you with voice + vision" },
];

export const HowItWorksScene: React.FC = () => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();

    // Title
    const titleOpacity = interpolate(frame, [0, 1 * fps], [0, 1], { extrapolateRight: "clamp" });

    // Fade out
    const fadeOut = interpolate(frame, [16 * fps, 18 * fps], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

    return (
        <AbsoluteFill
            style={{
                background: "linear-gradient(180deg, #06070d 0%, #10131e 100%)",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                padding: 80,
                opacity: fadeOut,
            }}
        >
            {/* Section title */}
            <div
                style={{
                    fontFamily: "Inter, sans-serif",
                    fontSize: 22,
                    fontWeight: 600,
                    color: "#7c3aed",
                    textTransform: "uppercase",
                    letterSpacing: 6,
                    opacity: titleOpacity,
                    marginBottom: 60,
                }}
            >
                How It Works
            </div>

            {/* 3 steps */}
            <div style={{ display: "flex", gap: 60, alignItems: "flex-start" }}>
                {steps.map((step, i) => {
                    const stepDelay = (2 + i * 4) * fps;
                    const slideX = interpolate(frame, [stepDelay, stepDelay + 1.5 * fps], [-200, 0], {
                        extrapolateLeft: "clamp",
                        extrapolateRight: "clamp",
                    });
                    const stepOpacity = interpolate(frame, [stepDelay, stepDelay + 1.5 * fps], [0, 1], {
                        extrapolateLeft: "clamp",
                        extrapolateRight: "clamp",
                    });
                    const lineScale = spring({
                        frame: Math.max(0, frame - stepDelay - fps),
                        fps,
                        config: { damping: 15 },
                        durationInFrames: fps,
                    });

                    return (
                        <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 20 }}>
                            {/* Card */}
                            <div
                                style={{
                                    opacity: stepOpacity,
                                    transform: `translateX(${slideX}px)`,
                                    background: "rgba(22, 26, 42, 0.75)",
                                    border: "1px solid #252a40",
                                    borderRadius: 20,
                                    padding: "40px 50px",
                                    textAlign: "center",
                                    width: 360,
                                }}
                            >
                                <div style={{ fontSize: 64, marginBottom: 16 }}>{step.icon}</div>
                                <div
                                    style={{
                                        fontFamily: "Inter, sans-serif",
                                        fontSize: 28,
                                        fontWeight: 700,
                                        color: "#edf0f8",
                                        marginBottom: 10,
                                    }}
                                >
                                    {step.title}
                                </div>
                                <div style={{ fontFamily: "Inter, sans-serif", fontSize: 18, color: "#8892b0", lineHeight: 1.5 }}>
                                    {step.desc}
                                </div>
                            </div>

                            {/* Step number */}
                            <div
                                style={{
                                    width: 40,
                                    height: 40,
                                    borderRadius: "50%",
                                    background: "#7c3aed",
                                    display: "flex",
                                    justifyContent: "center",
                                    alignItems: "center",
                                    fontFamily: "Inter, sans-serif",
                                    fontWeight: 800,
                                    color: "white",
                                    fontSize: 18,
                                    opacity: stepOpacity,
                                    transform: `scale(${lineScale})`,
                                }}
                            >
                                {i + 1}
                            </div>
                        </div>
                    );
                })}
            </div>
        </AbsoluteFill>
    );
};
