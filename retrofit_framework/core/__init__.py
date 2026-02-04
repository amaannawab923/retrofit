"""
Core retrofit conversion algorithms for transforming legacy warehouses
into robotic-accommodated warehouses.

This package provides the fundamental algorithms for:
- Navigation graph construction
- Distance matrix calculations
- Zone analysis
- Retrofit conversion logic
"""

from .converter import RetrofitConverter

__all__ = [
    'RetrofitConverter',
]

__version__ = '1.0.0'
