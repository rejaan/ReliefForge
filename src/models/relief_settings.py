from dataclasses import dataclass


@dataclass(slots=True)
class ReliefSettings:
    """Configuration for generating a sliced relief model."""

    slice_count: int = 80
    model_width_mm: float = 180.0

    base_thickness_mm: float = 2.0
    relief_depth_mm: float = 12.0

    slice_thickness_mm: float = 0.8
    slice_spacing_mm: float = 1.0
    depth_contrast: float = 1.0

    base_plate_enabled: bool = True
    base_plate_thickness_mm: float = 2.0
    base_plate_margin_mm: float = 1.0

    mirror_horizontal: bool = True
    background_cutoff: float = 0.08

    invert: bool = True
    blur_kernel: int = 3
    equalize_histogram: bool = True

    engine_version: str = "v3"