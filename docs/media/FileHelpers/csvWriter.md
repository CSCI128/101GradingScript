# csvWriter module


### csvWriter.csvWriter(_filename, _data)

* **Description**


Writes the data to a csv file. The data can either be a Dataframe where this will use the Pandas `to_csv` method
or a list where it will use the built-in csv handling functionality


* **Parameters**

    
    * **_filename** (`str`) – The filename to write. Checks to make sure extension is .csv if it isn’t - add it.


    * **_data** ((`DataFrame`, `list`)) – the data to write. Must be either a dataframe or list



* **Return type**

    `bool`



* **Returns**

    True if write was successful. False if not.
