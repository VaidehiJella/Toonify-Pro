"""
Unit tests for the Filters module.

This module contains comprehensive tests for all filter implementations
to ensure they work correctly with various input images and parameters.
"""

import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.filters import FilterManager
from utils.image_processing import ImageProcessor

class TestFilterManager:
    """Test cases for the FilterManager class."""

    @pytest.fixture
    def filter_manager(self):
        """Create a FilterManager instance for testing."""
        return FilterManager()

    @pytest.fixture
    def sample_image(self):
        """Create a sample test image."""
        # Create a simple test image (100x100 RGB)
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        return image

    @pytest.fixture
    def sample_image_bgr(self):
        """Create a sample test image in BGR format."""
        # Create a simple test image (100x100 BGR)
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        return image

    def test_initialization(self, filter_manager):
        """Test FilterManager initialization."""
        assert isinstance(filter_manager, FilterManager)
        assert hasattr(filter_manager, 'processor')
        assert hasattr(filter_manager, 'filters')
        assert len(filter_manager.filters) == 6  # Expected number of filters

    def test_get_available_filters(self, filter_manager):
        """Test getting available filters information."""
        filters = filter_manager.get_available_filters()

        assert isinstance(filters, dict)
        assert len(filters) == 6

        expected_filters = ['classic', 'sketch', 'color_pencil', 'oil_painting', 'watercolor', 'anime']
        for filter_id in expected_filters:
            assert filter_id in filters
            assert 'name' in filters[filter_id]
            assert 'description' in filters[filter_id]
            assert 'parameters' in filters[filter_id]

    def test_apply_filter_unknown_type(self, filter_manager, sample_image):
        """Test applying an unknown filter type."""
        with pytest.raises(ValueError):
            filter_manager.apply_filter(sample_image, 'unknown_filter')

    def test_apply_classic_cartoon_filter(self, filter_manager, sample_image):
        """Test applying classic cartoon filter."""
        result = filter_manager.apply_filter(sample_image, 'classic')

        assert isinstance(result, np.ndarray)
        assert result.shape == sample_image.shape
        assert result.dtype == np.uint8
        assert np.min(result) >= 0
        assert np.max(result) <= 255

    def test_apply_sketch_filter(self, filter_manager, sample_image):
        """Test applying sketch effect filter."""
        result = filter_manager.apply_filter(sample_image, 'sketch')

        assert isinstance(result, np.ndarray)
        assert result.shape == sample_image.shape
        assert result.dtype == np.uint8

    def test_apply_color_pencil_filter(self, filter_manager, sample_image):
        """Test applying color pencil filter."""
        result = filter_manager.apply_filter(sample_image, 'color_pencil')

        assert isinstance(result, np.ndarray)
        assert result.shape == sample_image.shape
        assert result.dtype == np.uint8

    def test_apply_oil_painting_filter(self, filter_manager, sample_image):
        """Test applying oil painting filter."""
        result = filter_manager.apply_filter(sample_image, 'oil_painting')

        assert isinstance(result, np.ndarray)
        assert result.shape == sample_image.shape
        assert result.dtype == np.uint8

    def test_apply_watercolor_filter(self, filter_manager, sample_image):
        """Test applying watercolor filter."""
        result = filter_manager.apply_filter(sample_image, 'watercolor')

        assert isinstance(result, np.ndarray)
        assert result.shape == sample_image.shape
        assert result.dtype == np.uint8

    def test_apply_anime_filter(self, filter_manager, sample_image):
        """Test applying anime style filter."""
        result = filter_manager.apply_filter(sample_image, 'anime')

        assert isinstance(result, np.ndarray)
        assert result.shape == sample_image.shape
        assert result.dtype == np.uint8

    def test_apply_filter_with_custom_parameters(self, filter_manager, sample_image):
        """Test applying filter with custom parameters."""
        custom_params = {
            'edge_thickness': 3,
            'color_smoothing': 5,
            'blur_strength': 2
        }

        result = filter_manager.apply_filter(sample_image, 'classic', custom_params)

        assert isinstance(result, np.ndarray)
        assert result.shape == sample_image.shape
        assert result.dtype == np.uint8

    def test_batch_process_images(self, filter_manager):
        """Test batch processing multiple images."""
        # Create multiple test images
        images = [np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8) for _ in range(3)]

        results = filter_manager.batch_process_images(images, 'classic')

        assert len(results) == len(images)
        for result in results:
            assert isinstance(result, np.ndarray)
            assert result.dtype == np.uint8

    def test_get_filter_preview_thumbnails(self, filter_manager, sample_image):
        """Test generating preview thumbnails."""
        thumbnails = filter_manager.get_filter_preview_thumbnails(sample_image)

        assert isinstance(thumbnails, dict)
        assert len(thumbnails) >= 1  # At least one thumbnail should be generated

        for filter_id, thumbnail in thumbnails.items():
            assert isinstance(thumbnail, np.ndarray)
            assert thumbnail.dtype == np.uint8

    def test_edge_cases_empty_parameters(self, filter_manager, sample_image):
        """Test filter application with empty parameters."""
        result = filter_manager.apply_filter(sample_image, 'classic', {})

        assert isinstance(result, np.ndarray)
        assert result.shape == sample_image.shape

    def test_edge_cases_none_parameters(self, filter_manager, sample_image):
        """Test filter application with None parameters."""
        result = filter_manager.apply_filter(sample_image, 'classic', None)

        assert isinstance(result, np.ndarray)
        assert result.shape == sample_image.shape

    def test_parameter_bounds(self, filter_manager, sample_image):
        """Test filters with extreme parameter values."""
        # Test with very low values
        low_params = {
            'edge_thickness': 1,
            'color_smoothing': 1,
            'blur_strength': 1
        }
        result_low = filter_manager.apply_filter(sample_image, 'classic', low_params)
        assert isinstance(result_low, np.ndarray)

        # Test with high values
        high_params = {
            'edge_thickness': 15,
            'color_smoothing': 15,
            'blur_strength': 10
        }
        result_high = filter_manager.apply_filter(sample_image, 'classic', high_params)
        assert isinstance(result_high, np.ndarray)

class TestFilterIntegration:
    """Integration tests for filter pipeline."""

    @pytest.fixture
    def filter_manager(self):
        return FilterManager()

    def test_filter_pipeline_consistency(self, filter_manager):
        """Test that the same input produces consistent output."""
        # Create a deterministic test image
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128

        # Apply the same filter twice
        result1 = filter_manager.apply_filter(image, 'classic')
        result2 = filter_manager.apply_filter(image, 'classic')

        # Results should be identical for the same input
        np.testing.assert_array_equal(result1, result2)

    def test_all_filters_produce_valid_output(self, filter_manager):
        """Test that all filters produce valid output."""
        # Create test image
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

        filters = filter_manager.get_available_filters()

        for filter_id in filters.keys():
            result = filter_manager.apply_filter(image, filter_id)

            # Check basic properties
            assert isinstance(result, np.ndarray)
            assert result.shape == image.shape
            assert result.dtype == np.uint8
            assert np.min(result) >= 0
            assert np.max(result) <= 255

    def test_filter_robustness_different_sizes(self, filter_manager):
        """Test filters with different image sizes."""
        sizes = [(50, 50), (100, 150), (200, 100)]

        for width, height in sizes:
            image = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
            result = filter_manager.apply_filter(image, 'classic')

            assert result.shape == image.shape

if __name__ == '__main__':
    # Run tests if script is executed directly
    pytest.main([__file__])
