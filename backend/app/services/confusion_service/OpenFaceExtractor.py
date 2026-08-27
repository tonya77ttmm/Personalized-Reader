from .FaceExtractor import FaceExtractor
from pathlib import Path
import subprocess

PROJECT_ROOT=Path(__file__).resolve().parents[3]
OPEN_FACE_DIR=PROJECT_ROOT/"OpenFace"/"build"/"bin"/"FaceLandmarkImg"

class OpenFaceExtractor(FaceExtractor):
    def preprocess(self,input_path,output_dir):
        command = [
                    str(OPEN_FACE_DIR),
                    "-f",
                    str(input_path),
                    "-out_dir",
                    str(output_dir)
                ]
        print("Running command:", " ".join(str(c) for c in command), flush=True)
        result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
        )
        
        
        
                # OpenFace output
                # 找 aligned face
        
        aligned_dir = output_dir / "input_aligned"
        face_files = list(
        aligned_dir.glob("*.bmp")
                )
        
        if len(face_files) == 0:
            raise Exception("No aligned face found")
        
        face_path = face_files[0]
        
        
        print("Detected and aligned face saved to:", face_path, flush=True)
        return face_path