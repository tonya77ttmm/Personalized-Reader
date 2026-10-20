import { useState } from "react";
import { type GazePoint } from "../../hooks/useWebGazer";

type CalibrationOverlayProps = {
  onCalibrate: (point: GazePoint) => void;
  onComplete: () => void;
  onRestart: () => void;
};

const CALIBRATION_POINTS = [
  { x: 10, y: 10 }, { x: 50, y: 10 }, { x: 90, y: 10 },
  { x: 10, y: 50 }, { x: 50, y: 50 }, { x: 90, y: 50 },
  { x: 10, y: 90 }, { x: 50, y: 90 }, { x: 90, y: 90 },
];
const CLICKS_PER_POINT = 5;

export function CalibrationOverlay({
  onCalibrate,
  onComplete,
  onRestart,
}: CalibrationOverlayProps) {
  const [pointIndex, setPointIndex] = useState(0);
  const [clickCount, setClickCount] = useState(0);
  const point = CALIBRATION_POINTS[pointIndex];

  const handlePointClick = (point: GazePoint) => {
    onCalibrate(point);
    const nextClickCount = clickCount + 1;

    if (nextClickCount < CLICKS_PER_POINT) {
      setClickCount(nextClickCount);
    } else if (pointIndex === CALIBRATION_POINTS.length - 1) {
      onComplete();
    } else {
      setPointIndex((current) => current + 1);
      setClickCount(0);
    }
  };

  const restart = () => {
    onRestart();
    setPointIndex(0);
    setClickCount(0);
  };

  return (
    <div className="fixed inset-0 z-[2000] bg-slate-950/90 text-white" aria-live="polite">
      <div className="absolute left-1/2 top-8 -translate-x-1/2 text-center">
        <h2 className="text-xl font-semibold">Calibrate eye tracking</h2>
        <p className="mt-2 text-sm text-slate-200">
          Look directly at the blue dot, then click it {CLICKS_PER_POINT} times.
        </p>
        <p className="mt-1 text-xs text-slate-400">
          Point {pointIndex + 1} of {CALIBRATION_POINTS.length} · Click {clickCount + 1} of {CLICKS_PER_POINT}
        </p>
        <button type="button" onClick={restart} className="mt-3 text-xs text-blue-300 underline">
          Restart calibration
        </button>
      </div>
      <button
        type="button"
        onClick={(event) =>
          handlePointClick({ x: event.clientX, y: event.clientY })
        }
        aria-label={`Calibration point ${pointIndex + 1}`}
        className="absolute h-12 w-12 rounded-full bg-blue-500 shadow-lg shadow-blue-400/50 transition-transform hover:scale-110 focus:outline-none focus:ring-4 focus:ring-blue-200"
        style={{ left: `${point.x}%`, top: `${point.y}%`, transform: "translate(-50%, -50%)" }}
      />
    </div>
  );
}
