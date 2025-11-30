from vlt.data.assign import assign

def basicuitools_defs(**kwargs):
    """
    BASICUITOOLS_DEFS - Basic user interface uitools setup

    uidefs = vlt.ui.basicuitools_defs(**kwargs)

    Returns a basic defined set of specifications for the commonly used
    user interface controls.

    The foreground and background colors are compatible with the current
    Matlab version (simulated).

    This function also accepts name/value pairs that modify the default options.
    kwargs:
      callbackstr ('')                 :  Callback function for all active controls
      uiBackgroundColor (0.94*[1 1 1]) :  Background color for all except 'frame'
      frameBackgroundColor(0.8*[1 1 1]):  Background color for 'frame'
      uiUnits ('pixels')               :  Units for controls

    Returns:
      uidefs (dict): Dictionary of UI definitions.
    """

    # Defaults
    callbackstr = ''
    uiBackgroundColor = [0.94, 0.94, 0.94]
    frameBackgroundColor = [0.8, 0.8, 0.8]
    uiUnits = 'pixels'

    # Process kwargs manually to override local vars?
    # assign(kwargs) functionality?
    # vlt.data.assign updates locals of caller?
    # In Python, we can't easily update locals.
    # We should use kwargs directly.

    if 'callbackstr' in kwargs: callbackstr = kwargs['callbackstr']
    if 'uiBackgroundColor' in kwargs: uiBackgroundColor = kwargs['uiBackgroundColor']
    if 'frameBackgroundColor' in kwargs: frameBackgroundColor = kwargs['frameBackgroundColor']
    if 'uiUnits' in kwargs: uiUnits = kwargs['uiUnits']

    # Define structs (dictionaries)

    button = {}
    button['Units'] = uiUnits
    button['BackgroundColor'] = uiBackgroundColor
    button['HorizontalAlignment'] = 'center'
    button['Callback'] = callbackstr
    button['Style'] = 'pushbutton'

    togglebutton = button.copy()
    togglebutton['HorizontalAlignment'] = 'left'
    togglebutton['Style'] = 'togglebutton'

    txt = {}
    txt['Units'] = uiUnits
    txt['BackgroundColor'] = uiBackgroundColor
    txt['fontsize'] = 12
    txt['fontweight'] = 'normal'
    txt['HorizontalAlignment'] = 'left'
    txt['Style'] = 'text'

    edit = txt.copy()
    edit['BackgroundColor'] = [1, 1, 1]
    edit['Style'] = 'Edit'

    popup = txt.copy()
    popup['style'] = 'popupmenu' # MATLAB uses lowercase style usually? Code says 'popupmenu'
    # Wait, 'style' vs 'Style'. MATLAB is case insensitive for properties?
    # Code uses: popup.style = 'popupmenu'. txt.Style='text'.
    # Python dict keys are case sensitive.
    # We should replicate keys exactly if possible, or normalize?
    # Let's replicate exact keys from MATLAB source if possible.
    # txt.Style='text'. popup.style='popupmenu'.
    # In Python we probably want consistency.
    # I'll use 'Style' for all property names if they are standard MATLAB properties.
    # But here I'll follow the source: popup.style (lowercase)
    popup['style'] = 'popupmenu'
    popup['Callback'] = callbackstr

    slider = txt.copy()
    slider['Style'] = 'slider'
    slider['Callback'] = callbackstr

    list_ui = txt.copy() # 'list' is reserved
    list_ui['style'] = 'list'
    list_ui['Callback'] = callbackstr

    cb = txt.copy()
    cb['Style'] = 'Checkbox'
    cb['Callback'] = callbackstr
    cb['fontsize'] = 12

    rb = cb.copy()
    rb['Style'] = 'radiobutton'

    frame = txt.copy()
    frame['BackgroundColor'] = frameBackgroundColor
    frame['Style'] = 'frame'

    uidefs = {
        'button': button,
        'togglebutton': togglebutton,
        'txt': txt,
        'edit': edit,
        'popup': popup,
        'slider': slider,
        'list': list_ui,
        'cb': cb,
        'rb': rb,
        'frame': frame
    }

    return uidefs
