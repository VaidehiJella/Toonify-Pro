"""
Unit tests for the Image Processing module.

This module contains comprehensive tests for all image processing functions
to ensure they work correctly with various input conditions.
"""

import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_processing import ImageProcessor

class TestImageProcessor:
    """Test cases for the ImageProcessor class."""

    @pytest.fixture
    def processor(self):
        """Create an ImageProcessor instance for testing."""
        return ImageProcessor()

    @pytest.fixture
    def sample_image_rgb(self):
        """Create a sample RGB image."""
        return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

    @pytest.fixture
    def sample_image_bgr(self):
        """Create a sample BGR image."""
        return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

    @pytest.fixture
    def sample_image_gray(self):
        """Create a sample grayscale image."""
        return np.random.randint(0, 255, (100, 100), dtype=np.uint8)

    def test_initialization(self, processor):
        """Test ImageProcessor initialization."""
        assert isinstance(processor, ImageProcessor)
        assert hasattr(processor, 'default_params')
        assert isinstance(processor.default_params, dict)

    def test_preprocess_image_rgb(self, processor, sample_image_rgb):
        """Test preprocessing RGB image."""
        result = processor.preprocess_image(sample_image_rgb)

        assert isinstance(result, np.ndarray)
        assert result.dtype == np.uint8
        assert len(result.shape) == 3
        assert result.shape[2] == 3

    def test_preprocess_image_with_resize(self, processor, sample_image_rgb):
        """Test preprocessing with resize."""
        target_size = (50, 50)
        result = processor.preprocess_image(sample_image_rgb, target_size)

        assert result.shape[:2] == target_size[::-1]  # OpenCV uses (height, width)

    def test_detect_edges_adaptive(self, processor, sample_image_bgr):
        """Test adaptive edge detection."""
        edges = processor.detect_edges_adaptive(sample_image_bgr)

        assert isinstance(edges, np.ndarray)
        assert len(edges.shape) == 2  # Should be grayscale
        assert edges.dtype == np.uint8
        assert np.all((edges == 0) | (edges == 255))  # Binary image

    def test_detect_edges_canny(self, processor, sample_image_bgr):
        """Test Canny edge detection."""
        edges = processor.detect_edges_canny(sample_image_bgr)

        assert isinstance(edges, np.ndarray)
        assert len(edges.shape) == 2  # Should be grayscale
        assert edges.dtype == np.uint8
        assert np.all((edges == 0) | (edges == 255))  # Binary image

    def test_apply_bilateral_filter(self, processor, sample_image_bgr):
        """Test bilateral filtering."""
        filtered = processor.apply_bilateral_filter(sample_image_bgr)

        assert isinstance(filtered, np.ndarray)
        assert filtered.shape == sample_image_bgr.shape
        assert filtered.dtype == np.uint8

    def test_quantize_colors(self, processor, sample_image_bgr):
        """Test color quantization."""
        quantized = processor.quantize_colors(sample_image_bgr, k=4)

        assert isinstance(quantized, np.ndarray)
        assert quantized.shape == sample_image_bgr.shape
        assert quantized.dtype == np.uint8

    def test_create_pencil_sketch(self, processor, sample_image_bgr):
        """Test pencil sketch creation."""
        sketch = processor.create_pencil_sketch(sample_image_bgr)

        assert isinstance(sketch, np.ndarray)
        assert sketch.shape == sample_image_bgr.shape
        assert sketch.dtype == np.uint8

    def test_dodge_blend(self, processor):
        """Test dodge blending function."""
        base = np.random.randint(0, 255, (50, 50), dtype=np.uint8)
        blend = np.random.randint(0, 255, (50, 50), dtype=np.uint8)

        result = processor._dodge_blend(base, blend)

        assert isinstance(result, np.ndarray)
        assert result.shape == base.shape
        assert result.dtype == np.uint8
        assert np.min(result) >= 0
        assert np.max(result) <= 255

    def test_enhance_edges(self, processor):
        """Test edge enhancement."""
        # Create a binary edge image
        edges = np.zeros((100, 100), dtype=np.uint8)
        edges[40:60, 40:60] = 255  # Create a square

        enhanced = processor.enhance_edges(edges)

        assert isinstance(enhanced, np.ndarray)
        assert enhanced.shape == edges.shape
        assert enhanced.dtype == np.uint8

    def test_combine_images_multiply(self, processor, sample_image_bgr):
        """Test image combination with multiply method."""
        # Create edge image
        edges = np.random.choice([0, 255], size=sample_image_bgr.shape[:2], p=[0.8, 0.2]).astype(np.uint8)

        result = processor.combine_images(sample_image_bgr, edges, method="multiply")

        assert isinstance(result, np.ndarray)
        assert result.shape == sample_image_bgr.shape
        assert result.dtype == np.uint8

    def test_combine_images_overlay(self, processor, sample_image_bgr):
        """Test image combination with overlay method."""
        edges = np.random.choice([0, 255], size=sample_image_bgr.shape[:2], p=[0.8, 0.2]).astype(np.uint8)

        result = processor.combine_images(sample_image_bgr, edges, method="overlay")

        assert isinstance(result, np.ndarray)
        assert result.shape == sample_image_bgr.shape
        assert result.dtype == np.uint8

    def test_combine_images_bitwise_and(self, processor, sample_image_bgr):
        """Test image combination with bitwise_and method."""
        edges = np.random.choice([0, 255], size=sample_image_bgr.shape[:2], p=[0.8, 0.2]).astype(np.uint8)

        result = processor.combine_images(sample_image_bgr, edges, method="bitwise_and")

        assert isinstance(result, np.ndarray)
        assert result.shape == sample_image_bgr.shape
        assert result.dtype == np.uint8

    def test_combine_images_unknown_method(self, processor, sample_image_bgr):
        """Test image combination with unknown method."""
        edges = np.random.choice([0, 255], size=sample_image_bgr.shape[:2]).astype(np.uint8)

        with pytest.raises(ValueError):
            processor.combine_images(sample_image_bgr, edges, method="unknown")

    def test_adjust_contrast_brightness(self, processor, sample_image_bgr):
        """Test contrast and brightness adjustment."""
        result = processor.adjust_contrast_brightness(sample_image_bgr, contrast=1.2, brightness=10)

        assert isinstance(result, np.ndarray)
        assert result.shape == sample_image_bgr.shape
        assert result.dtype == np.uint8

    def test_create_watercolor_effect(self, processor, sample_image_bgr):
        """Test watercolor effect creation."""
        result = processor.create_watercolor_effect(sample_image_bgr)

        assert isinstance(result, np.ndarray)
        assert result.shape == sample_image_bgr.shape
        assert result.dtype == np.uint8

    def test_postprocess_image_rgb(self, processor, sample_image_bgr):
        """Test postprocessing to RGB format."""
        result = processor.postprocess_image(sample_image_bgr, output_format="RGB")

        assert isinstance(result, np.ndarray)
        assert result.shape == sample_image_bgr.shape
        assert result.dtype == np.uint8
        assert np.min(result) >= 0
        assert np.max(result) <= 255

    def test_postprocess_image_bgr(self, processor, sample_image_bgr):
        """Test postprocessing to BGR format."""
        result = processor.postprocess_image(sample_image_bgr, output_format="BGR")

        assert isinstance(result, np.ndarray)
        assert result.shape == sample_image_bgr.shape
        assert result.dtype == np.uint8

    def test_get_image_stats(self, processor, sample_image_bgr):
        """Test getting image statistics."""
        stats = processor.get_image_stats(sample_image_bgr)

        assert isinstance(stats, dict)
        required_keys = ['shape', 'dtype', 'min_value', 'max_value', 'mean_value', 'std_value']
        for key in required_keys:
            assert key in stats

    def test_edge_cases_single_channel(self, processor):
        """Test processing single channel images."""
        gray_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)

        # Should handle grayscale input
        result = processor.preprocess_image(gray_image)
        assert isinstance(result, np.ndarray)

    def test_edge_cases_extreme_values(self, processor):
        """Test processing images with extreme values."""
        # Test with all zeros
        zero_image = np.zeros((50, 50, 3), dtype=np.uint8)
        result = processor.preprocess_image(zero_image)
        assert isinstance(result, np.ndarray)

        # Test with all 255s
        max_image = np.ones((50, 50, 3), dtype=np.uint8) * 255
        result = processor.preprocess_image(max_image)
        assert isinstance(result, np.ndarray)

    def test_parameter_validation(self, processor, sample_image_bgr):
        """Test parameter validation in various functions."""
        # Test negative parameters (should not crash)
        try:
            processor.detect_edges_adaptive(sample_image_bgr, line_size=1, blur_value=1)
            processor.apply_bilateral_filter(sample_image_bgr, d=1, sigma_color=1, sigma_space=1)
        except Exception as e:
            # Some parameter combinations might be invalid, but shouldn't crash unexpectedly
            assert isinstance(e, (ValueError, cv2.error))

class TestImageProcessorIntegration:
    """Integration tests for ImageProcessor."""

    @pytest.fixture
    def processor(self):
        return ImageProcessor()

    def test_full_processing_pipeline(self, processor):
        """Test a complete image processing pipeline."""
        # Create test image
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

        # Preprocess
        preprocessed = processor.preprocess_image(image)

        # Detect edges
        edges = processor.detect_edges_adaptive(preprocessed)

        # Apply bilateral filter
        smooth = processor.apply_bilateral_filter(preprocessed)

        # Quantize colors
        quantized = processor.quantize_colors(smooth)

        # Combine
        result = processor.combine_images(quantized, edges)

        # Postprocess
        final = processor.postprocess_image(result)

        assert isinstance(final, np.ndarray)
        assert final.shape == image.shape
        assert final.dtype == np.uint8

    def test_consistency_across_runs(self, processor):
        """Test that processing is consistent across multiple runs."""
        image = np.ones((50, 50, 3), dtype=np.uint8) * 128

        result1 = processor.preprocess_image(image)
        result2 = processor.preprocess_image(image)

        np.testing.assert_array_equal(result1, result2)

if __name__ == '__main__':
    # Run tests if script is executed directly
    pytest.main([__file__])
