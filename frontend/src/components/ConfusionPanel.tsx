import { useCallback, useEffect, useRef, useState } from "react";
import { useReadingSession } from "../hooks/useReadingSession";
import { useWebGazer, type GazePoint } from "../hooks/useWebGazer";
import { CalibrationOverlay } from "./eyeTracking/CalibrationOverlay";

type ConfusionPanelProps = {
  onFixation?: (point: GazePoint) => void;
};

export function ConfusionPanel({ onFixation }: ConfusionPanelProps) {
  const previewCanvasRef = useRef<HTMLCanvasElement>(null);
  const [calibrated, setCalibrated] = useState(false);
  const [gazeTrail, setGazeTrail] = useState<GazePoint[]>([]);
  const handleFixation = useCallback(
    (point: GazePoint) => {
      if (calibrated) {
        setGazeTrail((previousPoints) => [...previousPoints, point]);
      }
      onFixation?.(point);
    },
    [calibrated, onFixation],
  );
  const {
    isReady: isEyeTrackingReady,
    error: eyeTrackingError,
    gazePoint,
    sourceCanvas,
    resetCalibration,
    calibrateAt,
  } = useWebGazer({ onFixation: handleFixation });
  const { confusion, faceBox } = useReadingSession(sourceCanvas);

  const frameSize = {
    width: sourceCanvas?.width ?? 640,
    height: sourceCanvas?.height ?? 480,
  };

  useEffect(() => {
    if (!sourceCanvas || !previewCanvasRef.current) return;

    const preview = previewCanvasRef.current;
    const context = preview.getContext("2d");
    let frameId = 0;

    const drawPreview = () => {
      if (
        preview.width !== sourceCanvas.width ||
        preview.height !== sourceCanvas.height
      ) {
        preview.width = sourceCanvas.width;
        preview.height = sourceCanvas.height;
      }
      context?.drawImage(sourceCanvas, 0, 0, preview.width, preview.height);
      frameId = requestAnimationFrame(drawPreview);
    };

    drawPreview();
    return () => cancelAnimationFrame(frameId);
  }, [sourceCanvas]);

  const restartCalibration = () => {
    void resetCalibration();
    setCalibrated(false);
  };

  return (
    <>
      {!calibrated && isEyeTrackingReady && (
        <CalibrationOverlay
          onCalibrate={calibrateAt}
          onComplete={() => setCalibrated(true)}
          onRestart={restartCalibration}
        />
      )}

      {gazeTrail.map((point, index) => (
        <div
          key={index}
          aria-hidden="true"
          title={`Fixation ${index + 1}`}
          style={{
            position: "fixed",
            left: point.x,
            top: point.y,
            width: "10px",
            height: "10px",
            transform: "translate(-50%, -50%)",
            border: "2px solid #ec4899",
            borderRadius: "50%",
            background: "rgba(236, 72, 153, 0.4)",
            boxShadow: "0 0 7px rgba(236, 72, 153, 0.65)",
            pointerEvents: "none",
            zIndex: 3000,
          }}
        />
      ))}

      <div
        style={{
          position: "fixed",
          top: "0px",
          left: "0px",
          width: "320px",
          padding: "5px",
          background: "white",
          borderRadius: "10px",
          boxShadow: "0 0 10px gray",
          zIndex: 1000,
        }}
      >
        <div style={{ position: "relative", transform: "scaleX(-1)" }}>
          <canvas
            ref={previewCanvasRef}
            style={{ width: "100%", display: "block" }}
          />

          {faceBox && (
            <div
              style={{
                position: "absolute",
                left: `${(faceBox.x / frameSize.width) * 100}%`,
                top: `${(faceBox.y / frameSize.height) * 100}%`,
                width: `${(faceBox.width / frameSize.width) * 100}%`,
                height: `${(faceBox.height / frameSize.height) * 100}%`,
                border: "2px solid red",
              }}
            />
          )}
        </div>

        <p style={{ fontSize: "12px", marginTop: "5px" }}>
          {eyeTrackingError
            ? eyeTrackingError
            : !isEyeTrackingReady
              ? "Starting camera…"
              : confusion > 0.3
                ? "Confused"
                : "Not confused"}
        </p>

        {gazePoint && (
          <p style={{ fontSize: "10px" }}>
            Gaze: {Math.round(gazePoint.x)}, {Math.round(gazePoint.y)}
          </p>
        )}
      </div>
    </>
  );
}
