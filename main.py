import os
import sys
from Canvas import Canvas
import config
from UI.ui import mainMenu

def main():
    # TODO May want to rework this config loading!
    loadedConfig = config.loadConfig()
    # TODO Should this be moved to after the action is taken?

    print("Connecting to Canvas...")
    canvas = Canvas()
    canvas.loadSettings(loadedConfig)
    canvas.getAssignmentsFromConfig(loadedConfig)
    canvas.getStudentsFromCanvas()

    operation = mainMenu()
    if not operation(canvas=canvas, latePenalty=loadedConfig['late_penalties']):
        print("Grading failed.")


if __name__ == "__main__":
    # when the program is compiled, it will execute in a tmp folder, which is unhelpful when reading data in
    #  so to work around that, we are checking to see if we are running in that mode, then updating the current working
    #  directory to be where the app is downloaded.

    if getattr(sys, 'frozen', False):
        # print(os.path.dirname(sys.executable))
        os.chdir(os.path.dirname(sys.executable))
    main()
