from dataclasses import dataclass


@dataclass(slots=True)
class ReliefSettings:
    """Configuration for generating a relief model."""

    slice_count: int = 80
    model_width_mm: float = 180.0
    base_thickness_mm: float = 2.0
    relief_depth_mm: float = 12.0
    invert: bool = True

    blur_kernel: int = 3
    equalize_histogram: bool = True