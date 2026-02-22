import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from "remotion";

export const ProblemScene: React.FC = () => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();

    // Typewriter for the main statement
    const fullText = "When a deal closes, 80% of customer knowledge is lost.";
    const charsShown = Math.min(
        Math.floor(interpolate(frame, [0, 3 * fps], [0, fullText.length], { extrapolateRight: "clamp" })),
        fullText.length
    );
    const displayedText = fullText.slice(0, charsShown);

    // Stats fade in after the text
    const statOpacity = interpolate(frame, [4 * fps, 5 * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const statY = interpolate(frame, [4 * fps, 5 * fps], [30, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

    // Second line
    const secondLine = "The result? Bad onboarding. Slow time-to-value. Churn.";
    const secondStart = 7 * fps;
    const secondChars = Math.min(
        Math.floor(interpolate(frame, [secondStart, secondStart + 2.5 * fps], [0, secondLine.length], { extrapolateRight: "clamp", extrapolateLeft: "clamp" })),
        secondLine.length
    );
    const displayedSecond = frame >= secondStart ? secondLine.slice(0, secondChars) : "";

    // Fade out
    const fadeOut = interpolate(frame, [10.5 * fps, 12 * fps], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

    return (
        <AbsoluteFill
            style={{
                background: "linear-gradient(180deg, #06070d 0%, #0a0c14 100%)",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                padding: 80,
                opacity: fadeOut,
            }}
        >
            <div
                style={{
                    fontFamily: "Inter, sans-serif",
                    fontSize: 52,
                    fontWeight: 700,
                    color: "#edf0f8",
                    textAlign: "center",
                    lineHeight: 1.4,
                    maxWidth: 1200,
                    minHeight: 160,
                }}
            >
                {displayedText}
                <span style={{ opacity: frame % fps < fps / 2 ? 1 : 0, color: "#7c3aed" }}>|</span>
            </div>

            <div
                style={{
                    marginTop: 60,
                    display: "flex",
                    gap: 60,
                    opacity: statOpacity,
                    transform: `translateY(${statY}px)`,
                }}
            >
                {["$2M Deal", "48 Hours", "1 CSM"].map((stat, i) => (
                    <div
                        key={i}
                        style={{
                            textAlign: "center",
                            padding: "20px 40px",
                            borderRadius: 14,
                            border: "1px solid #252a40",
                            background: "rgba(22, 26, 42, 0.75)",
                        }}
                    >
                        <div style={{ fontFamily: "Inter, sans-serif", fontSize: 36, fontWeight: 800, color: "#a78bfa" }}>{stat}</div>
                    </div>
                ))}
            </div>

            <div
                style={{
                    fontFamily: "Inter, sans-serif",
                    fontSize: 32,
                    color: "#f43f5e",
                    textAlign: "center",
                    marginTop: 50,
                    fontWeight: 600,
                    minHeight: 50,
                }}
            >
                {displayedSecond}
            </div>
        </AbsoluteFill>
    );
};
