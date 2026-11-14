import torch
import os

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "models",
    "u2net",
    "u2netp.pth"
)

def load_u2net():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("U2Net weights not found")

    model = torch.load(MODEL_PATH, map_location="cpu")
    model.eval()
    return model