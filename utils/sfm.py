from utils.logger import get_logger

logger = get_logger()

try:
    # using the rust module
    import fuzzy_string_matcher as sfm  # type: ignore[import]

    logger.debug("Using Rust utils module")
except ImportError:
    # fallback to the python module
    import utils.string_fuzzy_matcher as sfm  # type: ignore[no-redef]

    logger.debug(
        "Rust implementation <fuzzy_string_matcher> not found using "
        "Python implementation <utils.string_fuzzy_matcher>",
    )

__all__ = ["sfm"]
