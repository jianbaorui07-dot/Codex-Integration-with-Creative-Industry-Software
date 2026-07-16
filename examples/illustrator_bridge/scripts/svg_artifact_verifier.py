"""Backward-compatible import for the package-level SVG verifier."""

from starbridge_mcp.vectorization.svg_verify import (
    SVG_NAMESPACE,
    SvgArtifactError,
    verify_svg_artifact,
)

__all__ = ["SVG_NAMESPACE", "SvgArtifactError", "verify_svg_artifact"]
