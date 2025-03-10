from cafi.errors.custom_exceptions import ValJsonEx
from cafi.library.loader import load_acr_db


def run() -> None:
    """
    Attempts to load the ACR database or handle version compatibility issues.

    This function is intended to be the entry point for running the application.
    Currently, it attempts to load the ACR
    database using the `load_acr_db()` function. If a `ValJsonEx` exception occurs,
    indicating that the installed cafi
    version is incompatible with the latest data, an appropriate error message is printed.

    Note:
        This function currently does not implement any additional functionality beyond
        the described behavior.

    Raises:
        ValJsonEx: If there is a compatibility issue between the installed cafi version
            and the latest data.
        Exception: Any unhandled exceptions raised by `load_acr_db()` will
            propagate upwards.

    Example:
        >>> run()
        # This will attempt to load the ACR database or print an error message
        # if incompatible versions are detected.
        # If an error occurs, it may output something like:
        # "installed cafi version is not compatible with the latest data"

    References:
        * `load_acr_db()`: Function responsible for loading the ACR database.
        * `ValJsonEx`: Exception raised when there's a version compatibility issue.
    """
    try:
        load_acr_db()
    except ValJsonEx:
        print("installed cafi version is not compatible with the latest data")


if __name__ == "__main__":
    run()
