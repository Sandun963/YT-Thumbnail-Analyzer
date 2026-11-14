import torch
import clip

_model = None
_preprocess = None

def load_model():
    global _model, _preprocess
    if _model is None:
        _model, _preprocess = clip.load("ViT-B/32", device="cpu")
    return _model, _preprocess

def get_clip_embedding(pil_image):
    model, preprocess = load_model()
    image = preprocess(pil_image).unsqueeze(0)

    with torch.no_grad():
        emb = model.encode_image(image)

    return emb.cpu().numpy().tolist()