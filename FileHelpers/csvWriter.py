import pandas as pd
import csv


def csvWriter(_filename: str, _data: (pd.DataFrame, list)) -> bool:
    if _filename is None or _data is None:
        raise AttributeError("Both _filename AND _data must be defined")

    if _filename[len(_filename) - 3:] != "csv":
        _filename += ".csv"

    if isinstance(_data, list):
        try:
            with open(_filename, "w", newline="\n") as fileOut:
                writer = csv.writer(fileOut)
                writer.writerows(_data)
        except IOError as e:
            print(f"Unable to write '{_filename}' to file due to {e}")
            return False

    elif isinstance(_data, pd.DataFrame):
        try:
            with open(_filename, "w", newline='\n') as fileOut:
                _data.to_csv(path_or_buf=fileOut, index=False)
        except IOError as e:
            print(f"Unable to write '{_filename}' to file due to {e}")
            return False
    else:
        print(f"Unsupported data type. Type is: {type(_data)}")
        return False

    return True
