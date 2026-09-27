# picks control or data service based on SERVICE env var, used by docker
import os
import sys

SERVICE = os.environ.get("SERVICE", "control")


def run_control():
    from control_plane import control_plane as cp

    cp.run_control({"name": "container-run", "fail_step": False})


def run_data():
    from data_plane import data_plane as dp

    print(dp.fetch_data({"url": "http://example.com"}))


def main():
    if SERVICE == "control":
        run_control()
    elif SERVICE == "data":
        run_data()
    else:
        print(f"Unknown SERVICE={SERVICE}")
        sys.exit(2)


if __name__ == "__main__":
    main()
