# hardware/__init__.py
from .eye_tracker import NeonEyeTracker
from .motion_tracker import MotionTracker
from .synchronizer import DataSynchronizer

# This allows users to import directly from the hardware package
__all__ = ['NeonEyeTracker', 'MotionTracker', 'DataSynchronizer']