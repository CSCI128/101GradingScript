# excelLoaders module


### excelLoaders.loadExcel(_filename, promptIfError=False, directoriesToCheck=None)

* **Description**


This function validates that an Excel file with the name _filename exists
If it does, it loads it in to a Pandas dataframe to be returned. In the event of an error,
an empty pandas dataframe is returned

Calls `fileHelper.findFile` internally


* **Parameters**
    
    * **directoriesToCheck** (`Optional`[`list`[`str`]]) – `fileHelper.findFile`

    * **promptIfError** (`bool`) – `fileHelper.findFile`

    * **_filename** – the Excel filename to load



* **Returns**

    the dataframe from the Excel file or an empty dataframe if loaded failed



### excelLoaders.loadSpecialCases()

* **Description**


This function loads the special cases file.

This function attempts to automatically load special cases from “./special_cases/special_cases.xlsx” or prompts the
user to enter a path if it cant be found


* **Returns**

    the special cases dataframe
