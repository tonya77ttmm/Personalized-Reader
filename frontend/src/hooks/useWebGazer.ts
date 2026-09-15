// hooks/useWebGazer.ts

import { useEffect, useRef, useState, useCallback } from "react";
// Import WebGazer directly from the npm package
import webgazer from "webgazer";

interface GazePoint {
  x: number;
  y: number;
}

export function useWebGazer() {
  const [isReady, setIsReady] = useState(false);
  const [isCalibrated, setIsCalibrated] = useState(false);
  const [gazePoint, setGazePoint] = useState<GazePoint | null>(null);
  const [fixatedElement, setFixatedElement] = useState<Element | null>(null);
  const [videoElement, setVideoElement] = useState<HTMLVideoElement | null>(
    null,
  );

  // Rolling window buffer for fixation detection
  const samplesRef = useRef<{ x: number; y: number; timestamp: number }[]>([]);

  // Calculate fixations (300-500ms continuous gaze within ~50px radius)
  const processFixation = useCallback((x: number, y: number) => {
    const now = Date.now();
    const windowMs = 400;
    const distanceThresholdPx = 50;

    samplesRef.current.push({ x, y, timestamp: now });
    samplesRef.current = samplesRef.current.filter(
      (s) => now - s.timestamp <= windowMs,
    );

    if (samplesRef.current.length < 5) return;
    const oldestSample = samplesRef.current[0];
    if (now - oldestSample.timestamp < windowMs * 0.8) return;

    const avgX =
      samplesRef.current.reduce((sum, s) => sum + s.x, 0) /
      samplesRef.current.length;
    const avgY =
      samplesRef.current.reduce((sum, s) => sum + s.y, 0) /
      samplesRef.current.length;

    let maxDist = 0;
    for (const sample of samplesRef.current) {
      const dist = Math.hypot(sample.x - avgX, sample.y - avgY);
      if (dist > maxDist) maxDist = dist;
    }

    if (maxDist <= distanceThresholdPx) {
      const targetEl = document.elementFromPoint(avgX, avgY);
      if (targetEl) {
        setFixatedElement(targetEl);
      }
    }
  }, []);

  useEffect(() => {
    // Clear old saved calibration data
    webgazer.clearData();

    // Configure camera constraints
    webgazer.setParams({
      videoViewerWidth: 640,
      videoViewerHeight: 480,
    });

    // Set callback listener for gaze predictions
    webgazer.setGazeListener((data: { x: number; y: number } | null) => {
      if (!data) return;
      setGazePoint({ x: data.x, y: data.y });
      processFixation(data.x, data.y);
    });

    // Request camera access and begin tracking
    webgazer
      .begin()
      .then(() => {
        console.log("WebGazer initialized and camera active.");
        webgazer.showVideoPreview(true);
        webgazer.showPredictionPoints(true);
      })
      .catch((err: unknown) => {
        console.error("Failed to start WebGazer camera feed:", err);
      });

    // Poll until WebGazer injects and starts playing its HTMLVideoElement
    const checkVideoElement = setInterval(() => {
      const videoEl = document.getElementById(
        "webgazerVideoFeed",
      ) as HTMLVideoElement;
      if (videoEl && videoEl.readyState >= 2) {
        setVideoElement(videoEl);
        setIsReady(true);
        clearInterval(checkVideoElement);
      }
    }, 200);

    return () => {
      clearInterval(checkVideoElement);
      try {
        webgazer.end();
      } catch (err) {
        console.warn("WebGazer cleanup error:", err);
      }
    };
  }, [processFixation]);

  const finishCalibration = useCallback(() => {
    setIsCalibrated(true);
    webgazer.showVideoPreview(false);
    webgazer.showFaceOverlay(false);
    webgazer.showFaceFeedbackBox(false);
    webgazer.showPredictionPoints(false);
  }, []);

  return {
    isReady,
    isCalibrated,
    gazePoint,
    fixatedElement,
    videoElement,
    finishCalibration,
  };
}
