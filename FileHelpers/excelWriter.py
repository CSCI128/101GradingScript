import pandas as pd
from styleframe import StyleFrame, Styler, utils


def finalize(_specialCasesSF: StyleFrame) -> StyleFrame:
    """
    This function updates the coloring for each row - and if the department wants it, locks the correctly handled
    ones.

    :param _specialCasesSF: The dataframe (technically a styleframe) to finalize
    :return: the styled dataframe
    """
    if not isinstance(_specialCasesSF, StyleFrame):
        raise AttributeError("Unable able to apply style to non StyleFrame object")

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


def applyStyling(_specialCasesDF: pd.DataFrame):
    defaultStyling: Styler = Styler(
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

    specialCasesSF = finalize(specialCasesSF)

    return specialCasesSF


def writeSpecialCases(_filename: str, _specialCasesDF: pd.DataFrame) -> bool:
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

    specialCasesSF = applyStyling(_specialCasesDF)

    return excelWriter(_filename, specialCasesSF)


def excelWriter(_filename: str, _data: StyleFrame)  -> bool:
    if _filename is None or _data is None:
        raise AttributeError("Both _filename AND _data must be defined")

    if _filename[len(_filename) - 4:] != "xlsx":
        _filename += ".xlsx"

    if isinstance(_data, StyleFrame):
        try:
            ew = pd.ExcelWriter(_filename)
            _data.to_excel(excel_writer=ew, merge_cells=True, index=False)
            ew.save()
        except IOError as e:
            print(f"Unable to write '{_filename}' to file due to {e}")
            return False

    return True
