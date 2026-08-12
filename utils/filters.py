"""
Filter Implementations for Toonify Application

This module contains all the cartoon filter implementations that use the ImageProcessor
utilities to create different artistic effects.
"""

import cv2
import numpy as np
from typing import Dict, Any, Optional
from .image_processing import ImageProcessor

class FilterManager:
    """
    Manages all available cartoon filters and their applications.

    This class provides a unified interface for applying different cartoon effects
    to images, with customizable parameters for each filter type.
    """

    def __init__(self):
        """Initialize the FilterManager with ImageProcessor instance."""
        self.processor = ImageProcessor()

        # Define available filters and their default parameters
        self.filters = {
            'classic': {
                'name': 'Classic Cartoon',
                'description': 'Traditional cartoon effect with smooth colors and bold edges',
                'function': self._apply_classic_cartoon,
                'parameters': ['edge_thickness', 'color_smoothing', 'blur_strength']
            },
            'sketch': {
                'name': 'Sketch Effect',
                'description': 'Black and white pencil sketch style',
                'function': self._apply_sketch_effect,
                'parameters': ['edge_thickness', 'blur_strength']
            },
            'color_pencil': {
                'name': 'Color Pencil',
                'description': 'Colored pencil drawing effect',
                'function': self._apply_color_pencil,
                'parameters': ['edge_thickness', 'color_smoothing', 'blur_strength']
            },
            'oil_painting': {
                'name': 'Oil Painting',
                'description': 'Artistic oil painting style',
                'function': self._apply_oil_painting,
                'parameters': ['color_smoothing', 'blur_strength']
            },
            'watercolor': {
                'name': 'Watercolor',
                'description': 'Soft watercolor painting effect',
                'function': self._apply_watercolor,
                'parameters': ['color_smoothing', 'blur_strength']
            },
            'anime': {
                'name': 'Anime Style',
                'description': 'Anime/manga cartoon style',
                'function': self._apply_anime_style,
                'parameters': ['edge_thickness', 'color_smoothing']
            }
        }

    def get_available_filters(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all available filters.

        Returns:
            Dictionary containing filter information
        """
        return {k: {
            'name': v['name'],
            'description': v['description'],
            'parameters': v['parameters']
        } for k, v in self.filters.items()}

    def apply_filter(self, image: np.ndarray, filter_type: str, 
                    parameters: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """
        Apply the specified filter to the image.

        Args:
            image: Input image as numpy array
            filter_type: Type of filter to apply
            parameters: Dictionary of filter parameters

        Returns:
            Processed image

        Raises:
            ValueError: If filter_type is not recognized
        """
        if filter_type not in self.filters:
            raise ValueError(f"Unknown filter type: {filter_type}")

        # Use default parameters if none provided
        if parameters is None:
            parameters = {}

        # Preprocess the image
        processed_image = self.processor.preprocess_image(image)

        # Apply the selected filter
        filter_function = self.filters[filter_type]['function']
        result = filter_function(processed_image, parameters)

        # Postprocess for final output
        final_image = self.processor.postprocess_image(result, output_format="RGB")

        return final_image

    def _apply_classic_cartoon(self, image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """
        Apply classic cartoon effect.

        This is the most traditional cartoon filter that combines edge detection
        with bilateral filtering and color quantization.

        Args:
            image: Input image (BGR format)
            params: Filter parameters

        Returns:
            Cartoon-processed image
        """
        # Extract parameters with defaults
        edge_thickness = params.get('edge_thickness', 5)
        color_smoothing = params.get('color_smoothing', 7)
        blur_strength = params.get('blur_strength', 3)

        # Step 1: Create edge mask
        edges = self.processor.detect_edges_adaptive(image, edge_thickness, blur_strength)

        # Step 2: Apply bilateral filtering for smooth colors
        smooth = self.processor.apply_bilateral_filter(
            image, 
            d=color_smoothing * 2 + 1,
            sigma_color=color_smoothing * 20,
            sigma_space=color_smoothing * 20
        )

        # Step 3: Quantize colors for cartoon effect
        quantized = self.processor.quantize_colors(smooth, k=8)

        # Step 4: Combine with edges
        cartoon = self.processor.combine_images(quantized, edges, method="bitwise_and")

        return cartoon

    def _apply_sketch_effect(self, image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """
        Apply pencil sketch effect.

        Args:
            image: Input image (BGR format)
            params: Filter parameters

        Returns:
            Sketch-processed image
        """
        # Extract parameters
        blur_strength = params.get('blur_strength', 3)

        # Create pencil sketch
        sketch = self.processor.create_pencil_sketch(image, blur_sigma=blur_strength)

        return sketch

    def _apply_color_pencil(self, image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """
        Apply colored pencil effect.

        Args:
            image: Input image (BGR format)
            params: Filter parameters

        Returns:
            Color pencil processed image
        """
        # Extract parameters
        edge_thickness = params.get('edge_thickness', 5)
        color_smoothing = params.get('color_smoothing', 7)
        blur_strength = params.get('blur_strength', 3)

        # Create edge mask
        edges = self.processor.detect_edges_adaptive(image, edge_thickness, blur_strength)

        # Apply light bilateral filtering to maintain some texture
        smooth = self.processor.apply_bilateral_filter(
            image,
            d=color_smoothing,
            sigma_color=color_smoothing * 10,
            sigma_space=color_smoothing * 10
        )

        # Light color quantization
        quantized = self.processor.quantize_colors(smooth, k=12)

        # Combine with edges using multiply blend for softer effect
        colored_pencil = self.processor.combine_images(quantized, edges, method="multiply")

        # Adjust contrast for pencil-like appearance
        result = self.processor.adjust_contrast_brightness(colored_pencil, contrast=1.2, brightness=10)

        return result

    def _apply_oil_painting(self, image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """
        Apply oil painting effect.

        Args:
            image: Input image (BGR format)
            params: Filter parameters

        Returns:
            Oil painting processed image
        """
        # Extract parameters
        color_smoothing = params.get('color_smoothing', 7)
        blur_strength = params.get('blur_strength', 3)

        # Apply oil painting effect
        oil_painted = self.processor.apply_oil_painting_effect(
            image, 
            size=color_smoothing,
            dyn_ratio=blur_strength
        )

        return oil_painted

    def _apply_watercolor(self, image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """
        Apply watercolor effect.

        Args:
            image: Input image (BGR format)
            params: Filter parameters

        Returns:
            Watercolor processed image
        """
        # Apply watercolor effect
        watercolor = self.processor.create_watercolor_effect(image)

        return watercolor

    def _apply_anime_style(self, image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """
        Apply anime/manga style effect.

        Args:
            image: Input image (BGR format)
            params: Filter parameters

        Returns:
            Anime-style processed image
        """
        # Extract parameters
        edge_thickness = params.get('edge_thickness', 5)
        color_smoothing = params.get('color_smoothing', 7)

        # Create strong edge mask for anime-style bold outlines
        edges = self.processor.detect_edges_adaptive(image, edge_thickness, 5)

        # Apply strong bilateral filtering for flat color areas
        smooth = self.processor.apply_bilateral_filter(
            image,
            d=color_smoothing * 3,
            sigma_color=color_smoothing * 25,
            sigma_space=color_smoothing * 25
        )

        # Aggressive color quantization for anime-style flat colors
        quantized = self.processor.quantize_colors(smooth, k=6)

        # Enhance saturation for vibrant anime colors
        hsv = cv2.cvtColor(quantized, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], 1.3)  # Increase saturation
        quantized = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # Combine with strong edges
        anime = self.processor.combine_images(quantized, edges, method="bitwise_and")

        return anime

    def get_filter_preview_thumbnails(self, image: np.ndarray, 
                                    thumbnail_size: tuple = (150, 150)) -> Dict[str, np.ndarray]:
        """
        Generate preview thumbnails for all filters.

        Args:
            image: Input image
            thumbnail_size: Size of thumbnail (width, height)

        Returns:
            Dictionary mapping filter names to thumbnail images
        """
        thumbnails = {}

        # Resize image for faster processing
        small_image = cv2.resize(image, thumbnail_size)

        for filter_id in self.filters.keys():
            try:
                # Apply filter with default parameters
                filtered = self.apply_filter(small_image, filter_id)
                thumbnails[filter_id] = filtered
            except Exception as e:
                print(f"Error generating thumbnail for {filter_id}: {e}")
                # Use original image as fallback
                thumbnails[filter_id] = self.processor.postprocess_image(small_image)

        return thumbnails

    def batch_process_images(self, images: list, filter_type: str, 
                           parameters: Optional[Dict[str, Any]] = None) -> list:
        """
        Process multiple images with the same filter.

        Args:
            images: List of input images
            filter_type: Filter to apply
            parameters: Filter parameters

        Returns:
            List of processed images
        """
        processed_images = []

        for image in images:
            try:
                processed = self.apply_filter(image, filter_type, parameters)
                processed_images.append(processed)
            except Exception as e:
                print(f"Error processing image: {e}")
                # Add original image as fallback
                processed_images.append(self.processor.postprocess_image(image))

        return processed_images
