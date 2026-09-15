// components/CalibrationOverlay.tsx

import React, { useState } from "react";

interface CalibrationOverlayProps {
  onComplete: () => void;
}

const TARGET_POINTS = [
  { id: 1, top: "10%", left: "10%" },
  { id: 2, top: "10%", left: "50%" },
  { id: 3, top: "10%", left: "90%" },
  { id: 4, top: "50%", left: "10%" },
  { id: 5, top: "50%", left: "50%" },
  { id: 6, top: "50%", left: "90%" },
  { id: 7, top: "90%", left: "10%" },
  { id: 8, top: "90%", left: "50%" },
  { id: 9, top: "90%", left: "90%" },
];

const CLICKS_PER_POINT = 5;

export const CalibrationOverlay: React.FC<CalibrationOverlayProps> = ({
  onComplete,
}) => {
  const [clickCounts, setClickCounts] = useState<Record<number, number>>({});

  const handlePointClick = (id: number) => {
    const currentClicks = (clickCounts[id] || 0) + 1;
    const updated = { ...clickCounts, [id]: currentClicks };
    setClickCounts(updated);

    const allCompleted = TARGET_POINTS.every(
      (pt) => (updated[pt.id] || 0) >= CLICKS_PER_POINT,
    );
    if (allCompleted) {
      onComplete();
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(0,0,0,0.7)",
        zIndex: 9999,
        pointerEvents: "auto",
      }}
    >
      <div style={{ color: "white", textAlign: "center", paddingTop: "20px" }}>
        <h3>Gaze Calibration</h3>
        <p>Focus your eyes on each red point and click it 5 times.</p>
      </div>

      {TARGET_POINTS.map((pt) => {
        const count = clickCounts[pt.id] || 0;
        const isDone = count >= CLICKS_PER_POINT;

        return (
          <button
            key={pt.id}
            onClick={() => handlePointClick(pt.id)}
            disabled={isDone}
            style={{
              position: "absolute",
              top: pt.top,
              left: pt.left,
              transform: "translate(-50%, -50%)",
              width: "32px",
              height: "32px",
              borderRadius: "50%",
              backgroundColor: isDone ? "#4CAF50" : "#FF5252",
              border: "2px solid white",
              color: "white",
              fontSize: "12px",
              cursor: isDone ? "default" : "pointer",
            }}
          >
            {count}
          </button>
        );
      })}
    </div>
  );
};
