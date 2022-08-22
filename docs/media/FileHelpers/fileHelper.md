# fileHelper module


### fileHelper.findFile(_filename, promptIfError=False, directoriesToCheck=None)

* **Description**


This function attempts to automatically locate the file in a few different places:
./, ./grades/, ./canvas/, ./gradescope/, ./special_cases/


* **Parameters**

    
    * **directoriesToCheck** (`Optional`[`list`[`str`]]) – The directories to search


    * **promptIfError** (`bool`) – If we should prompt the user for a file name if we fail to locate the file


    * **_filename** (`str`) – the file name to search for



* **Returns**

    the file name with the found directory prepended
