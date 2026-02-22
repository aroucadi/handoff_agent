import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";

export const IntroScene: React.FC = () => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();

    // Logo scale spring
    const logoScale = spring({ frame, fps, config: { damping: 12, mass: 0.8 }, durationInFrames: 2 * fps });

    // Tagline fade
    const taglineOpacity = interpolate(frame, [2 * fps, 3 * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const taglineY = interpolate(frame, [2 * fps, 3 * fps], [20, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

    // Glow pulse
    const glowOpacity = interpolate(frame, [0, 3 * fps, 6 * fps], [0, 0.6, 0.3], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

    // Particle nodes (static dots that fade in)
    const particles = Array.from({ length: 30 }, (_, i) => ({
        x: (i * 137.5) % 1920,
        y: (i * 73.3) % 1080,
        delay: (i * 0.1) % 3,
        size: 3 + (i % 4),
    }));

    // Fade out at the end
    const fadeOut = interpolate(frame, [8.5 * fps, 10 * fps], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

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
            {/* Glow backdrop */}
            <div
                style={{
                    position: "absolute",
                    width: 600,
                    height: 600,
                    borderRadius: "50%",
                    background: "radial-gradient(circle, rgba(124, 58, 237, 0.4) 0%, transparent 70%)",
                    filter: "blur(80px)",
                    opacity: glowOpacity,
                }}
            />

            {/* Particles */}
            {particles.map((p, i) => {
                const pOpacity = interpolate(frame, [p.delay * fps, (p.delay + 1) * fps], [0, 0.5], {
                    extrapolateLeft: "clamp",
                    extrapolateRight: "clamp",
                });
                return (
                    <div
                        key={i}
                        style={{
                            position: "absolute",
                            left: p.x,
                            top: p.y,
                            width: p.size,
                            height: p.size,
                            borderRadius: "50%",
                            background: i % 2 === 0 ? "#7c3aed" : "#38bdf8",
                            opacity: pOpacity,
                        }}
                    />
                );
            })}

            {/* Logo */}
            <div
                style={{
                    fontFamily: "Inter, sans-serif",
                    fontSize: 120,
                    fontWeight: 800,
                    letterSpacing: -3,
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
                    fontSize: 28,
                    color: "#8892b0",
                    marginTop: 20,
                    opacity: taglineOpacity,
                    transform: `translateY(${taglineY}px)`,
                    letterSpacing: 4,
                    textTransform: "uppercase",
                    zIndex: 1,
                }}
            >
                The living memory of your customer journey
            </div>
        </AbsoluteFill>
    );
};
