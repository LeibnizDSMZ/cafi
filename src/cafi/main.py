from cafi.errors.custom_exceptions import ValJsonEx
from cafi.library.loader import load_acr_db


def run() -> None:
    # TODO no real functionality yet
    try:
        load_acr_db()
    except ValJsonEx:
        print("installed cafi version is not compatible with the latest data")


if __name__ == "__main__":
    run()
