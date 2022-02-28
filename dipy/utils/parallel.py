import numpy as np
import multiprocessing
from tqdm.auto import tqdm
from dipy.utils.optpkg import optional_package

joblib, has_joblib, _ = optional_package('joblib')
dask, has_dask, _ = optional_package('dask')


def parfor(func, in_list, out_shape=None, n_jobs=-1, engine="joblib",
           backend=None, func_args=[], func_kwargs={},
           **kwargs):
    """
    Parallel for loop for numpy arrays

    Parameters
    ----------
    func : callable
        The function to apply to each item in the array. Must have the form:
        ``func(arr, idx, *args, *kwargs)`` where arr is an ndarray and idx is an
        index into that array (a tuple). The Return of `func` needs to be one
        item (e.g. float, int) per input item.
    in_list : list
       A sequence of items each of which can be an input to ``func``.
    out_shape : tuple, optional
         The shape of the output array. If not specified, the output shape will
         be `(len(in_list),)`.
    n_jobs : integer, optional
        The number of jobs to perform in parallel. -1 to use all but one cpu.
        Default: -1.
    engine : str
        {"dask", "joblib", "serial"}
        The last one is useful for debugging -- runs the code without any
        parallelization. Default: "joblib"
    backend : str, optional
        What joblib or dask backend to use. For joblib, the default is "loky".
        For dask the default is "threading".
    func_args : list, optional
        Positional arguments to `func`. Default: []
    func_kwargs : list, optional
        Keyword arguments to `func`. Default: {}
    kwargs : dict, optional
        Additional arguments to pass to either joblib.Parallel
        or dask.compute depending on the engine used.
        Default: {}

    Returns
    -------
    ndarray of identical shape to `arr`

    Examples
    --------
    >>> def power_it(num, n=2):
    ...     return num ** n
    >>> arr = np.arange(100).reshape(10, 10)
    >>> out = parfor(power_it, arr, n_jobs=2)
    >>> out[0, 0] == power_it(arr[0, 0]) # doctest: +SKIP
    """
    if engine == "joblib":
        if not has_joblib:
            raise joblib()
        if backend is None:
            backend = "loky"
        p = joblib.Parallel(
            n_jobs=n_jobs, backend=backend,
            **kwargs)
        d = joblib.delayed(func)
        d_l = []
        for in_element in in_list:
            d_l.append(d(in_element, *func_args, **func_kwargs))
        results = p(tqdm(d_l))

    elif engine == "dask":
        if not has_dask:
            raise dask()
        if backend is None:
            backend = "threading"

        if n_jobs == -1:
            n_jobs = multiprocessing.cpu_count()
            n_jobs = n_jobs - 1

        def partial(func, *args, **keywords):
            def newfunc(in_arg):
                return func(in_arg, *args, **keywords)
            return newfunc
        p = partial(func, *func_args, **func_kwargs)
        d = [dask.delayed(p)(i) for i in in_list]
        if backend == "multiprocessing":
            results = dask.compute(*d, scheduler="processes",
                                   workers=n_jobs, **kwargs)
        elif backend == "threading":
            results = dask.compute(*d, scheduler="threads",
                                   workers=n_jobs, **kwargs)
        else:
            raise ValueError("%s is not a backend for dask" % backend)

    elif engine == "serial":
        results = []
        for in_element in in_list:
            results.append(func(in_element, *func_args, **func_kwargs))

    if out_shape is not None:
        return np.array(results).reshape(out_shape)
    else:
        return results
