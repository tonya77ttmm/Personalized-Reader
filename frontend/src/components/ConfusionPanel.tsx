import { useReadingSession } from "../hooks/useReadingSession";
import { useRef } from "react";

export function ConfusionPanel() {
  //
  const videoRef = useRef<HTMLVideoElement>(null);
  const { confusion } = useReadingSession(videoRef);
  return (
    <div
      style={{
        position: "fixed",

        top: "0px",

        left: "0px",

        width: "150px",

        padding: "5px",

        background: "white",

        borderRadius: "10px",

        boxShadow: "0 0 10px gray",

        zIndex: 1000,
      }}
    >
      <video ref={videoRef} autoPlay muted />

      <p style={{ fontSize: "10px", marginTop: "5px" }}>
        Confusion:
        {confusion}
      </p>
    </div>
  );
}
