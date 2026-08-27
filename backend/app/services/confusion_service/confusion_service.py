
#test just on this file not whole application



import torch
import os
import cv2
import numpy as np

import tempfile
from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms

from ...models import models_vit, confusion_classifier
from .FaceExtractor import FaceExtractor
from .OpenFaceExtractor import OpenFaceExtractor
from .MediaPipeExtractor import MediaPipeExtractor

openface_extractor = OpenFaceExtractor()
extractor = MediaPipeExtractor()

PROJECT_ROOT=Path(__file__).resolve().parents[3]


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
        classifier_ckpt_path = (PROJECT_ROOT/"app"/"models"/"MLP_final_model_512.pth")
        ckpt = torch.load(
             classifier_ckpt_path, map_location="cpu",weights_only=True)

        # hp = ckpt["hyperparameters"]
        self.classifier = confusion_classifier.EmotionMLP(
            input_size=768,
            hidden_layers=ckpt["architecture"],
            dropout_rate=ckpt["dropout_rate"],
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

        # temp_dir = PROJECT_ROOT/"debug"/"temp"

        # temp_dir.mkdir(
        #     exist_ok=True)


        # input_path = (
        #     temp_dir / "input.png"
        # )

        # # /** need to restore after test
        # Path(input_path).write_bytes(frame_bytes)
        # print("Saved input frame to:", input_path, flush=True)
        

        # ==========================
        # Step 2
        # OpenFace crop face
        # ==========================

        #step 1 : decode bytes into an opencv image
        np_arr = np.frombuffer(frame_bytes, np.uint8)

        #frame is a normal OpenCV image (numpy.ndarray).
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)  
        
        #extract face using mediapipe
        #face is already the cropped face image.
        print("extractor starts",flush=True)
        face,face_box=extractor.preprocess(frame)
        
        
        # face_dir = (
        #     temp_dir / "face"
        # )

        # face_dir.mkdir(
        #     exist_ok=True
        # )
        # print("Running OpenFace for face detection and alignment...", flush=True)

        # face_path=openface_extractor.preprocess(input_path,output_dir=face_dir)
        
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
        #covert openCV image to PIL image
        face=cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(face)

        # print("Opening image...", flush=True)
        # image = Image.open(
        #     face_path
        # ).convert("RGB")


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
        print("Running MA...", flush=True)
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

        return confusion_prob,face_box

# if __name__ == "__main__":
#     service = ConfusionService()
#     # test with a sample image
#     confusion_prob = service.predict()
#     print("Confusion probability for test image:", confusion_prob)E