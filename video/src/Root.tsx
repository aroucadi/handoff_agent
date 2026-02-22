import { Composition } from "remotion";
import { SynapseBrandVideo } from "./SynapseBrandVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="SynapseBrandVideo"
        component={SynapseBrandVideo}
        durationInFrames={1800}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
