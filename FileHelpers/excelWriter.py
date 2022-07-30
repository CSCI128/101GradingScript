import pandas as pd
from styleframe import StyleFrame, Styler, utils


def finalizeSpecialCases(_specialCasesSF: StyleFrame) -> StyleFrame:
    """
    This function updates the coloring for each row - and if the department wants it, locks the correctly handled
    ones.
    :param _specialCasesSF: The dataframe (technically a styleframe) to finalize
    :return: the finalized styled dataframe
    """
    if not isinstance(_specialCasesSF, StyleFrame):
        raise AttributeError("Unable able to apply style to non StyleFrame object")

    # If the department wants special cases to be locked after they are applied -
    #  add protect = True to the success column
    successCol: Styler = Styler(bg_color="#E2EFDA", font_color=utils.colors.black)
    failureCol: Styler = Styler(bg_color="#EACCCC", font_color=utils.colors.black)

    _specialCasesSF.apply_style_by_indexes(
        indexes_to_style=_specialCasesSF[_specialCasesSF['handled'] == "TRUE"],
        styler_obj=successCol,
        overwrite_default_style=False
    )
    _specialCasesSF.apply_style_by_indexes(
        indexes_to_style=_specialCasesSF[_specialCasesSF['handled'] == "FALSE"],
        styler_obj=failureCol,
        overwrite_default_style=False
    )

    return _specialCasesSF


def applyStylingForSpecialCases(_specialCasesDF: pd.DataFrame) -> StyleFrame:
    """
    This function converts a dataframe to a style frame and applies the styling for special cases.
    After the initial styling is done, it finalizes the data using the finalizeSpecialCases function
    :param _specialCasesDF: the special cases dataframe to be styled.
    :return: the styled dataframe in the format of a styleframe.
    """
    # Every cell in the sheet gets this style unless overridden. This library is kinda crap, so I can't apply boarder
    #  and style at the same time, unless im ok with bold black boarders - which im not.
    defaultStyling: Styler = Styler(  # this is mostly overriding the default parameters that styleframe uses.
        font=utils.fonts.calibri,
        font_size=11.0,
        wrap_text=False,
        shrink_to_fit=False,
        horizontal_alignment=utils.horizontal_alignments.right,
        border_type=None,
    )

    specialCasesSF: StyleFrame = StyleFrame(_specialCasesDF, styler_obj=defaultStyling)

    specialCasesSF.apply_headers_style(styler_obj=Styler.combine(defaultStyling, Styler(bold=True)))
    specialCasesSF.set_column_width(specialCasesSF.columns, width=17.5)

    specialCasesSF = finalizeSpecialCases(specialCasesSF)

    return specialCasesSF


def writeSpecialCases(_filename: str, _specialCasesDF: pd.DataFrame) -> bool:
    """
    This is the specialized function for writing special cases to file. It runs the updates to the dataframe to ready it
    for writing, and calls the helper methods to correctly style it. Calls excelWriter internally actually write
    :param _filename: The file name to write. If it doesn't contain the correct file extension (.xlsx) it will be added
    :param _specialCasesDF: The data to write.
    :return: True if it was able to write successfully, false if not.
    """
    if _filename is None or _specialCasesDF is None:
        raise AttributeError("Both _filename AND _specialCasesDF must be defined")

    if not isinstance(_specialCasesDF, pd.DataFrame):
        raise AttributeError("Special Cases MUST be passed as a pandas dataframe")

    # So excel and python dont really get along great - but if all numbers are stored as strings
    #  then there are less issues
    _specialCasesDF['new_due_date'] = _specialCasesDF['new_due_date'].dt.strftime("%m/%d/%y")
    _specialCasesDF['extension_days'] = _specialCasesDF['extension_days'].astype(str)
    _specialCasesDF.columns = _specialCasesDF.columns.str.replace('_', ' ')
    _specialCasesDF.drop(columns={'multipass'}, inplace=True)

    specialCasesSF = applyStylingForSpecialCases(_specialCasesDF)

    return excelWriter(_filename, specialCasesSF)


def excelWriter(_filename: str, _data: (StyleFrame, pd.DataFrame)) -> bool:
    """
    Writes a style frame (a stylized dataframe) to disk (All formatting must be applied) or
    a raw dataframe.
    :param _filename: The filename to write. Checks to make sure extension is .xlsx, if it isn't - add it.
    :param _data: the data to write. Must be either a styleframe or a dataframe.
    :return: True if write was successful. False if not.
    """
    if _filename is None or _data is None:
        raise AttributeError("Both _filename AND _data must be defined")

    if _filename[len(_filename) - 4:] != "xlsx":
        _filename += ".xlsx"

    # both the styleframe and dataframe use the same pandas excel writer, but incase I want to add support for different
    #  processing for each type I have broken them out
    if isinstance(_data, StyleFrame):
        try:
            ew = pd.ExcelWriter(_filename)
            _data.to_excel(excel_writer=ew, merge_cells=True, index=False, allow_protection=True)
            ew.save()
        except IOError as e:
            print(f"Unable to write '{_filename}' to file due to {e}")
            return False
    elif isinstance(_data, pd.DataFrame):
        try:
            ew = pd.ExcelWriter(_filename)
            _data.to_excel(excel_writer=ew, merge_cells=True, index=False)
            ew.save()
        except IOError as e:
            print(f"Unable to write '{_filename}' to file due to {e}")
            return False
    else:
        return False

    return True
