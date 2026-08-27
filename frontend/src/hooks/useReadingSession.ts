// hooks/useReadingSession.ts

import { useEffect, useState } from "react";
import { WebSocketService } from "../services/websocket";
import { CameraService } from "../services/camera";

type FaceBox = {
  x: number;
  y: number;
  width: number;
  height: number;
};
export function useReadingSession(videoRef: React.RefObject<HTMLVideoElement>) {
  const [confusion, setConfusion] = useState(0);
  const [faceBox, setFaceBox] = useState<FaceBox | null>(null);
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
      if (message.face_box) {
        setFaceBox(message.face_box);
      } else {
        setFaceBox(null);
      }
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
    faceBox,
  };
}
