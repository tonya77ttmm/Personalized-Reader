export class CameraService {
  private captureTimer: number | null = null;

  /**
   * Publishes frames from WebGazer's camera canvas. WebGazer is deliberately
   * the only code that calls getUserMedia, avoiding a competing camera stream.
   */
  start(source: HTMLCanvasElement, onFrame: (frame: Blob) => void) {
    this.stop();

    const captureCanvas = document.createElement("canvas");
    const context = captureCanvas.getContext("2d");

    const capture = () => {
      if (!context || source.width === 0 || source.height === 0) return;

      captureCanvas.width = source.width;
      captureCanvas.height = source.height;
      context.drawImage(source, 0, 0, captureCanvas.width, captureCanvas.height);

      captureCanvas.toBlob((blob) => {
        if (blob) onFrame(blob);
      }, "image/png");
    };

    capture();
    this.captureTimer = window.setInterval(capture, 500);
  }

  stop() {
    if (this.captureTimer !== null) {
      window.clearInterval(this.captureTimer);
      this.captureTimer = null;
    }
  }
}
