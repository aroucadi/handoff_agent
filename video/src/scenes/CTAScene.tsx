import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";

export const CTAScene: React.FC = () => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();

    // Logo
    const logoScale = spring({ frame, fps, config: { damping: 15, mass: 0.8 }, durationInFrames: Math.round(1.5 * fps) });

    // Tagline
    const tagOpacity = interpolate(frame, [1.5 * fps, 2.5 * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

    // Hackathon badge
    const badgeOpacity = interpolate(frame, [3 * fps, 4 * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const badgeY = interpolate(frame, [3 * fps, 4 * fps], [20, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

    return (
        <AbsoluteFill
            style={{
                background: "#06070d",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
            }}
        >
            {/* Glow */}
            <div
                style={{
                    position: "absolute",
                    width: 700,
                    height: 700,
                    borderRadius: "50%",
                    background: "radial-gradient(circle, rgba(124, 58, 237, 0.3) 0%, transparent 70%)",
                    filter: "blur(100px)",
                }}
            />

            {/* Logo */}
            <div
                style={{
                    fontFamily: "Inter, sans-serif",
                    fontSize: 100,
                    fontWeight: 800,
                    letterSpacing: -2,
                    background: "linear-gradient(135deg, #a78bfa, #38bdf8)",
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                    transform: `scale(${logoScale})`,
                    zIndex: 1,
                }}
            >
                Synapse
            </div>

            {/* Tagline */}
            <div
                style={{
                    fontFamily: "Inter, sans-serif",
                    fontSize: 24,
                    color: "#8892b0",
                    marginTop: 16,
                    opacity: tagOpacity,
                    letterSpacing: 3,
                    textTransform: "uppercase",
                    zIndex: 1,
                }}
            >
                The living memory of your customer journey
            </div>

            {/* Hackathon badge */}
            <div
                style={{
                    marginTop: 60,
                    opacity: badgeOpacity,
                    transform: `translateY(${badgeY}px)`,
                    background: "rgba(22, 26, 42, 0.75)",
                    border: "1px solid #7c3aed",
                    borderRadius: 14,
                    padding: "16px 40px",
                    zIndex: 1,
                }}
            >
                <div style={{ fontFamily: "Inter, sans-serif", fontSize: 18, fontWeight: 600, color: "#edf0f8", textAlign: "center" }}>
                    Built for the <span style={{ color: "#38bdf8" }}>Gemini Live Agent Challenge</span>
                </div>
            </div>
        </AbsoluteFill>
    );
};
