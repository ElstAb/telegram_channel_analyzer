import sys

from app.console.access_manager import (
    show_access_list,
    add_access_menu,
    remove_access_menu
)

from app.core.shutdown import shutdown_app


def start_console():
    """
    Main admin console loop.
    """

    while True:

        print("\n========= ADMIN MENU =========")
        print("1. Show access list")
        print("2. Add user access to channel")
        print("3. Remove user access from channel")
        print("4. Shutdown application")

        choice = input("\nChoose option: ").strip()

        try:

            if choice == "1":
                show_access_list()

            elif choice == "2":
                add_access_menu()

            elif choice == "3":
                remove_access_menu()

            elif choice == "4":
                confirm_shutdown()

            else:
                print("Invalid option")

        except Exception as e:
            print("Error:", e)


def confirm_shutdown():
    """
    Ask confirmation before shutting down application.
    Default answer is No.
    """

    confirm = input(
        "\nAre you sure you want to shutdown the application? (y/N): "
    ).strip().lower()

    if confirm == "y":

        print("\nShutting down application...")

        shutdown_app()

    else:

        print("Shutdown cancelled")