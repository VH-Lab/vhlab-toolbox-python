import numpy as np
from vlt.data.eqlen import eqlen

def mergegraph(G1, G2, nodenumbers2_1):
    """
    Merge adjacency matrices of 2 graphs.

    Args:
        G1 (numpy.ndarray): Adjacency matrix of graph 1.
        G2 (numpy.ndarray): Adjacency matrix of graph 2.
        nodenumbers2_1 (list or numpy.ndarray): The node index values of the nodes of G2 in G1.
                                                Indices are 1-based (MATLAB style) as per porting convention,
                                                BUT usually we convert to 0-based for internal processing if needed.
                                                However, the function description says "index values".
                                                Since we are porting, we should respect the input values.
                                                If the input `nodenumbers2_1` are indices into G1, they are likely 1-based if coming from MATLAB logic.
                                                But here we are in Python.
                                                Usually Python ports use 0-based indexing.
                                                However, memory says "Ported functions where MATLAB indices are returned ... use 1-based indexing".
                                                It doesn't explicitly say about *input* indices.
                                                If `nodenumbers2_1` contains values > n1 (number of nodes in G1), they are new nodes.
                                                In MATLAB, if n1=3, nodes are 1,2,3. If nodenumbers2_1 has 4, it's a new node.
                                                In Python, if n1=3, nodes are 0,1,2. If nodenumbers2_1 has 3, it's a new node?

                                                Let's stick to Python 0-based indexing for the implementation logic,
                                                but we need to decide what `nodenumbers2_1` contains.
                                                If the user passes [0, 3] where n1=3 (indices 0,1,2), then 3 is > 2, so it's a new node.

                                                The MATLAB code:
                                                newnodes_index = find(nodenumbers2_1>n1);
                                                oldnodes_index = find(nodenumbers2_1<=n1);

                                                If we use 1-based indexing for `nodenumbers2_1`, this logic holds (n1 is count).
                                                If we use 0-based indexing for `nodenumbers2_1`, and n1 is count.
                                                Example: G1 3 nodes (0,1,2). n1=3.
                                                If `nodenumbers2_1` has 3, it is >= n1 (3). So it is new.
                                                Wait, if indices are 0,1,2, then 3 is new.
                                                So `nodenumbers2_1 >= n1` would be the check for new nodes in 0-based.
                                                MATLAB uses `> n1` (strictly greater) because indices are 1..n1.

                                                However, the prompt memory says "Ported functions ... use 1-based indexing to preserve direct compatibility".
                                                This might apply here.
                                                But standard numpy usage is 0-based.

                                                Let's assume inputs are consistent with the ecosystem. If the ecosystem uses 1-based indices in return values, it might expect 1-based indices in arguments for compatibility.
                                                BUT, `mergegraph` takes G1 and G2 which are numpy arrays.
                                                If I use 1-based indices for `nodenumbers2_1`, I have to adjust them when accessing arrays.

                                                Let's assume `nodenumbers2_1` are 1-based indices to match MATLAB behavior described in memory.
                                                So `newnodes_index = find(nodenumbers2_1 > n1)`.

    Returns:
        tuple: (merged_graph, indexes, numnewnodes)
               indexes is a dict.
    """

    G1 = np.array(G1)
    G2 = np.array(G2)
    nodenumbers2_1 = np.array(nodenumbers2_1).flatten()

    n1 = G1.shape[0]
    n2 = G2.shape[0]

    if G1.shape[0] != G1.shape[1]:
        raise ValueError('G1 not square; an adjacency matrix must be square.')
    if G2.shape[0] != G2.shape[1]:
        raise ValueError('G2 not square; an adjacency matrix must be square.')

    # Assuming 1-based indexing for nodenumbers2_1 as per memory hint for compatibility
    # If nodenumbers2_1 contains 1, it refers to the first node of G1.

    # newnodes_index: indices into nodenumbers2_1 (which correspond to nodes of G2)
    # in MATLAB: find(nodenumbers2_1 > n1)

    # In Python, we return indices into nodenumbers2_1.
    # Note: nodenumbers2_1 corresponds to nodes of G2. So `nodenumbers2_1[i]` is the ID in G1 of the i-th node of G2.
    # If G2 has 2 nodes, nodenumbers2_1 has 2 elements.

    # Check if we should use 1-based or 0-based.
    # If I use 1-based, then n1 is the count. A node existing in G1 has index <= n1.
    # A node NOT in G1 has index > n1.

    # Let's perform the check.
    is_new_node = nodenumbers2_1 > n1
    newnodes_indices_in_G2 = np.flatnonzero(is_new_node) # 0-based indices into G2/nodenumbers2_1
    oldnodes_indices_in_G2 = np.flatnonzero(~is_new_node)

    if len(newnodes_indices_in_G2) == 0:
        raise ValueError('At least one of the nodes of G2 must be not present in G1.')

    newnodes = nodenumbers2_1[newnodes_indices_in_G2]
    oldnodes = nodenumbers2_1[oldnodes_indices_in_G2]

    numnewnodes = len(newnodes)

    # Check order of new nodes
    # sort(newnodes(:)-n1) == 1:numnewnodes
    # In Python 1-based:
    sorted_new_offsets = np.sort(newnodes - n1)
    expected_offsets = np.arange(1, numnewnodes + 1)

    if not np.array_equal(sorted_new_offsets, expected_offsets):
         # Also use eqlen? The MATLAB code uses vlt.data.eqlen
         # But array_equal is strict. eqlen handles shape.
         # Let's use eqlen equivalent or just array comparison
         raise ValueError('New nodes must be in increasing numerical order with no gaps in index values from the existing nodes.')

    # lower_right = G2(newnodes_index, newnodes_index)
    # Using numpy indexing (0-based indices into G2)
    lower_right = G2[np.ix_(newnodes_indices_in_G2, newnodes_indices_in_G2)]

    # indexes.lower_right
    # In MATLAB: sub2ind(size(G2), x_, y_)
    # sub2ind returns linear indices.
    # We should return linear indices (1-based for MATLAB compat?) or subscripts?
    # The doc says "index values of the panel in the merged matrix" and "G2".
    # If we return linear indices, they are hard to use in Python.
    # Maybe we should return row/col indices?
    # But for strict porting, we might want to return what MATLAB returns if downstream code expects it.
    # However, Python code using this will likely use numpy.
    # Linear indices in numpy are not standard usage (ravel).
    # "Ported functions where MATLAB indices are returned ... use 1-based indexing".
    # This suggests we might return 1-based linear indices? Or maybe just return subscripts?
    # The memory refers to "point2samplelabel", "line_n".
    # Let's look at the structure of `indexes`.
    # It has `lower_right`, `lower_left`, `upper_right`.
    # In MATLAB `indexes.lower_right` contains the linear indices of G2 elements that go into lower_right.
    # This is useful if you want to copy values later.
    # But `mergegraph` already builds `merged_graph`.
    # The doc says "INDEXES is a structure array of the entries that make up the new panels...".
    # If I am to use this in Python, I'd prefer a tuple of (rows, cols) or a boolean mask.
    # But to follow the port, maybe I should return a list of linear indices (1-based)?
    # Or maybe I should modify the return to be more Pythonic (e.g. 0-based linear indices or tuple of arrays).

    # Given the memory "use 1-based indexing to preserve direct compatibility", I will return 1-based linear indices.
    # Linear index L = row + col * nrows (MATLAB is column-major).
    # Python is row-major by default, but we can compute column-major indices.

    def sub2ind_colmajor(shape, rows, cols):
        # shape is (nrows, ncols)
        # L = rows + cols * nrows + 1 (1-based)
        return rows + cols * shape[0] + 1

    # Indexes for lower_right in G2
    # grid of indices
    # MATLAB: [x_, y_] = meshgrid(newnodes_index, newnodes_index)
    # Note: meshgrid in MATLAB is (x,y) -> (col, row). But here inputs are indices.
    # newnodes_index is 1-based in MATLAB logic?
    # Wait, in MATLAB `find` returns 1-based indices.
    # `newnodes_index` are indices into G2.

    # In Python `newnodes_indices_in_G2` are 0-based indices into G2.
    rr, cc = np.meshgrid(newnodes_indices_in_G2, newnodes_indices_in_G2, indexing='ij')
    # indexing='ij' gives matrix indexing (row, col).
    # MATLAB meshgrid(v,v) gives X (cols varies), Y (rows varies).
    # MATLAB:
    # x_ corresponds to columns? No, meshgrid(x,y) -> X has copies of x as rows. Y has copies of y as cols.
    # Actually MATLAB meshgrid: [X,Y] = meshgrid(x,y). X varies along columns (values of x). Y varies along rows (values of y).
    # Here inputs are same.
    # sub2ind(size, x_, y_) -> indices for (x_, y_).
    # Wait, sub2ind(size, row, col).
    # In MATLAB `meshgrid(newnodes_index, newnodes_index)`:
    # If newnodes_index = [2], X=[2], Y=[2]. sub2ind(..., 2, 2).
    # So it uses (row, col) from meshgrid outputs?
    # Usually [X,Y] = meshgrid(a,b). X corresponds to b (cols), Y to a (rows) in cartesian?
    # No. MATLAB `meshgrid`: `[X,Y] = meshgrid(xg, yg)`. X is length(yg) x length(xg).
    # Rows of X are copies of xg.
    # Cols of Y are copies of yg.
    # Wait.
    # Let's check MATLAB logic carefully.
    # `[x_, y_] = meshgrid(newnodes_index, newnodes_index)`.
    # `indexes.lower_right = sub2ind(size(G2), x_, y_)`.
    # So `x_` is treated as row index? or col? `sub2ind(size, r, c)`.
    # In MATLAB, `meshgrid` output order is X (cols), Y (rows).
    # But usually `sub2ind` takes (row, col).
    # If the author used `[x,y] = meshgrid(...)` and then `sub2ind(..., x, y)`,
    # then `x` is row index and `y` is col index.
    # BUT `meshgrid` puts the first argument across columns (X).
    # So `x` varies across columns. `y` varies across rows.
    # So `x` corresponds to columns (2nd dim) and `y` to rows (1st dim) usually in plotting.
    # BUT if passed to `sub2ind(size, row, col)`, then `x` is row, `y` is col.
    # So `x` (which varies across columns) is the ROW index.
    # `y` (which varies across rows) is the COL index.
    # This effectively generates the indices of the submatrix defined by `newnodes_index` by `newnodes_index`.

    # In Python, we can just compute the linear indices for the block.
    # We want indices (r, c) where r in newnodes_indices, c in newnodes_indices.
    # And convert to linear 1-based column-major.

    indexes = {}

    # lower_right indices in G2
    # We need (r, c) pairs.
    # Using broadcasting
    rows_lr = newnodes_indices_in_G2[:, None] # column vector
    cols_lr = newnodes_indices_in_G2[None, :] # row vector
    # We want the full grid
    rows_lr_grid = np.broadcast_to(rows_lr, (len(newnodes_indices_in_G2), len(newnodes_indices_in_G2)))
    cols_lr_grid = np.broadcast_to(cols_lr, (len(newnodes_indices_in_G2), len(newnodes_indices_in_G2)))

    # BUT MATLAB `meshgrid` order:
    # If a=[1,2]. [X,Y] = meshgrid(a,a).
    # X = [1 2; 1 2]. (Values of first arg, varying across columns).
    # Y = [1 1; 2 2]. (Values of second arg, varying across rows).
    # sub2ind(..., X, Y).
    # Row indices = X. Col indices = Y.
    # Row indices: 1, 2, 1, 2.
    # Col indices: 1, 1, 2, 2.
    # Pairs: (1,1), (2,1), (1,2), (2,2).
    # This covers the grid, but order might matter if reshaping.
    # The result in MATLAB is a matrix same size as X/Y.
    # Python meshgrid(..., indexing='xy') matches this X, Y behavior (roughly).

    # Let's replicate this.
    # Note: 1-based indices for calculation of linear index.
    # `newnodes_indices_in_G2` is 0-based. So we add 1.
    idxs_1based = newnodes_indices_in_G2 + 1
    X, Y = np.meshgrid(idxs_1based, idxs_1based) # indexing='xy' is default
    # X varies across columns (1, 2, ...). Y varies down rows.
    # sub2ind(size, X, Y) -> Row=X, Col=Y.
    lr_linear = sub2ind_colmajor(G2.shape, X, Y)
    indexes['lower_right'] = lr_linear

    # lower_left
    # lower_left = inf(numel(newnodes), n1)
    lower_left = np.full((numnewnodes, n1), np.inf)

    # lower_left( (newnodes-n1), oldnodes ) = G2( [newnodes_index], [oldnodes_index] )
    # LHS indices:
    # newnodes are 1-based values > n1.
    # newnodes - n1 are 1-based indices into lower_left rows.
    # So 0-based: (newnodes - n1 - 1).
    lhs_rows = (newnodes - n1 - 1).astype(int)

    # oldnodes are 1-based indices into G1 (and thus lower_left cols).
    # 0-based: oldnodes - 1.
    lhs_cols = (oldnodes - 1).astype(int)

    # RHS indices into G2: newnodes_indices_in_G2, oldnodes_indices_in_G2

    # Assigning
    # Python: lower_left[np.ix_(lhs_rows, lhs_cols)] = G2[np.ix_(newnodes_indices_in_G2, oldnodes_indices_in_G2)]
    # We must ensure correct mapping.
    # In MATLAB: lower_left(R, C) = G2(R2, C2).
    # It assigns the submatrix defined by R, C from the submatrix defined by R2, C2.
    # Since newnodes corresponds to newnodes_index, and oldnodes to oldnodes_index, the order is preserved.
    # BUT `newnodes` and `oldnodes` are extracted from `nodenumbers2_1`.
    # `newnodes_index` are the indices in `nodenumbers2_1`.
    # `nodenumbers2_1` is flattened.
    # So `newnodes = nodenumbers2_1(newnodes_index)`.
    # So the i-th element of lhs_rows corresponds to i-th element of newnodes, which comes from i-th element of newnodes_index.
    # So the mapping is consistent.

    lower_left[np.ix_(lhs_rows, lhs_cols)] = G2[np.ix_(newnodes_indices_in_G2, oldnodes_indices_in_G2)]

    indexes['lower_left'] = {'G2': [], 'merged': []}

    if len(oldnodes) > 0:
        # [x,y] = meshgrid(newnodes-n1, oldnodes)
        # indexes.lower_left.merged = sub2ind(size(lower_left), x, y)
        # x (rows), y (cols).
        # x is from newnodes-n1 (which are row indices 1-based).
        # y is from oldnodes (which are col indices 1-based).

        r_vals = newnodes - n1 # 1-based
        c_vals = oldnodes # 1-based
        X_ll, Y_ll = np.meshgrid(r_vals, c_vals)
        # sub2ind on lower_left
        ll_merged_linear = sub2ind_colmajor(lower_left.shape, X_ll, Y_ll)
        indexes['lower_left']['merged'] = ll_merged_linear

        # [x2,y2] = meshgrid(newnodes_index, oldnodes_index)
        # indexes.lower_left.G2 = sub2ind(size(G2), x2, y2)
        r2_vals = newnodes_indices_in_G2 + 1
        c2_vals = oldnodes_indices_in_G2 + 1
        X2_ll, Y2_ll = np.meshgrid(r2_vals, c2_vals)
        ll_G2_linear = sub2ind_colmajor(G2.shape, X2_ll, Y2_ll)
        indexes['lower_left']['G2'] = ll_G2_linear

    # upper_right
    # upper_right = inf(n1, numel(newnodes))
    upper_right = np.full((n1, numnewnodes), np.inf)

    # upper_right( oldnodes, (newnodes-n1)) = G2( [oldnodes_index], [newnodes_index] )
    lhs_rows_ur = (oldnodes - 1).astype(int)
    lhs_cols_ur = (newnodes - n1 - 1).astype(int)

    upper_right[np.ix_(lhs_rows_ur, lhs_cols_ur)] = G2[np.ix_(oldnodes_indices_in_G2, newnodes_indices_in_G2)]

    indexes['upper_right'] = {'G2': [], 'merged': []}

    if len(oldnodes) > 0:
        # indexes.upper_right.merged = sub2ind(size(upper_right), y, x)
        # Uses y and x from previous meshgrid:
        # y corresponds to oldnodes (rows in upper_right)
        # x corresponds to newnodes-n1 (cols in upper_right)
        # Note: In MATLAB, `[x,y] = meshgrid(newnodes-n1, oldnodes)`.
        # X has `newnodes-n1` values. Y has `oldnodes`.
        # previous block used `sub2ind(..., x, y)`. x=row, y=col.
        # Here `sub2ind(..., y, x)`. y=row, x=col.
        # This matches `upper_right(oldnodes, newnodes-n1)`.
        # So we can reuse X_ll, Y_ll but swapped.

        ur_merged_linear = sub2ind_colmajor(upper_right.shape, Y_ll, X_ll)
        indexes['upper_right']['merged'] = ur_merged_linear

        # indexes.upper_right.G2 = sub2ind(size(G2), y2, x2)
        # y2 (oldnodes_index) -> rows
        # x2 (newnodes_index) -> cols

        ur_G2_linear = sub2ind_colmajor(G2.shape, Y2_ll, X2_ll)
        indexes['upper_right']['G2'] = ur_G2_linear

    # merged_graph = [G1 upper_right ; lower_left lower_right]
    top = np.hstack((G1, upper_right))
    bottom = np.hstack((lower_left, lower_right))
    merged_graph = np.vstack((top, bottom))

    return merged_graph, indexes, numnewnodes
