from skimage import filters
import numpy as np

def simple_saliency(gray):
    edges = filters.sobel(gray)
    return float(np.mean(edges))