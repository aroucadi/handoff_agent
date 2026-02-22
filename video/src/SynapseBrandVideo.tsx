import { AbsoluteFill, Series } from "remotion";
import { ProblemScene } from "./scenes/ProblemScene";
import { IntroScene } from "./scenes/IntroScene";
import { HowItWorksScene } from "./scenes/HowItWorksScene";
import { CapabilitiesScene } from "./scenes/CapabilitiesScene";
import { CTAScene } from "./scenes/CTAScene";

/**
 * Synapse — Brand Video (60s @ 30fps = 1800 frames)
 *
 * 5-scene cinematic showcase of the Synapse Level 5 Multimodal Agent.
 */
export const SynapseBrandVideo: React.FC = () => {
    return (
        <AbsoluteFill style={{ background: "#06070d" }}>
            <Series>
                <Series.Sequence durationInFrames={360}>
                    <ProblemScene />
                </Series.Sequence>
                <Series.Sequence durationInFrames={300}>
                    <IntroScene />
                </Series.Sequence>
                <Series.Sequence durationInFrames={540}>
                    <HowItWorksScene />
                </Series.Sequence>
                <Series.Sequence durationInFrames={360}>
                    <CapabilitiesScene />
                </Series.Sequence>
                <Series.Sequence durationInFrames={240}>
                    <CTAScene />
                </Series.Sequence>
            </Series>
        </AbsoluteFill>
    );
};
