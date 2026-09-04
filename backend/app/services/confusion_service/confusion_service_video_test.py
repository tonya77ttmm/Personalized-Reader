import asyncio
from pathlib import Path
import cv2
import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from ...models import confusion_classifier, models_vit
from .MediaPipeExtractor import MediaPipeExtractor

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class ConfusionServiceVideoTest:

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.extractor = MediaPipeExtractor()

        # ==========================
        # 1. MAE Model
        # ==========================
        model_name = "vit_base_patch16"
        mae_ckpt_path = (
            PROJECT_ROOT / "app" / "models" / "mae_face_pretrain_vit_base.pth"
        )

        self.mae = getattr(models_vit, model_name)(
            global_pool=True,
            num_classes=2,
            drop_path_rate=0.1,
            img_size=224,
        )
        checkpoint = torch.load(
            mae_ckpt_path, map_location="cpu", weights_only=False
        )

        self.mae.load_state_dict(checkpoint["model"], strict=False)
        self.mae.to(self.device)
        self.mae.eval()

        # ==========================
        # 2. MLP Classifier
        # ==========================
        classifier_ckpt_path = (
            PROJECT_ROOT / "app" / "models" / "MLP_final_model_512.pth"
        )
        ckpt = torch.load(
            classifier_ckpt_path, map_location="cpu", weights_only=True
        )

        self.classifier = confusion_classifier.EmotionMLP(
            input_size=768,
            hidden_layers=ckpt["architecture"],
            dropout_rate=ckpt["dropout_rate"],
            num_classes=2,
        )
        self.classifier.load_state_dict(ckpt["model_state_dict"])
        self.classifier.to(self.device)
        self.classifier.eval()

        # Preprocessing transform
        self.transform = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

    def predict(self, frame: np.ndarray):
        """Predict method modified for direct OpenCV BGR numpy frame input."""
        # 1. Guard against empty frame input
        if frame is None or frame.size == 0 or frame.shape[0] == 0 or frame.shape[1] == 0:
            return {"confusion": 0.0}, None

        # Ensure frame memory alignment
        frame = np.ascontiguousarray(frame)

        # 2. Extract face using MediaPipe
        face, face_box = self.extractor.preprocess(frame)

        # Guard: If MediaPipe finds no face or returns an empty array, safely skip prediction
        if (
            face is None
            or not isinstance(face, np.ndarray)
            or face.size == 0
            or face.shape[0] == 0
            or face.shape[1] == 0
        ):
            print("No face detected in this frame. Skipping.", flush=True)
            return {"confusion": 0.0}, face_box

        # 3. Convert face crop to RGB and PIL Image
        face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(face_rgb)

        # 4. Feature Extraction & Prediction
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            _, feature = self.mae(image_tensor, ret_feature=True)
            logits = self.classifier(feature)
            probs = torch.softmax(logits, dim=1)
            confusion_prob = probs[:, 1].cpu().item()

        return {"confusion": confusion_prob}, face_box