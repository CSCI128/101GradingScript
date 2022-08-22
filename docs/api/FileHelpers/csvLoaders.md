# csvLoaders module


### csvLoaders.loadCSV(_filename, promptIfError=False, directoriesToCheck=None)

* **Description**


This function validates that a CSV file with the name ‘_filename’ exists
If it does, it loads it in to a Pandas dataframe to be returned. In the event of an error,
an empty pandas dataframe is returned


* **Parameters**

    
    * **directoriesToCheck** (`Optional`[`list`[`str`]]) – See fileHelper.findFile


    * **promptIfError** (`bool`) – See fileHelper.findFile


    * **_filename** (`str`) – the csv filename to load



* **Returns**

    the dataframe from the csv or an empty dataframe if loaded failed



### csvLoaders.loadGradescope(_filename)

* **Description**


This function loads the selected gradescope CSV file, drops all unnecessary columns,
and converts the columns to the format that will be used later.

Remaps Lateness (H:M:S) -> Lateness -> (converts to hours) -> hours_late
Remaps Email -> (converts to multipass) -> multipass


* **Parameters**

    **_filename** – the filename of the assignment to be graded



* **Returns**

    the loaded gradescope dataframe



### csvLoaders.loadPageFlagging(_filename, _assignment)

* **Description**


**NOT IMPLEMENTED**

This is currently backlogged: see [#1](https://github.com/TriHardStudios/101GradingScript/issues/1)

This function loads the page flagging file, drops all rows whose assignment column does not correspond to the
selected assignment


* **Parameters**

    
    * **_filename** – 


    * **_assignment** – 



* **Returns**
