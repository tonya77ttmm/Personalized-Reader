declare module "webgazer" {
  export type GazeData = { x: number; y: number } | null;

  export interface WebGazer {
    params: {
      faceMeshSolutionPath: string;
    };
    begin(onFail?: () => void): Promise<WebGazer>;
    end(): WebGazer;
    clearData(): Promise<void>;
    clearGazeListener(): WebGazer;
    getVideoElementCanvas(): HTMLCanvasElement | null;
    recordScreenPosition(
      x: number,
      y: number,
      eventType?: "click" | "move",
    ): WebGazer;
    removeMouseEventListeners(): WebGazer;
    saveDataAcrossSessions(save: boolean): WebGazer;
    setCameraConstraints(constraints: MediaStreamConstraints): Promise<void>;
    setGazeListener(
      callback: (data: GazeData, elapsedTime: number) => void,
    ): WebGazer;
    showFaceFeedbackBox(show: boolean): WebGazer;
    showFaceOverlay(show: boolean): WebGazer;
    showPredictionPoints(show: boolean): WebGazer;
    showVideo(show: boolean): WebGazer;
    stopVideo(): WebGazer;
  }

  const webgazer: WebGazer;
  export default webgazer;
}
