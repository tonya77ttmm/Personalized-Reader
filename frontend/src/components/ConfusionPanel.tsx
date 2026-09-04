import { useReadingSession } from "../hooks/useReadingSession";
import { useRef } from "react";

export function ConfusionPanel() {
  //
  const videoRef = useRef<HTMLVideoElement>(null);
  const { confusion, faceBox } = useReadingSession(videoRef);
  return (
    <div
      style={{
        position: "fixed",

        top: "0px",

        left: "0px",

        width: "640px",

        height: "480px",

        padding: "5px",

        background: "white",

        borderRadius: "10px",

        boxShadow: "0 0 10px gray",

        zIndex: 1000,
      }}
    >
      <div style={{ position: "relative" }}>
        <video
          ref={videoRef}
          autoPlay
          muted
          style={{
            width: "100%",
          }}
        />

        {faceBox && (
          <div
            style={{
              position: "absolute",

              left: faceBox.x,

              top: faceBox.y,

              width: faceBox.width,

              height: faceBox.height,

              border: "2px solid red",
            }}
          />
        )}
      </div>
      <p style={{ fontSize: "10px", marginTop: "5px" }}></p>
      {confusion > 0.4 ? "Confused" : "Not Confused"}
      {confusion}
    </div>
  );
}
