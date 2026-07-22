import Key
import odszyfrowanie
import szyfrowanie
import ui
import time
import os
import saving
ACTIONS = {
    "1": Key.main,
    "2": szyfrowanie.main,
    "3": odszyfrowanie.main,
    "4": ui.main,
    "5": saving.main
}

def main () -> None:
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("""What do you want to do?
            1.Generate new key.
            2.Encrypt your message.
            3.Decrypt a message (Remember to have the same key as the sender of the message)
            4. Open UI
            5. Paste / save key
            0. exit
            """)
        choice = input("Choose a number: ").strip()
        if choice != "0" and choice not in ACTIONS:
            print("You must choose a number between 0 and 5")
            time.sleep(5)
            continue
        if choice == "0":
            break
        action = ACTIONS.get(choice)
        try:
            action()
        except SystemExit as error:
            print(error)
        input("\nPress Enter to return to the menu...")
if __name__ == "__main__":
    main()
