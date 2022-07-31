from Canvas import Canvas
import config
from UI.ui import mainMenu


def main():
    loadedConfig = config.loadConfig()
    print("Connecting to Canvas...")
    canvas = Canvas()
    canvas.loadSettings(loadedConfig)
    canvas.getAssignmentsFromConfig(loadedConfig)
    canvas.getStudentsFromCanvas()

    operation = mainMenu()
    if not operation(canvas):
        print("Grading failed.")


if __name__ == "__main__":
    main()
