import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)


def show_tk_setup_help(error):
    print("\nThe desktop GUI is ready, but this Python installation is missing Tcl/Tk.")
    print("Install Python from python.org and keep 'tcl/tk and IDLE' selected.")
    print("Then choose that Python interpreter in VS Code and run Run_GUI.py again.\n")
    print(f"Technical detail: {error}")
    try:
        input("\nPress Enter to close...")
    except EOFError:
        pass


if __name__ == "__main__":
    try:
        from Financial_Planner_GUI import main
        main()
    except Exception as error:
        if "init.tcl" in str(error) or "Tcl" in type(error).__name__:
            show_tk_setup_help(error)
        else:
            raise
