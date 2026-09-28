// hooks/useWebGazer.ts

import { useCallback, useEffect, useRef, useState } from "react";
import webgazer from "webgazer";

export interface GazePoint {
  x: number;
  y: number;
}

type UseWebGazerOptions = {
  onFixation?: (point: GazePoint) => void;
};

export function useWebGazer(options: UseWebGazerOptions = {}) {
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [gazePoint, setGazePoint] = useState<GazePoint | null>(null);
  const [fixation, setFixation] = useState<GazePoint | null>(null);
  const [sourceCanvas, setSourceCanvas] = useState<HTMLCanvasElement | null>(null);
  const fixationCallbackRef = useRef(options.onFixation);
  const isReadyRef = useRef(false);

  useEffect(() => {
    fixationCallbackRef.current = options.onFixation;
  }, [options.onFixation]);

  const resetCalibration = useCallback(async () => {
    await webgazer.clearData();
    setGazePoint(null);
    setFixation(null);
  }, []);

  /**
   * Adds a labelled gaze target to WebGazer's regression model. Calibration
   * targets call this deliberately instead of allowing ordinary reader clicks
   * and mouse movement to continuously change the model.
   */
  const calibrateAt = useCallback((point: GazePoint) => {
    if (!isReadyRef.current) return;

    webgazer.recordScreenPosition(point.x, point.y, "click");
  }, []);

  useEffect(() => {
    let cancelled = false;
    let engineStarted = false;
    let lastUiUpdate = 0;
    let fixationAnchor: (GazePoint & { startedAt: number }) | null = null;
    let fixationReported = false;

    const start = async () => {
      try {
        // The npm package stores these runtime files in node_modules. Vite does
        // not serve them automatically, so public/ exposes them at this URL.
        // An absolute path also works when the reader route is nested.
        webgazer.params.faceMeshSolutionPath = "/mediapipe/face_mesh";
        webgazer.saveDataAcrossSessions(false);
        await webgazer.setCameraConstraints({
          video: {
            width: { ideal: 640 },
            height: { ideal: 480 },
            facingMode: "user",
          },
        });

        webgazer
          .showVideo(false)
          .showFaceOverlay(false)
          .showFaceFeedbackBox(false)
          .showPredictionPoints(false)
          .setGazeListener((data, elapsedTime) => {
            if (!data || cancelled) return;

            const point = { x: data.x, y: data.y };
            const now = performance.now();

            if (now - lastUiUpdate >= 100) {
              lastUiUpdate = now;
              setGazePoint(point);
            }

            if (!fixationAnchor) {
              fixationAnchor = { ...point, startedAt: elapsedTime };
              fixationReported = false;
              return;
            }

            if (Math.hypot(point.x - fixationAnchor.x, point.y - fixationAnchor.y) > 50) {
              fixationAnchor = { ...point, startedAt: elapsedTime };
              fixationReported = false;
              return;
            }

            if (!fixationReported && elapsedTime - fixationAnchor.startedAt >= 400) {
              fixationReported = true;
              setFixation(point);
              fixationCallbackRef.current?.(point);
            }
          });

        const engine = await webgazer.begin();
        engineStarted = true;

        // begin() installs document-level click and mousemove listeners which
        // otherwise treat every reader interaction as new calibration data.
        // CalibrationOverlay supplies the only training points via calibrateAt.
        engine.removeMouseEventListeners();
        await engine.clearData();
        const canvas = engine.getVideoElementCanvas();

        if (cancelled) {
          engine.stopVideo();
          engine.end();
          return;
        }

        if (!canvas || canvas.width === 0 || canvas.height === 0) {
          throw new Error("WebGazer camera canvas did not become available.");
        }

        setSourceCanvas(canvas);
        isReadyRef.current = true;
        setIsReady(true);
      } catch (startError) {
        if (!cancelled) {
          setError(startError instanceof Error ? startError.message : "Unable to start eye tracking.");
        }
      }
    };

    void start();

    return () => {
      try {
        cancelled = true;
        isReadyRef.current = false;
        webgazer.clearGazeListener();
        webgazer.removeMouseEventListeners();
        if (engineStarted) {
          webgazer.stopVideo();
        }
        webgazer.end();
      } catch {
        // WebGazer may not have created its DOM elements if permission was denied.
      }
    };
  }, []);

  return {
    isReady,
    error,
    gazePoint,
    fixation,
    sourceCanvas,
    resetCalibration,
    calibrateAt,
  };
}
