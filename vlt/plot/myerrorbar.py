import numpy as np
import matplotlib.pyplot as plt

def myerrorbar(*args, **kwargs):
    """
    MYERRORBAR Error bar plot.

    This function ports vlt.plot.myerrorbar to Python.

    It plots the graph of vector X vs. vector Y with error bars specified by
    lower and upper error ranges.

    Usage:
        h = myerrorbar(x, y, l, u, symbol, tt)
        h = myerrorbar(x, y, e)
        h = myerrorbar(y, e)

    Arguments:
        x, y: Data coordinates (array-like)
        l, u: Lower and upper error ranges (or symmetric error e) (array-like)
        symbol: Line specification (e.g. 'r-') (string)
        tt: Tee width (capsize) in x-axis units. (float)

    Returns:
        h: A tuple containing the errorbar container.
    """

    # Argument parsing
    # The MATLAB function is extremely flexible with arguments.
    # We will try to map common use cases.

    x = None
    y = None
    l = None
    u = None
    symbol = None
    tt = None

    # args can have variable length.
    # Case 1: errorbar(y, e) -> 2 args
    # Case 2: errorbar(x, y, e) -> 3 args
    # Case 3: errorbar(x, y, l, u) -> 4 args
    # Plus optional symbol and tt.

    # Helper to check if string
    def is_str(s):
        return isinstance(s, str)

    parsed_args = list(args)

    if len(parsed_args) >= 1:
        # Check if first arg is y or x.
        # If 2 args, and second is e, then first is y.
        # But MATLAB says:
        # if min(size(x))==1 -> vector
        #   if nargin > 2...
        pass

    # Re-implementing logic based on MATLAB source structure

    # We need to handle arguments robustly.
    # Let's try to detect based on types and length.

    # MATLAB:
    # if nargin == 2: l=y; u=y; y=x; x=1:npt; symbol='-';
    # This implies input was (y, e) actually. Because y becomes x (data), and l/u become what was in y (error).
    # Wait, the MATLAB code says:
    # if nargin == 2
    #    l = y;
    #    u = y;
    #    y = x;
    #    ...
    # This means call was myerrorbar(data, error).
    # Then y (data) -> x
    #      l/u (error) -> y
    # This seems backwards variable naming in the swap, but let's trace:
    # INPUT: myerrorbar(A, B)
    # x = A, y = B.
    # l = B; u = B;
    # y = A;
    # x = 1:length(A)
    # So effectively: x=index, y=A, error=B.

    # if nargin == 3
    #   if ~isstr(l) (arg 3)
    #      u = l; symbol = '-';
    #      This is (x, y, e). x=x, y=y, l=e, u=e.
    #   else (arg 3 is string)
    #      symbol = l;
    #      l = y; u = y; y = x; x = 1:npt;
    #      This is (y, e, symbol).

    # if nargin == 4
    #   if isstr(u) (arg 4)
    #      symbol = u; u = l;
    #      This is (x, y, e, symbol) -> x, y, l=e, u=e.
    #   else
    #      symbol = '-';
    #      This is (x, y, l, u).

    args_list = list(args)
    nargs = len(args_list)

    # Initialize variables with provided args to start matching MATLAB logic
    val_x = args_list[0] if nargs > 0 else None
    val_y = args_list[1] if nargs > 1 else None
    val_l = args_list[2] if nargs > 2 else None
    val_u = args_list[3] if nargs > 3 else None
    val_symbol = args_list[4] if nargs > 4 else None
    val_tt = args_list[5] if nargs > 5 else None

    # Logic blocks

    # Check dimensions of val_x (first arg)
    x_is_vector = False
    if val_x is not None:
         x_arr = np.array(val_x)
         if x_arr.ndim == 1 or min(x_arr.shape) == 1:
             x_is_vector = True

    # MATLAB logic implementation

    # Default values
    real_x = None
    real_y = None
    real_l = None
    real_u = None
    real_symbol = '-'
    real_tt = None

    # Handle the swapping logic

    if nargs == 2:
        # myerrorbar(y, e)
        # x passed as val_x (y data), y passed as val_y (error)
        real_l = val_y
        real_u = val_y
        real_y = val_x
        # real_x generated later
        real_symbol = '-'

    elif nargs == 3:
        if not is_str(val_l):
            # myerrorbar(x, y, e)
            real_u = val_l
            real_l = val_l
            real_x = val_x
            real_y = val_y
            real_symbol = '-'
        else:
            # myerrorbar(y, e, symbol)
            # passed: val_x=y, val_y=e, val_l=symbol
            real_symbol = val_l
            real_l = val_y
            real_u = val_y
            real_y = val_x
            # real_x generated later

    elif nargs == 4:
        if is_str(val_u):
            # myerrorbar(x, y, e, symbol)
            # passed: val_x=x, val_y=y, val_l=e, val_u=symbol
            real_symbol = val_u
            real_u = val_l
            real_l = val_l
            real_x = val_x
            real_y = val_y
        else:
            # myerrorbar(x, y, l, u)
            real_x = val_x
            real_y = val_y
            real_l = val_l
            real_u = val_u
            real_symbol = '-'

    else:
        # 5 or 6 args
        # myerrorbar(x, y, l, u, symbol, tt)
        real_x = val_x
        real_y = val_y
        real_l = val_l
        real_u = val_u
        if nargs >= 5:
            real_symbol = val_symbol
        else:
            real_symbol = '-'
        if nargs >= 6:
            real_tt = val_tt

    # Generate x if needed
    if real_x is None:
        if real_y is not None:
             real_y = np.array(real_y)
             npt = real_y.shape[0] # Assuming first dim is samples if vector
             # MATLAB: [npt, n] = size(y); x(:) = (1:npt)'*ones(1,n);
             # If y is 1D, shape (N,). If 2D (N, M).
             if real_y.ndim == 1:
                 real_x = np.arange(1, npt + 1)
             else:
                 # If matrix, x needs to be matrix or vector?
                 # MATLAB says x(:) = (1:npt)'*ones(1,n).
                 # So x matches y shape.
                 npt, n = real_y.shape
                 real_x = np.tile(np.arange(1, npt + 1).reshape(-1, 1), (1, n))

    # Ensure numpy arrays
    real_x = np.array(real_x)
    real_y = np.array(real_y)
    real_l = np.array(real_l)
    real_u = np.array(real_u)

    # Handle absolute values for errors as per MATLAB
    real_u = np.abs(real_u)
    real_l = np.abs(real_l)

    # Parse symbol (LineSpec)
    # Matplotlib errorbar accepts 'fmt' which is similar to symbol.

    # Handle 'tt' (tee width)
    # MATLAB uses tt in x-units. Matplotlib uses capsize in points.
    # This is a significant difference.
    # If we want exact visual replication, we might need to calculate how many points correspond to the data unit.
    # However, for a port, passing capsize is often sufficient.
    # But if tt is provided, we should try to use it.
    # If tt is not provided, MATLAB defaults to (max(x)-min(x))/100.

    capsize = None
    if real_tt is not None:
        # User provided explicit tee width in data units.
        # This is hard to map to points without the axes transform, which requires drawing first.
        # We will ignore the exact data-unit mapping for now and just set a default capsize or ignore it
        # unless we want to draw the bars manually like MATLAB does.
        # The MATLAB code *manually* draws the error bars using plot lines.
        # It constructs `xb` and `yb` vectors with NaNs to draw the lines.
        # To be faithful to the "port", maybe we should do the same?
        # The prompt asks to port the function.
        # If I use `plt.errorbar`, I get native behavior which is usually better, but `myerrorbar` might be used
        # precisely because they want that specific control (e.g. `tt` in data units).

        # If `tt` is specified, it sets the width of the cap in data units.
        # Standard matplotlib `capsize` is in points (pixels/static size), not data units.
        # If the user zooms in, `capsize` stays same size in pixels, but `tt` (data units) would zoom.
        # This suggests `myerrorbar` intends for the caps to be part of the data scaling.

        # Let's try to implement the manual drawing if possible, or fallback to errorbar.
        # The MATLAB code implementation is actually quite simple: it constructs the line data.
        # It returns a handle to the lines.
        pass

    # Let's implement the manual drawing approach as it preserves the exact behavior of `tt` being in data units.

    if real_tt is None:
         # Default tee
         if real_x.size > 0:
             tee = (np.max(real_x) - np.min(real_x)) / 100.0
         else:
             tee = 0.1 # Fallback
    else:
         tee = 0.5 * real_tt

    # Dimensions
    # MATLAB:
    # xb = zeros(npt*9,n); ...
    # It interleaves x, x, NaN, x-tee, x+tee, NaN, x-tee, x+tee, NaN
    # yb = ytop, ybot, NaN, ytop, ytop, NaN, ybot, ybot, NaN

    # Let's handle the 1D case and ND case.
    # Flatten if 1D for easier processing, or treat everything as columns.

    if real_y.ndim == 1:
        # Convert to column vector (N, 1)
        real_y = real_y.reshape(-1, 1)
        real_x = real_x.reshape(-1, 1)
        real_l = real_l.reshape(-1, 1)
        real_u = real_u.reshape(-1, 1)

    npt, n = real_y.shape

    ytop = real_y + real_u
    ybot = real_y - real_l
    xl = real_x - tee
    xr = real_x + tee

    # Construct xb and yb
    # rows = npt * 9
    # cols = n

    xb = np.zeros((npt * 9, n))
    yb = np.zeros((npt * 9, n))
    nan_row = np.full((1, n), np.nan)

    # We can vectorize this construction
    # x (center)
    xb[0::9, :] = real_x
    xb[1::9, :] = real_x
    xb[2::9, :] = np.nan
    # top bar
    xb[3::9, :] = xl
    xb[4::9, :] = xr
    xb[5::9, :] = np.nan
    # bottom bar
    xb[6::9, :] = xl
    xb[7::9, :] = xr
    xb[8::9, :] = np.nan

    yb[0::9, :] = ytop
    yb[1::9, :] = ybot
    yb[2::9, :] = np.nan
    yb[3::9, :] = ytop
    yb[4::9, :] = ytop
    yb[5::9, :] = np.nan
    yb[6::9, :] = ybot
    yb[7::9, :] = ybot
    yb[8::9, :] = np.nan

    # Parsing symbol for color/linestyle/marker
    # Matplotlib's plot function handles "fmt" string.
    # But we need to separate marker for the data points vs line for the bars.
    # MATLAB:
    # [ls,col,mark,msg] = colstyle(symbol);
    # symbol = [ls mark col]; % Use marker only on data part
    # esymbol = ['-' col]; % Make sure bars are solid

    # We need to parse the fmt string to extract color.
    # This is non-trivial in Python without a helper.
    # However, `plt.plot` returns the lines, and we can inspect them.
    # Or we can just pass the symbol to the data plot, get the color, and use it for the error bars.

    # Plot bars first (solid line, same color)
    # But we don't know the color yet if it's in the symbol (e.g. 'r-').

    # Strategy:
    # 1. Plot the data points (x, y) with `symbol`.
    # 2. Get the color from that plot.
    # 3. Plot the error bars (xb, yb) with that color and solid line, no marker.

    # If symbol has a marker, `real_symbol` will have it.

    # Warning: If `symbol` is e.g. 'o', then no line is drawn for data.
    # MATLAB: symbol = [ls mark col]; -> uses original symbol for data.
    # esymbol = ['-' col]; -> forces solid line for bars.

    # If I plot `xb` with `symbol`, it might draw markers on the error bar tips if symbol has markers.
    # We want bars to be lines.

    lines_data = plt.plot(real_x, real_y, real_symbol, **kwargs)

    # There might be multiple lines if n > 1

    all_handles = []

    for i, line in enumerate(lines_data):
        color = line.get_color()
        # Create style for error bars: solid line, same color, no marker
        # We can construct a style or just pass kwargs

        # Plot the error bars
        # xb[:, i], yb[:, i]

        line_err = plt.plot(xb[:, i], yb[:, i], linestyle='-', color=color, marker=None)

        all_handles.append(line) # Add the data line handle
        all_handles.extend(line_err) # Add the error bar line handle

    return tuple(all_handles)
