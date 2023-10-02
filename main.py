import os
import sys
from typing import Optional
from AzureAD import AzureAD
from Bartik.Bartik import Bartik
from Canvas import Canvas
import config
from UI.ui import mainMenu
import asyncio

async def main():
    # TODO May want to rework this config loading!
    loadedConfig = config.loadConfig()
    # TODO Should this be moved to after the action is taken?

    print("Connecting to Canvas...")
    canvas = Canvas()
    canvas.loadSettings(loadedConfig)
    canvas.getAssignmentsFromConfig(loadedConfig)
    canvas.getStudentsFromCanvas()

    azure: Optional[AzureAD] = None
    bartik: Optional[Bartik] = None

    if "tenant_id" in loadedConfig.keys():
        azure = AzureAD(loadedConfig["tenant_id"])

    if "bartik_url" in loadedConfig.keys() \
        and "bartik_username" in loadedConfig.keys() \
        and "bartik_password" in loadedConfig.keys() \
        and "bartik_course" in loadedConfig.keys():
        bartik = Bartik(loadedConfig["bartik_url"], loadedConfig["bartik_username"], loadedConfig["bartik_password"], loadedConfig['bartik_course'])

    operation = mainMenu()
    if not await operation(canvas=canvas, azure=azure, bartik=bartik, latePenalty=loadedConfig['late_penalties']):
        print("Grading failed.")


if __name__ == "__main__":
    # when the program is compiled, it will execute in a tmp folder, which is unhelpful when reading data in
    #  so to work around that, we are checking to see if we are running in that mode, then updating the current working
    #  directory to be where the app is downloaded.

    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    asyncio.run(main())
