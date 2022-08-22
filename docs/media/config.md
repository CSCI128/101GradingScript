# config module


### config.createNewConfig()
Creates a new config file.
Config file must contain an api key,
the course ID, the user ID, and the canvas endpoint.
It also must contain the assignment list.
This function walks the user through the creation, and builds a new config file to be saved and loaded.


### config.loadConfig()
This function gets the list of available config files and prompts the user to create a new file if none exist
or choose file to open from a list. If only one file exists then it will load that file by default.
Returns the loaded config file. (unless one isnt created, in which case it exits the program)


### config.locateConfigFiles()
This function reads the config files from the ‘./config/’ directory.
It filters out any non files and any files that don’t end in .json
Returns the number of found files and a list of the files


### config.readConfig(_configFileName)
This function reads the config from the disk and converts it to a python dictionary.
PARAMS:

> _configFileName - The file name to load
