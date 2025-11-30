import json
import numpy as np

def jsonencodenan(obj):
    """
    Encodes the variable OBJ into a JSON object in a manner that
    allows the use of NaN and -Inf and Inf.
    """
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                np.int16, np.int32, np.int64, np.uint8,
                np.uint16, np.uint32, np.uint64)):
                return int(obj)
            if isinstance(obj, (np.float_, np.float16, np.float32,
                np.float64)):
                return float(obj)
            return super(NumpyEncoder, self).default(obj)

    # In Python's json library, NaN/Inf are supported by default.
    return json.dumps(obj, cls=NumpyEncoder, indent=4)
