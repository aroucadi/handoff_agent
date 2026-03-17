import { useRef, useEffect, useState } from 'react';
import hls from 'hls.js';

interface BackgroundVideoProps {
    src: string;
    poster?: string;
}

export default function BackgroundVideo({ src, poster }: BackgroundVideoProps) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const [isLoaded, setIsLoaded] = useState(false);

    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        if (src.endsWith('.m3u8')) {
            if (hls.isSupported()) {
                const hlsInstance = new hls();
                hlsInstance.loadSource(src);
                hlsInstance.attachMedia(video);
                hlsInstance.on(hls.Events.MANIFEST_PARSED, () => {
                    video.play().catch(e => console.error("HLS Autoplay failed:", e));
                });
                return () => {
                    hlsInstance.destroy();
                };
            } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                video.src = src;
            }
        } else {
            video.src = src;
        }
    }, [src]);

    return (
        <div className="fixed inset-0 w-full h-full overflow-hidden bg-black -z-10 pointer-events-none">
            <div className="absolute inset-0 flex items-center justify-center">
                <video
                    ref={videoRef}
                    autoPlay
                    loop
                    muted
                    playsInline
                    poster={poster}
                    onLoadedData={() => setIsLoaded(true)}
                    className={`
                        w-[120%] h-[120%] object-cover object-bottom transition-opacity duration-1000
                        ${isLoaded ? 'opacity-100' : 'opacity-0'}
                    `}
                />
            </div>
            <div 
                className="absolute left-1/2 -translate-x-1/2 top-[215px] w-[801px] h-[384px] bg-black rounded-full mix-blend-normal z-[1]" 
                style={{ filter: 'blur(77.5px)' }} 
            />
            <div className="absolute inset-0 bg-black/40 z-[1]" />
        </div>
    );
}
