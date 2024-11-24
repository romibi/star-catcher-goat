import os
import pickle
import sys

main_dir = os.path.split(os.path.abspath(__file__))[0]

HIGHSCORES_EASY = []
HIGHSCORES_NORMAL = []

def load_highscores(name):
    try:
        filename = os.path.join(main_dir, "recordings", name)

        with open(filename, "rb") as f:
            print(f"Loading {filename}")
            highscores = pickle.load(f)
            f.close()
            return highscores

    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)
        return []

def load_all_highscores():
    global HIGHSCORES_NORMAL, HIGHSCORES_EASY
    HIGHSCORES_NORMAL = load_highscores("highscores.pickle")
    HIGHSCORES_EASY = load_highscores("highscores_easy.pickle")


def persist_highscores(name, highscores):
    try:
        filename = os.path.join(main_dir, "recordings", name)
        filename_bak = f"{filename}.bak"

        if os.path.exists(filename_bak):
            os.remove(filename_bak)
        if os.path.exists(filename):
            os.rename(filename, filename_bak)

        with open(filename, "wb") as f:
            # noinspection PyTypeChecker
            pickle.dump(highscores, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()
            print(f"Saved {filename}")
    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)

def print_highscores(amount=10):
    print("HIGHSCORE Normal:")

    for x in range(amount):
        if x < len(HIGHSCORES_NORMAL):
            entry = HIGHSCORES_NORMAL[x]
            original_name = ""
            if "original_name" in entry:
                original_name = f" ({entry["original_name"]})"
            highscoretext = f"{x + 1: >2}. {entry['points']: >4} Punkte: {entry['name']: <10} am {entry['timestamp'].strftime('%d.%m.%Y %H:%M')}{original_name}"
            print(highscoretext)

    print("")

    print("HIGHSCORE Easy:")
    for x in range(amount):
        if x < len(HIGHSCORES_EASY):
            entry = HIGHSCORES_EASY[x]
            original_name = ""
            if "original_name" in entry:
                original_name = f" ({entry["original_name"]})"
            highscoretext = f"{x + 1: >2}. {entry['points']: >4} Punkte: {entry['name']: <10} am {entry['timestamp'].strftime('%d.%m.%Y %H:%M')}{original_name}"
            print(highscoretext)

def editEntry(list, index):
    entry = list[index]
    original_name = ""
    if "original_name" in entry:
        original_name = f" ({entry["original_name"]})"
    highscoretext = f"{index + 1: >2}. {entry['points']: >4} Punkte: {entry['name']: <10} am {entry['timestamp'].strftime('%d.%m.%Y %H:%M')}{original_name}"
    print(highscoretext)
    print("Currently only editing name supported. Enter new Name:")
    newName = input()
    if not "original_name" in list[index]:
        list[index]["original_name"] = list[index]["name"]
    list[index]["name"] = newName

def editOn(list):
    print("Which entry to edit?:")
    index = int(input())
    editEntry(list, index-1)

def edit():
    print("Which Highscore List to edit? (n=normal, e=easy)")
    selection = input()
    if selection == "n":
        editOn(HIGHSCORES_NORMAL)
    if selection == "e":
        editOn(HIGHSCORES_EASY)

def deleteEntry(list, index):
    entry = list[index]
    original_name = ""
    if "original_name" in entry:
        original_name = f" ({entry["original_name"]})"
    highscoretext = f"{index + 1: >2}. {entry['points']: >4} Punkte: {entry['name']: <10} am {entry['timestamp'].strftime('%d.%m.%Y %H:%M')}{original_name}"
    print(highscoretext)
    print("Delete this entry? (y/n)")
    if input()=="y":
        list.remove(list[index])

def deleteFrom(list):
    print("Which entry to edit?:")
    index = int(input())
    deleteEntry(list, index-1)


def delete():
    print("From which Highscore List to delete? (n=normal, e=easy)")
    selection = input()
    if selection == "n":
        deleteFrom(HIGHSCORES_NORMAL)
    if selection == "e":
        deleteFrom(HIGHSCORES_EASY)

def save():
    print("Which Highscore List to save? (n=normal, e=easy)")

    selection = input()
    if selection == "n":
        persist_highscores("highscores.pickle", HIGHSCORES_NORMAL)
    if selection == "e":
        persist_highscores("highscores_easy.pickle", HIGHSCORES_EASY)

def taskquery():
    print("Action? (e=edit, d=delete, s=save, l=reload, q=quit)")
    action = input()
    if action == "q":
        return False
    if action == "e":
        edit()
        return True
    if action == "d":
        delete()
        return True
    if action == "s":
        save()
        return True
    if action == "l":
        load_all_highscores()
        return  True
    print("Unknown action")
    return True


def main():
    load_all_highscores()
    print_highscores()
    print("")
    if (len(sys.argv)<2) or (sys.argv[1] != "-i"):
        print("For interactive modification call with -i")
        return
    while taskquery():
        print_highscores()
        print("")


# call the "main" function if running this script
if __name__ == "__main__":
    main()
