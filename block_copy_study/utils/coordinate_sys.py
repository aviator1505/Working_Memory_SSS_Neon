# coordinate_sys.py
# utils/coordinate_sys.py
import numpy as np
from scipy.spatial.transform import Rotation
from dataclasses import dataclass
from typing import Dict, Tuple, Optional


@dataclass
class CoordinateSystem:
    """Represents a 3D coordinate system with origin and orientation."""
    origin: np.ndarray  # 3D position
    orientation: np.ndarray  # 3x3 rotation matrix


class CoordinateTransformer:
    def __init__(self):
        """
        Handles coordinate system transformations between different sensors.
        Maintains relationships between coordinate frames and provides
        transformation utilities.
        """
        self.coordinate_systems = {}
        self.transformations = {}

    def add_coordinate_system(self, name: str, origin: np.ndarray,
                              orientation: np.ndarray):
        """
        Adds a new coordinate system to the transformer.

        Args:
            name: Identifier for the coordinate system
            origin: 3D position of origin
            orientation: 3x3 rotation matrix defining orientation
        """
        self.coordinate_systems[name] = CoordinateSystem(origin, orientation)

    def compute_transformation(self, from_sys: str, to_sys: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Computes transformation matrix and translation vector between coordinate systems.

        Args:
            from_sys: Source coordinate system name
            to_sys: Target coordinate system name

        Returns:
            Tuple containing:
            - 3x3 rotation matrix
            - 3D translation vector
        """
        if from_sys not in self.coordinate_systems or to_sys not in self.coordinate_systems:
            raise ValueError("Coordinate system not found")

        from_cs = self.coordinate_systems[from_sys]
        to_cs = self.coordinate_systems[to_sys]

        # Compute rotation matrix between systems
        rotation = to_cs.orientation @ from_cs.orientation.T

        # Compute translation vector
        translation = to_cs.origin - (rotation @ from_cs.origin)

        self.transformations[(from_sys, to_sys)] = (rotation, translation)
        return rotation, translation

    def transform_point(self, point: np.ndarray, from_sys: str,
                        to_sys: str) -> np.ndarray:
        """
        Transforms a point from one coordinate system to another.

        Args:
            point: 3D point to transform
            from_sys: Source coordinate system name
            to_sys: Target coordinate system name

        Returns:
            Transformed 3D point
        """
        if (from_sys, to_sys) not in self.transformations:
            self.compute_transformation(from_sys, to_sys)

        rotation, translation = self.transformations[(from_sys, to_sys)]
        return (rotation @ point) + translation

    def transform_orientation(self, orientation: np.ndarray, from_sys: str,
                              to_sys: str) -> np.ndarray:
        """
        Transforms an orientation matrix between coordinate systems.

        Args:
            orientation: 3x3 rotation matrix
            from_sys: Source coordinate system name
            to_sys: Target coordinate system name

        Returns:
            Transformed 3x3 rotation matrix
        """
        if (from_sys, to_sys) not in self.transformations:
            self.compute_transformation(from_sys, to_sys)

        rotation, _ = self.transformations[(from_sys, to_sys)]
        return rotation @ orientation

    def quaternion_to_matrix(self, quat: np.ndarray) -> np.ndarray:
        """Converts quaternion to rotation matrix."""
        return Rotation.from_quat(quat).as_matrix()

    def matrix_to_quaternion(self, matrix: np.ndarray) -> np.ndarray:
        """Converts rotation matrix to quaternion."""
        return Rotation.from_matrix(matrix).as_quat()

    def euler_to_matrix(self, angles: np.ndarray, sequence: str = 'xyz') -> np.ndarray:
        """
        Converts Euler angles to rotation matrix.

        Args:
            angles: Array of 3 Euler angles in radians
            sequence: Rotation sequence (e.g., 'xyz', 'zyx')
        """
        return Rotation.from_euler(sequence, angles).as_matrix()

    def matrix_to_euler(self, matrix: np.ndarray, sequence: str = 'xyz') -> np.ndarray:
        """
        Converts rotation matrix to Euler angles.

        Args:
            matrix: 3x3 rotation matrix
            sequence: Rotation sequence (e.g., 'xyz', 'zyx')

        Returns:
            Array of 3 Euler angles in radians
        """
        return Rotation.from_matrix(matrix).as_euler(sequence)