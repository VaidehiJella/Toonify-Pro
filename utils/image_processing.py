"""
Image Processing Utilities for Toonify Application

This module contains core image processing functions used across different filters.
Implements OpenCV-based algorithms for edge detection, noise reduction, and color manipulation.
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from typing import Tuple, Optional, Dict, Any

class ImageProcessor:
    """
    Core image processing utilities for cartoon effects.

    This class provides fundamental image processing operations that are used
    by various cartoon filters including edge detection, bilateral filtering,
    color quantization, and morphological operations.
    """

    def __init__(self):
        """Initialize the ImageProcessor with default parameters."""
        self.default_params = {
            'gaussian_blur_ksize': (5, 5),
            'gaussian_blur_sigma': 0,
            'bilateral_d': 9,
            'bilateral_sigma_color': 200,
            'bilateral_sigma_space': 200,
            'adaptive_threshold_max_value': 255,
            'adaptive_threshold_block_size': 9,
            'adaptive_threshold_c': 9,
            'kmeans_k': 8,
            'kmeans_max_iter': 100
        }

    def preprocess_image(self, image: np.ndarray, target_size: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """
        Preprocess input image for optimal processing.

        Args:
            image: Input image as numpy array
            target_size: Optional target size (width, height) for resizing

        Returns:
            Preprocessed image
        """
        # Convert to RGB if needed (OpenCV uses BGR by default)
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Assume input is RGB from PIL/Streamlit, convert to BGR for OpenCV
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Resize if target size specified
        if target_size:
            image = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)

        # Ensure image is in proper format
        image = np.clip(image, 0, 255).astype(np.uint8)

        return image

    def detect_edges_adaptive(self, image: np.ndarray, line_size: int = 7, blur_value: int = 7) -> np.ndarray:
        """
        Detect edges using adaptive thresholding.

        This method provides better edge detection for varying lighting conditions
        compared to global thresholding.

        Args:
            image: Input image (BGR format)
            line_size: Size of the neighborhood area for threshold calculation
            blur_value: Blur intensity before edge detection

        Returns:
            Binary edge image
        """
        # OpenCV requires odd kernel sizes; adaptiveThreshold also requires blockSize > 1.
        blur_value = max(1, int(blur_value))
        if blur_value % 2 == 0:
            blur_value += 1

        line_size = max(3, int(line_size))
        if line_size % 2 == 0:
            line_size += 1

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply median blur to reduce noise
        gray_blur = cv2.medianBlur(gray, blur_value)

        # Create edge mask using adaptive threshold
        edges = cv2.adaptiveThreshold(
            gray_blur, 
            self.default_params['adaptive_threshold_max_value'],
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            line_size,
            blur_value
        )

        return edges

    def detect_edges_canny(self, image: np.ndarray, low_threshold: int = 50, 
                          high_threshold: int = 150, blur_ksize: int = 5) -> np.ndarray:
        """
        Detect edges using Canny edge detection.

        Args:
            image: Input image (BGR format)
            low_threshold: Lower threshold for edge detection
            high_threshold: Upper threshold for edge detection
            blur_ksize: Kernel size for Gaussian blur preprocessing

        Returns:
            Binary edge image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur
        if blur_ksize > 0:
            gray = cv2.GaussianBlur(gray, (blur_ksize, blur_ksize), 0)

        # Apply Canny edge detection
        edges = cv2.Canny(gray, low_threshold, high_threshold)

        return edges

    def apply_bilateral_filter(self, image: np.ndarray, d: int = 9, 
                              sigma_color: int = 200, sigma_space: int = 200) -> np.ndarray:
        """
        Apply bilateral filtering for noise reduction while preserving edges.

        Bilateral filtering is very effective in noise removal while keeping edges sharp.

        Args:
            image: Input image
            d: Diameter of each pixel neighborhood
            sigma_color: Filter sigma in the color space
            sigma_space: Filter sigma in the coordinate space

        Returns:
            Filtered image
        """
        return cv2.bilateralFilter(image, d, sigma_color, sigma_space)

    def quantize_colors(self, image: np.ndarray, k: int = 8) -> np.ndarray:
        """
        Reduce the number of colors in the image using K-means clustering.

        This creates a cartoon-like effect by reducing the color palette.

        Args:
            image: Input image
            k: Number of color clusters

        Returns:
            Color-quantized image
        """
        # Reshape image to be a list of pixels
        data = image.reshape((-1, 3))
        data = np.float32(data)

        # Define criteria and apply K-means
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 
                   self.default_params['kmeans_max_iter'], 1.0)
        _, labels, centers = cv2.kmeans(
            data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
        )

        # Convert back to uint8 and reshape to original image shape
        centers = np.uint8(centers)
        quantized_data = centers[labels.flatten()]
        quantized_image = quantized_data.reshape(image.shape)

        return quantized_image

    def create_pencil_sketch(self, image: np.ndarray, blur_sigma: int = 5) -> np.ndarray:
        """
        Create a pencil sketch effect.

        This implements the dodge blending technique to create realistic pencil sketches.

        Args:
            image: Input image
            blur_sigma: Sigma value for Gaussian blur

        Returns:
            Pencil sketch image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Invert the image
        inverted = 255 - gray

        # Apply Gaussian blur to the inverted image
        blurred = cv2.GaussianBlur(inverted, (0, 0), sigmaX=blur_sigma)

        # Create the sketch using dodge blend
        sketch = self._dodge_blend(gray, blurred)

        # Convert back to 3-channel for consistency
        sketch_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

        return sketch_bgr

    def _dodge_blend(self, base: np.ndarray, blend: np.ndarray) -> np.ndarray:
        """
        Apply dodge blending mode.

        Args:
            base: Base layer
            blend: Blend layer

        Returns:
            Blended result
        """
        # Avoid division by zero
        blend = 255 - blend
        blend[blend == 0] = 1

        # Apply dodge formula
        result = (base.astype(np.float32) * 255) / blend.astype(np.float32)
        result = np.clip(result, 0, 255)

        return result.astype(np.uint8)

    def enhance_edges(self, edges: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """
        Enhance edge detection results using morphological operations.

        Args:
            edges: Binary edge image
            kernel_size: Size of morphological kernel

        Returns:
            Enhanced edge image
        """
        # Create morphological kernel
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))

        # Apply morphological closing to connect nearby edges
        enhanced = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        # Apply dilation to make edges slightly thicker
        enhanced = cv2.dilate(enhanced, kernel, iterations=1)

        return enhanced

    def combine_images(self, color_image: np.ndarray, edge_image: np.ndarray, 
                      method: str = "multiply") -> np.ndarray:
        """
        Combine color image with edge image to create cartoon effect.

        Args:
            color_image: Processed color image
            edge_image: Binary edge image
            method: Blending method ("multiply", "overlay", "bitwise_and")

        Returns:
            Combined cartoon image
        """
        # Ensure edge image is 3-channel
        if len(edge_image.shape) == 2:
            edge_image = cv2.cvtColor(edge_image, cv2.COLOR_GRAY2BGR)

        if method == "multiply":
            # Normalize edge image to 0-1 range for multiplication
            edge_norm = edge_image.astype(np.float32) / 255.0
            result = (color_image.astype(np.float32) * edge_norm).astype(np.uint8)

        elif method == "overlay":
            # Simple overlay blending
            result = cv2.addWeighted(color_image, 0.8, edge_image, 0.2, 0)

        elif method == "bitwise_and":
            # Traditional bitwise AND approach
            result = cv2.bitwise_and(color_image, edge_image)

        else:
            raise ValueError(f"Unknown blending method: {method}")

        return result

    def adjust_contrast_brightness(self, image: np.ndarray, contrast: float = 1.0, 
                                  brightness: int = 0) -> np.ndarray:
        """
        Adjust image contrast and brightness.

        Args:
            image: Input image
            contrast: Contrast factor (1.0 = no change)
            brightness: Brightness adjustment (-100 to 100)

        Returns:
            Adjusted image
        """
        # Apply contrast and brightness adjustment
        adjusted = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)

        return adjusted

    def apply_oil_painting_effect(self, image: np.ndarray, size: int = 7, 
                                 dyn_ratio: int = 1) -> np.ndarray:
        """
        Apply oil painting effect using OpenCV's xphoto module.

        Args:
            image: Input image
            size: Size of the neighborhood
            dyn_ratio: Image dynamic ratio

        Returns:
            Oil painting effect image
        """
        try:
            # Try to use OpenCV's oil painting function if available
            import cv2
            oil_painting = cv2.xphoto.oilPainting(image, size, dyn_ratio)
            return oil_painting
        except (ImportError, AttributeError):
            # Fallback to a simple approximation using blur and quantization
            # Apply strong bilateral filtering
            smooth = cv2.bilateralFilter(image, 15, 80, 80)

            # Quantize colors
            quantized = self.quantize_colors(smooth, k=6)

            return quantized

    def create_watercolor_effect(self, image: np.ndarray) -> np.ndarray:
        """
        Create watercolor painting effect.

        Args:
            image: Input image

        Returns:
            Watercolor effect image
        """
        # Apply multiple bilateral filters with different parameters
        smooth1 = cv2.bilateralFilter(image, 15, 80, 80)
        smooth2 = cv2.bilateralFilter(smooth1, 15, 80, 80)

        # Reduce colors
        quantized = self.quantize_colors(smooth2, k=6)

        # Add slight blur for soft watercolor look
        watercolor = cv2.GaussianBlur(quantized, (3, 3), 0)

        return watercolor

    def postprocess_image(self, image: np.ndarray, output_format: str = "RGB") -> np.ndarray:
        """
        Postprocess image for final output.

        Args:
            image: Processed image
            output_format: Desired output format ("RGB" or "BGR")

        Returns:
            Final processed image
        """
        # Convert BGR to RGB if needed (for display in Streamlit/PIL)
        if output_format == "RGB" and len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Ensure proper data type and range
        image = np.clip(image, 0, 255).astype(np.uint8)

        return image

    def get_image_stats(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Get basic statistics about the image.

        Args:
            image: Input image

        Returns:
            Dictionary containing image statistics
        """
        stats = {
            'shape': image.shape,
            'dtype': str(image.dtype),
            'min_value': int(np.min(image)),
            'max_value': int(np.max(image)),
            'mean_value': float(np.mean(image)),
            'std_value': float(np.std(image))
        }

        return stats
