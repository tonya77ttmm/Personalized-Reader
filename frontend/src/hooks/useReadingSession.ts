// hooks/useReadingSession.ts

import { useEffect, useState } from "react";
import { WebSocketService } from "../services/websocket";
import { CameraService } from "../services/camera";

export function useReadingSession(videoRef: React.RefObject<HTMLVideoElement>) {
  const [confusion, setConfusion] = useState(0);
  useEffect(() => {
    if (!videoRef.current) {
      return;
    }
    // create websocket service
    const websocket = new WebSocketService();
    const camera = new CameraService();
    // connect to the websocket server
    websocket.connect((message) => {
      console.log("Message from backend:", message);
      setConfusion(message.confusion_prob);
    });
    // 2. open camera

    camera.start(videoRef.current, (frame) => {
      websocket.send(frame);
    });

    // cleanup
    return () => {
      camera.stop();
      websocket.disconnect();
    };
  }, [videoRef]);

  return {
    confusion,
  };
}
