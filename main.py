import pandas as pd

from FileHelpers import csvLoaders
from Grade import post, score, grade
from Canvas import Canvas
import config


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
