import { useEffect, useState } from "react";
import { WebSocketService } from "../services/websocket";
import { CameraService } from "../services/camera";

type FaceBox = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export function useReadingSession(sourceCanvas: HTMLCanvasElement | null) {
  const [confusion, setConfusion] = useState(0);
  const [faceBox, setFaceBox] = useState<FaceBox | null>(null);

  useEffect(() => {
    if (!sourceCanvas) return;

    const websocket = new WebSocketService();
    const framePublisher = new CameraService();

    websocket.connect((message) => {
      setConfusion(message.confusion_prob);
      setFaceBox(message.face_box ?? null);
    });

    framePublisher.start(sourceCanvas, (frame) => websocket.send(frame));

    return () => {
      framePublisher.stop();
      websocket.disconnect();
    };
  }, [sourceCanvas]);

  return {
    confusion,
    faceBox,
  };
}
