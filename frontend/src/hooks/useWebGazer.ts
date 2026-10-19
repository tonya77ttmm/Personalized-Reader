// hooks/useWebGazer.ts

import { useCallback, useEffect, useRef, useState } from "react";
import webgazer from "webgazer";

export interface GazePoint {
  x: number;
  y: number;
}

type FaceLandmark = readonly [number, number, number];
type EyeTrackingState = "open" | "closed" | "unavailable";
type EyePatches = {
  left?: { patch?: ImageData };
  right?: { patch?: ImageData };
};

type BlinkDetectorState = {
  baselineEar: number | null;
  earWarmupSamples: number;
  leftBrightnessSamples: number[];
  rightBrightnessSamples: number[];
  closedFrames: number;
  openFrames: number;
  isBlinking: boolean;
};

type UseWebGazerOptions = {
  onFixation?: (point: GazePoint) => void;
};

// MediaPipe FaceMesh landmark indices. Each group is ordered as:
// outer corner, two upper-lid points, inner corner, two lower-lid points.
const LEFT_EYE = [362, 385, 387, 263, 373, 380] as const;
const RIGHT_EYE = [33, 160, 158, 133, 153, 144] as const;

const EYE_CLOSED_RATIO = 0.78;
// WebGazer's FaceMesh loop can be slower than the camera. A short blink may
// only appear in one analysed frame, so hide the gaze immediately on it.
const FRAMES_TO_CONFIRM_CLOSED_EYES = 1;
const FRAMES_TO_CONFIRM_OPEN_EYES = 2;
const EAR_BASELINE_WARMUP_SAMPLES = 20;
const BRIGHTNESS_BASELINE_SAMPLE_SIZE = 12;
const BRIGHTNESS_CHANGE_RATIO = 0.2;

function createBlinkDetectorState(): BlinkDetectorState {
  return {
    baselineEar: null,
    earWarmupSamples: 0,
    leftBrightnessSamples: [],
    rightBrightnessSamples: [],
    closedFrames: 0,
    openFrames: 0,
    isBlinking: false,
  };
}

function distance(first: FaceLandmark, second: FaceLandmark) {
  return Math.hypot(first[0] - second[0], first[1] - second[1]);
}

/**
 * EAR (Eye Aspect Ratio) is the eye's vertical opening divided by its width.
 * It falls sharply when an eye closes, while remaining fairly stable when the
 * user's face moves closer to or farther from the camera.
 */
function calculateEyeAspectRatio(
  landmarks: readonly FaceLandmark[],
  indices: readonly number[],
) {
  const points = indices.map((index) => landmarks[index]);
  if (points.some((point) => !point)) return null;

  const [outer, upperOne, upperTwo, inner, lowerOne, lowerTwo] =
    points as FaceLandmark[];
  const eyeWidth = distance(outer, inner);
  if (eyeWidth === 0) return null;

  return (
    (distance(upperOne, lowerTwo) + distance(upperTwo, lowerOne)) /
    (2 * eyeWidth)
  );
}

function getEarBlinkSignal(
  landmarks: readonly FaceLandmark[] | null,
  detector: BlinkDetectorState,
): boolean | null {
  if (!landmarks) return null;

  const leftEar = calculateEyeAspectRatio(landmarks, LEFT_EYE);
  const rightEar = calculateEyeAspectRatio(landmarks, RIGHT_EYE);
  if (leftEar === null || rightEar === null) return null;

  // Use the smaller eye value: if either eye is closed or occluded, the gaze
  // prediction is not reliable enough to display or record as a fixation.
  const currentEar = Math.min(leftEar, rightEar);

  // During the first frames we learn this user's normal open-eye EAR. The
  // largest value avoids accidentally treating a first-frame blink as normal.
  if (detector.earWarmupSamples < EAR_BASELINE_WARMUP_SAMPLES) {
    detector.baselineEar = Math.max(detector.baselineEar ?? 0, currentEar);
    detector.earWarmupSamples += 1;
    return false;
  }

  const baselineEar = detector.baselineEar;
  if (baselineEar === null || baselineEar === 0) return null;

  const eyesLookClosed = currentEar < baselineEar * EYE_CLOSED_RATIO;
  // Adapt gently to ordinary changes in face angle without allowing a
  // partially closed eye to lower the user's normal-open-eye baseline.
  if (!eyesLookClosed && currentEar >= baselineEar * 0.85) {
    detector.baselineEar = baselineEar * 0.95 + currentEar * 0.05;
  }

  return eyesLookClosed;
}

function calculatePatchBrightness(patch: ImageData) {
  let total = 0;
  let sampleCount = 0;

  // Sample every fourth pixel. The patches are small, but this avoids doing
  // unnecessary work in a callback that runs for every WebGazer prediction.
  for (let index = 0; index < patch.data.length; index += 16) {
    total +=
      (patch.data[index] + patch.data[index + 1] + patch.data[index + 2]) / 3;
    sampleCount += 1;
  }

  return sampleCount === 0 ? null : total / sampleCount;
}

function calculateEyePatchBrightness(
  eyePatches: EyePatches | null | undefined,
) {
  const leftPatch = eyePatches?.left?.patch;
  const rightPatch = eyePatches?.right?.patch;
  if (!leftPatch || !rightPatch) return null;

  const left = calculatePatchBrightness(leftPatch);
  const right = calculatePatchBrightness(rightPatch);
  if (left === null || right === null) return null;

  return { left, right };
}

function pushBrightnessSample(samples: number[], value: number) {
  samples.push(value);
  if (samples.length > BRIGHTNESS_BASELINE_SAMPLE_SIZE) {
    samples.shift();
  }
}

function average(values: readonly number[]) {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

/**
 * A closed eyelid changes both eye patches at once. This is a second signal
 * for cases where FaceMesh eyelid landmarks do not move enough for EAR alone.
 * A sliding baseline lets the detector adapt to gradual lighting changes.
 */
function getBrightnessBlinkSignal(
  eyePatches: EyePatches | null | undefined,
  detector: BlinkDetectorState,
): boolean | null {
  const brightness = calculateEyePatchBrightness(eyePatches);
  if (!brightness) return null;

  const leftSamples = detector.leftBrightnessSamples;
  const rightSamples = detector.rightBrightnessSamples;
  if (
    leftSamples.length < BRIGHTNESS_BASELINE_SAMPLE_SIZE ||
    rightSamples.length < BRIGHTNESS_BASELINE_SAMPLE_SIZE
  ) {
    pushBrightnessSample(leftSamples, brightness.left);
    pushBrightnessSample(rightSamples, brightness.right);
    return false;
  }

  const leftBaseline = average(leftSamples);
  const rightBaseline = average(rightSamples);
  const leftChange = (brightness.left - leftBaseline) / leftBaseline;
  const rightChange = (brightness.right - rightBaseline) / rightBaseline;
  const bothPatchesChangedInTheSameDirection =
    (leftChange >= BRIGHTNESS_CHANGE_RATIO &&
      rightChange >= BRIGHTNESS_CHANGE_RATIO) ||
    (leftChange <= -BRIGHTNESS_CHANGE_RATIO &&
      rightChange <= -BRIGHTNESS_CHANGE_RATIO);

  // Keep the same rolling-average behaviour as the referenced brightness
  // approach, so the threshold also catches up after a sustained lighting
  // change instead of leaving tracking paused forever.
  pushBrightnessSample(leftSamples, brightness.left);
  pushBrightnessSample(rightSamples, brightness.right);

  return bothPatchesChangedInTheSameDirection;
}

function getEyeTrackingState(
  landmarks: readonly FaceLandmark[] | null,
  eyePatches: EyePatches | null | undefined,
  detector: BlinkDetectorState,
): EyeTrackingState {
  const earBlinkSignal = getEarBlinkSignal(landmarks, detector);
  const brightnessBlinkSignal = getBrightnessBlinkSignal(eyePatches, detector);
  if (earBlinkSignal === null && brightnessBlinkSignal === null) {
    return "unavailable";
  }

  const eyesLookClosed =
    earBlinkSignal === true || brightnessBlinkSignal === true;
  if (eyesLookClosed) {
    detector.closedFrames += 1;
    detector.openFrames = 0;
    if (detector.closedFrames >= FRAMES_TO_CONFIRM_CLOSED_EYES) {
      detector.isBlinking = true;
    }
  } else {
    detector.closedFrames = 0;
    if (detector.isBlinking) {
      detector.openFrames += 1;
      if (detector.openFrames >= FRAMES_TO_CONFIRM_OPEN_EYES) {
        detector.isBlinking = false;
        detector.openFrames = 0;
      }
    } else {
      detector.openFrames = 0;
    }
  }

  return detector.isBlinking ? "closed" : "open";
}

export function useWebGazer(options: UseWebGazerOptions = {}) {
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [gazePoint, setGazePoint] = useState<GazePoint | null>(null);
  const [fixation, setFixation] = useState<GazePoint | null>(null);
  const [isBlinking, setIsBlinking] = useState(false);
  const [sourceCanvas, setSourceCanvas] = useState<HTMLCanvasElement | null>(
    null,
  );
  const fixationCallbackRef = useRef(options.onFixation);
  const isReadyRef = useRef(false);
  const blinkDetectorRef = useRef<BlinkDetectorState>(
    createBlinkDetectorState(),
  );

  useEffect(() => {
    fixationCallbackRef.current = options.onFixation;
  }, [options.onFixation]);

  const resetCalibration = useCallback(async () => {
    await webgazer.clearData();
    blinkDetectorRef.current = createBlinkDetectorState();
    setGazePoint(null);
    setFixation(null);
    setIsBlinking(false);
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

    const clearDisplayedTracking = () => {
      fixationAnchor = null;
      fixationReported = false;
      setGazePoint(null);
      setFixation(null);
    };

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
            if (cancelled) return;

            let eyeTrackingState: EyeTrackingState;
            try {
              const landmarks = webgazer.getTracker().getPositions();
              eyeTrackingState = getEyeTrackingState(
                landmarks,
                data?.eyeFeatures,
                blinkDetectorRef.current,
              );
            } catch {
              eyeTrackingState = "unavailable";
            }

            if (eyeTrackingState === "closed") {
              setIsBlinking(true);
              clearDisplayedTracking();
              return;
            }

            if (eyeTrackingState === "unavailable" || !data) {
              setIsBlinking(false);
              clearDisplayedTracking();
              return;
            }

            setIsBlinking(false);

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

            if (
              Math.hypot(
                point.x - fixationAnchor.x,
                point.y - fixationAnchor.y,
              ) > 200
            ) {
              fixationAnchor = { ...point, startedAt: elapsedTime };
              fixationReported = false;
              setFixation(null);
              return;
            }

            if (
              !fixationReported &&
              elapsedTime - fixationAnchor.startedAt >= 200
            ) {
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
          setError(
            startError instanceof Error
              ? startError.message
              : "Unable to start eye tracking.",
          );
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
    isBlinking,
    sourceCanvas,
    resetCalibration,
    calibrateAt,
  };
}
