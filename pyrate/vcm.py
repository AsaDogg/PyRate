'''
Variance/Covariance matrix functionality for PyRate, ported from Hua Wang's
MATLAB code for Pirate.

.. codeauthor:: Ben Davies, Matt Garthwaite, Sudipta Basak
'''

from numpy import array, where, isnan, real, imag, sum, sqrt, meshgrid
from numpy import zeros, vstack, ceil, mean, exp, reshape
from numpy.linalg import norm
import numpy as np
from scipy.fftpack import fft2, ifft2, fftshift
from scipy.optimize import fmin

from pyrate.algorithm import master_slave_ids


def pendiffexp(alphamod, cvdav):
    """
    Fits an exponential model to data.

    :param float alphamod: Exponential decay exponent.
    :param array cvdav: Function magnitude at 0 radius (2 col array of radius,
    variance)
    """

    # maxvar usually at zero lag
    mx = cvdav[1, 0]
    return norm(cvdav[1, :] - (mx * exp(-alphamod * cvdav[0, :])))


# this is not used any more
def unique_points(points):
    """
    Returns unique points from a list of coordinates.

    :param points: Sequence of (y,x) or (x,y) tuples.
    """
    return vstack([array(u) for u in set(points)])


def cvd(ifg, calc_alpha=False):
    """
    Calculate average covariance versus distance (autocorrelation) and its best
    fitting exponential function

    :param ifg: An interferogram.
    :type ifg: :py:class:`pyrate.shared.Ifg`.
    :param calc_alpha: whether you calculate alpha.
    """
    # distance division factor of 1000 converts to km and is needed to match
    # Matlab code output
    distfact = 1000

    # calculate 2D auto-correlation of image using the
    # spectral method (Wiener-Khinchin theorem)
    if ifg.nan_converted:  # saves heaps of time with no-nan conversion
        phase = where(isnan(ifg.phase_data), 0, ifg.phase_data)
    else:
        phase = ifg.phase_data
    fft_phase = fft2(phase)
    pspec = real(fft_phase)**2 + imag(fft_phase)**2
    autocorr_grid = ifft2(pspec)
    nzc = sum(sum(phase != 0))
    autocorr_grid = fftshift(real(autocorr_grid)) / nzc

    # pixel distances from pixel at zero lag (image centre).
    xx, yy = meshgrid(range(ifg.ncols), range(ifg.nrows))

    # r is distance from the center
    # doing np.divide and np.sqrt will improve performance as it keeps
    # calculations in the numpy land
    r = np.divide(np.sqrt(((xx-ifg.x_centre) * ifg.x_size)**2 +
             ((yy-ifg.y_centre) * ifg.y_size)**2), distfact)

    r = reshape(r, ifg.num_cells)
    acg = reshape(autocorr_grid, ifg.num_cells)

    # Symmetry in image; keep only unique points
    # tmp = unique_points(zip(acg, r))
    # Sudipta: Is this faster than keeping only the 1st half as in Matlab?
    # Sudipta: Unlikely, as unique_point is a search/comparison,
    # whereas keeping 1st half is just numpy indexing.
    # If it is not faster, why was this done differently here?

    r = r[:int(ceil(ifg.num_cells/2.0)) + ifg.nrows]
    acg = acg[:len(r)]

    # Alternative method to remove duplicate cells from Matlab Pirate
    #r = r[:ceil(len(r)/2)+nlines] # Reason for '+nlines' term unknown

    # eg. array([x for x in set([(1,1), (2,2), (1,1)])])
    # the above shortens r by some number of cells

    # bin width for collecting data
    w = max(ifg.x_size, ifg.y_size) * 2 / distfact

    # pick the smallest axis to determine circle search radius
    #print 'ifg.X_CENTRE, ifg.Y_CENTRE=', ifg.x_centre, ifg.y_centre
    #print 'ifg.X_SIZE, ifg.Y_SIZE', ifg.x_size, ifg.y_size
    if (ifg.x_centre * ifg.x_size) < (ifg.y_centre * ifg.y_size):
        maxdist = ifg.x_centre * ifg.x_size / distfact
    else:
        maxdist = ifg.y_centre * ifg.y_size/ distfact

    # filter out data where the of lag distance is greater than maxdist
    #r = array([e for e in rorig if e <= maxdist]) # MG: prefers to use all the data
    #acg = array([e for e in rorig if e <= maxdist])
    indices_to_keep = r < maxdist
    r = r[indices_to_keep]
    acg = acg[indices_to_keep]

    if calc_alpha:
        # classify values of r according to bin number
        rbin = ceil(r / w).astype(int)
        maxbin = max(rbin)  # consistent with Matlab code

        cvdav = zeros(shape=(2, maxbin))

        # the following stays in numpy land
        # distance instead of bin number
        cvdav[0, :] = np.multiply(range(maxbin), w)
        # mean variance for the bins
        cvdav[1, :] = map(lambda b: mean(acg[rbin == b]), range(maxbin))

        # calculate best fit function maxvar*exp(-alpha*r)
        alphaguess = 2 / (maxbin * w)
        alpha = fmin(pendiffexp, x0=alphaguess, args=(cvdav,), disp=0,
                     xtol=1e-6, ftol=1e-6)
        print "1st guess alpha", alphaguess, 'converged alpha:', alpha
        # maximum variance usually at the zero lag: max(acg[:len(r)])
        return np.max(acg), alpha[0]
    else:
        return np.max(acg), None


def get_vcmt(ifgs, maxvar):
    '''
    Returns the temporal variance/covariance matrix.
    '''

    # c=0.5 for common master or slave; c=-0.5 if master of one matches slave of another
    nifgs = len(ifgs)
    vcm_pat = zeros((nifgs, nifgs))

    dates = [ifg.master for ifg in ifgs] + [ifg.slave for ifg in ifgs]
    ids = master_slave_ids(dates)

    for i, ifg in enumerate(ifgs):
        mas1, slv1 = ids[ifg.master], ids[ifg.slave]

        for j, ifg2 in enumerate(ifgs):
            mas2, slv2 = ids[ifg2.master], ids[ifg2.slave]
            if mas1 == mas2 or slv1 == slv2:
                vcm_pat[i, j] = 0.5

            if mas1 == slv2 or slv1 == mas2:
                vcm_pat[i, j] = -0.5

            if mas1 == mas2 and slv1 == slv2:
                vcm_pat[i, j] = 1.0  # handle testing ifg against itself

    # make covariance matrix in time domain
    std = sqrt(maxvar).reshape((nifgs, 1))
    vcm_t = std * std.transpose()
    return vcm_t * vcm_pat


if __name__ == "__main__":
    import os
    import shutil
    from subprocess import call

    from pyrate.scripts import run_pyrate
    from pyrate import matlab_mst_kruskal as matlab_mst
    from pyrate.tests.common import SYD_TEST_MATLAB_ORBITAL_DIR, SYD_TEST_OUT
    from pyrate import config as cf
    from pyrate import reference_phase_estimation as rpe

    # start each full test run cleanly
    shutil.rmtree(SYD_TEST_OUT, ignore_errors=True)

    os.makedirs(SYD_TEST_OUT)

    params = cf.get_config_params(
            os.path.join(SYD_TEST_MATLAB_ORBITAL_DIR, 'pyrate_system_test.conf'))
    params[cf.REF_EST_METHOD] = 2
    call(["python", "pyrate/scripts/run_prepifg.py",
          os.path.join(SYD_TEST_MATLAB_ORBITAL_DIR, 'pyrate_system_test.conf')])

    xlks, ylks, crop = run_pyrate.transform_params(params)

    base_ifg_paths = run_pyrate.original_ifg_paths(params[cf.IFG_FILE_LIST])

    dest_paths = run_pyrate.get_dest_paths(base_ifg_paths, crop, params, xlks)

    ifg_instance = matlab_mst.IfgListPyRate(datafiles=dest_paths)

    ifgs = ifg_instance.ifgs
    nan_conversion = int(params[cf.NAN_CONVERSION])

    for i in ifgs:
        if not i.is_open:
            i.open()
        if not i.nan_converted:
            i.convert_to_nans()

        if not i.mm_converted:
            i.convert_to_mm()
            i.write_modified_phase()

    if params[cf.ORBITAL_FIT] != 0:
        run_pyrate.remove_orbital_error(ifgs, params)

    refx, refy = run_pyrate.find_reference_pixel(ifgs, params)

    if params[cf.ORBITAL_FIT] != 0:
        run_pyrate.remove_orbital_error(ifgs, params)

    _, ifgs = rpe.estimate_ref_phase(ifgs, params, refx, refy)

    # Calculate interferogram noise
    maxvar = [cvd(i)[0] for i in ifgs]

    for n, i in enumerate(ifgs):
        print maxvar[n], os.path.basename(i.data_path)

