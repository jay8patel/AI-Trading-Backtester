from .strategy_base import Strategy
from .strategies import MovingAverageCrossover, RSIReversal
from .data_loader import load_data, generate_synthetic_data

# Defines what is available when someone does: from src import *
__all__ = [
    'Strategy',
    'MovingAverageCrossover',
    'RSIReversal',
    'load_data',
    'generate_synthetic_data'
]