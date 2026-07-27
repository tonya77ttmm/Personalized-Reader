export class CameraService {
  private stream: MediaStream | null = null;

  async start(video: HTMLVideoElement, onFrame: (frame: Blob) => void) {
    // 1. request camera access
    this.stream = await navigator.mediaDevices.getUserMedia({
      video: true,
    });
    // const video = document.createElement("video");

    video.srcObject = this.stream;

    await video.play();

    // 3. create canvas for screenshots
    const canvas = document.createElement("canvas");

    const context = canvas.getContext("2d");

    // 4. 2 frames per second
    setInterval(() => {
      if (!context) return;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      //   Take the current picture in the canvas, convert it into a PNG Blob, and when that conversion finishes, run this function
      canvas.toBlob((blob) => {
        if (blob) {
          onFrame(blob);
        }
      }, "image/png");
    }, 1000);
  }

  stop() {
    this.stream?.getTracks().forEach((track) => track.stop());
  }
}
