
#test just on this file not whole application


import torch
import os
import subprocess
import tempfile
from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms

from app.models import models_vit, confusion_classifier

PROJECT_ROOT=Path(__file__).resolve().parents[2]
OPEN_FACE_DIR=PROJECT_ROOT/"OpenFace"/"build"/"bin"/"FaceLandmarkImg"

class ConfusionService:


    def __init__(self):

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )
        # ==========================
        # 2. MAE
        # ==========================

        model_name = 'vit_base_patch16'

        mae_ckpt_path = (
            PROJECT_ROOT / "app" / "models" / "mae_face_pretrain_vit_base.pth"
        )

        #create MAE model
        self.mae = getattr(
            models_vit,
            model_name
        )(
            global_pool=True,
            num_classes=2, 
            drop_path_rate=0.1,
            img_size=224,
        )
        checkpoint = torch.load(
            mae_ckpt_path,
            map_location="cpu",
            weights_only=False
        )

        self.mae.load_state_dict(
            checkpoint["model"],
            strict=False
        )
        self.mae.to(self.device)
        self.mae.eval()



        # ==========================
        # 3. MLP classifier
        # ==========================
        classifier_ckpt_path = (PROJECT_ROOT/"app"/"models"/"MLP_1024_512_final_model.pth")
        ckpt = torch.load(
             classifier_ckpt_path, map_location="cpu",weights_only=False)

        hp = ckpt["hyperparameters"]
        self.classifier = confusion_classifier.EmotionMLP(
            input_size=768,
            hidden_layers=[1024, 512],
            dropout_rate=hp["dropout"],
            num_classes=2
        )
        self.classifier.load_state_dict(ckpt["model_state_dict"])

        self.classifier.to(self.device)

        self.classifier.eval()


        # MAE preprocessing
        self.transform = transforms.Compose([
            transforms.Resize(
                (224,224)
            ),
            transforms.ToTensor(),
            #normalize？
            transforms.Normalize(
                mean=[0.485,0.456,0.406],
                std=[0.229,0.224,0.225]
            )
        ])

    def predict(self, frame_bytes):

        # ==========================
        # Step 1
        # save received image
        # ==========================

        temp_dir = PROJECT_ROOT/"debug"/"temp"

        temp_dir.mkdir(
            exist_ok=True)


        input_path = (
            temp_dir / "input.png"
        )

        # /** need to restore after test
        Path(input_path).write_bytes(frame_bytes)
        print("Saved input frame to:", input_path, flush=True)
        

        # ==========================
        # Step 2
        # OpenFace crop face
        # ==========================

        face_dir = (
            temp_dir / "face"
        )

        face_dir.mkdir(
            exist_ok=True
        )
        print("Running OpenFace for face detection and alignment...", flush=True)
        command = [
            str(OPEN_FACE_DIR),
            "-f",
            str(input_path),
            "-out_dir",
            str(face_dir)
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

        aligned_dir = face_dir / "input_aligned"
        face_files = list(
        aligned_dir.glob("*.bmp")
        )

        if len(face_files) == 0:
            raise Exception("No aligned face found")

        face_path = face_files[0]


        print("Detected and aligned face saved to:", face_path, flush=True)
        # debug save
        # predict_face=PROJECT_ROOT/"debug"/"predict_face.jpg"    
        # # debug_face = Path(
        # #     "debug/cropped_face.jpg"
        # # )

        # print("Saving predict face image to:", predict_face, flush=True)
        # predict_face.write_bytes(
        #     face_path.read_bytes()
        # )

        # print("face_path:", face_path, flush=True)
        # print("predict_face:", predict_face, flush=True)

        # ==========================
        # Step 3
        # MAE feature extraction
        # ==========================
        print("Opening image...", flush=True)
        image = Image.open(
            face_path
        ).convert("RGB")

        print("Transform...", flush=True)
        image = self.transform(
            image
        )

        print("Unsqueeze...", flush=True)
        image = image.unsqueeze(0)
        print("Move to device...", flush=True)
        image = image.to(
            self.device
        )   
        print("Running MAE...", flush=True)
        print("self.device:", self.device, flush=True)  

        print(image.shape)

        with torch.no_grad():

            _, feature = self.mae(
                image,
                ret_feature=True
            )

        print("Extracted feature shape:", feature.shape, flush=True)
        # feature:
        # [1,768]



        # ==========================
        # Step 4
        # classifier
        # ==========================

        with torch.no_grad():

            logits = self.classifier(
                feature
            )

            print("Logits:", logits, flush=True)
            probs = torch.softmax(
                logits,
                dim=1
            )
            print("Probabilities:", probs, flush=True)

            confusion_prob = (
                probs[:,1]
                .cpu()
                .item()
            )

        print("Confusion probability:", confusion_prob, flush=True)

        return confusion_prob

# if __name__ == "__main__":
#     service = ConfusionService()
#     # test with a sample image
#     confusion_prob = service.predict()
#     print("Confusion probability for test image:", confusion_prob)