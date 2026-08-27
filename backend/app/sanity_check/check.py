import asyncio
from pathlib import Path
import cv2
from ..services.confusion_service.confusion_service_video_test import ConfusionServiceVideoTest

async def sanity_check_confusion_detector(video_path: Path, confusion_service):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Failed to open video: {video_path}")
        return

    frame_count = 0
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or frame is None or frame.size == 0:
                print("End of video stream or unallocated frame reached.")
                break
            
            frame_count += 1
            prediction, face_box = await asyncio.to_thread(
                confusion_service.predict, frame
            )

            # Extract confusion probability safely
            prob = 0.0
            if isinstance(prediction, dict):
                prob = prediction.get("confusion", 0.0)
            elif isinstance(prediction, (float, int)):
                prob = float(prediction)

            print(f"Frame {frame_count} - Confusion: {prob:.6f}, Face Box: {face_box}", flush=True)

            # Draw face box and confusion text on video window
            if face_box is not None:
                try:
                    # Support dictionary format: {'x': ..., 'y': ..., 'width': ..., 'height': ...}
                    if isinstance(face_box, dict):
                        x = int(face_box.get("x", 0))
                        y = int(face_box.get("y", 0))
                        w = int(face_box.get("width", 0))
                        h = int(face_box.get("height", 0))
                    # Support tuple/list format: [x, y, w, h]
                    elif isinstance(face_box, (list, tuple)) and len(face_box) == 4:
                        x, y, w, h = [int(v) for v in face_box]
                    else:
                        x = y = w = h = 0

                    if w > 0 and h > 0:
                        # Draw bounding box (Green)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        
                        # Format label cleanly as a 0 to 1 float string
                        label = f"Confusion: {prob:.4f}"
                        
                        # Draw text background box for clarity
                        cv2.putText(
                            frame,
                            label,
                            (x, max(y - 10, 25)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0),
                            2,
                        )
                except Exception as e:
                    print(f"Error drawing frame {frame_count}: {e}")

            # Display frame in standard OpenCV pop-up window
            cv2.imshow("Confusion Model Sanity Check", frame)
            
            # Press 'q' to quit early or wait 30ms between frames
            if cv2.waitKey(30) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        # Give OpenCV window time to close cleanly on macOS
        cv2.waitKey(1)

if __name__ == "__main__":
    service = ConfusionServiceVideoTest()
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    video_file = PROJECT_ROOT / "backend"/"app"/"sanity_check" /"video"/ "9403280115.avi"
    asyncio.run(sanity_check_confusion_detector(video_file, service))

    #1100012010.avi" confusion 3
    #1100011012. confusion.  2
    #110001010. confusion 0
    #5000441034.avi, 2
    # 5000441035.avi,1
    # 5100451045.avi,0,2,1,0
    #5100452016.avi,1,1,2,0
    # 8826540260.mp4,3,2,2,1
    # 88265402780.mp4,0,3,2,0
    # 9403280115.avi,1,2,1,1