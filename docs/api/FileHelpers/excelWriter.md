# excelWriter module


### excelWriter.applyStylingForSpecialCases(_specialCasesDF)

* **Description**


This function converts a dataframe to a style frame and applies the styling for special cases.
After the initial styling is done, it finalizes the data using the finalizeSpecialCases function


* **Parameters**

    **_specialCasesDF** (`DataFrame`) – the special cases dataframe to be styled.



* **Return type**

    `StyleFrame`



* **Returns**

    the styled dataframe in the format of a styleframe.



### excelWriter.excelWriter(_filename, _data)

* **Description**


Writes a style frame (a stylized dataframe) to disk (All formatting must be applied) or
a raw dataframe.


* **Parameters**

    
    * **_filename** (`str`) – The filename to write. Checks to make sure extension is .xlsx, if it isn’t - add it.


    * **_data** ((`StyleFrame`, `DataFrame`)) – the data to write. Must be either a styleframe or a dataframe.



* **Return type**

    `bool`



* **Returns**

    True if write was successful. False if not.



### excelWriter.finalizeSpecialCases(_specialCasesSF)

* **Description**


This function updates the coloring for each row - and if the department wants it, locks the correctly handled
ones.
:type _specialCasesSF: `StyleFrame`
:param _specialCasesSF: The dataframe (technically a styleframe) to finalize


* **Return type**

    `StyleFrame`



* **Returns**

    the finalized styled dataframe



### excelWriter.writeSpecialCases(_filename, _specialCasesDF)

* **Description**


This is the specialized function for writing special cases to file. It runs the updates to the dataframe to ready it
for writing, and calls the helper methods to correctly style it. Calls excelWriter internally actually write


* **Parameters**

    
    * **_filename** (`str`) – The file name to write. If it doesn’t contain the correct file extension (.xlsx) it will be added


    * **_specialCasesDF** (`DataFrame`) – The data to write.



* **Return type**

    `bool`



* **Returns**

    True if it was able to write successfully, false if not.
