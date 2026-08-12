"""
Toonify Image Processing Utilities

This package contains the core image processing and filter implementations
for the Toonify cartoon image application.
"""

from .image_processing import ImageProcessor
from .filters import FilterManager

__all__ = ['ImageProcessor', 'FilterManager']
__version__ = '1.0.0'
