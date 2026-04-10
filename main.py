# Hussein
# Entry point - launches the SmartBudget application

import sys
from database import initialize_database

def main():
    initialize_database()

    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        from cli import run_cli
        run_cli()
    else:
        import tkinter as tk
        from GUI import MainWindow
        root = tk.Tk()
        app = MainWindow(root)
        root.mainloop()

if __name__ == "__main__":
    main()