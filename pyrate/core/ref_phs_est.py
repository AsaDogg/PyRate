#   This Python module is part of the PyRate software package.
#
#   Copyright 2020 Geoscience Australia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
# coding: utf-8
"""
This Python module implements a reference phase estimation algorithm.
"""
from pathlib import Path
from typing import List
from joblib import Parallel, delayed
import numpy as np

from pyrate.core import ifgconstants as ifc, config as cf, mpiops, shared
from pyrate.core.shared import joblib_log_level, nanmedian, Ifg
from pyrate.core import mpiops
from pyrate.configuration import Configuration
from pyrate.core.logger import pyratelogger as log

MAIN_PROCESS = 0


def est_ref_phase_patch_median(ifg_paths, params, refpx, refpy):
    """
    Reference phase estimation, calculated as the median within a patch around
    the supplied reference pixel.

    :param list ifg_paths: List of interferogram paths or objects.
    :param dict params: Dictionary of configuration parameters
    :param int refpx: Reference pixel X found by ref pixel method
    :param int refpy: Reference pixel Y found by ref pixel method

    :return: ref_phs: Numpy array of reference phase values of size (nifgs, 1)
    :rtype: ndarray
    :return: ifgs: Reference phase data is removed interferograms in place
    """
    half_chip_size = int(np.floor(params[cf.REF_CHIP_SIZE] / 2.0))
    chipsize = 2 * half_chip_size + 1
    thresh = chipsize * chipsize * params[cf.REF_MIN_FRAC]

    def _inner(ifg_paths):
        if isinstance(ifg_paths[0], Ifg):
            ifgs = ifg_paths
        else:
            ifgs = [Ifg(ifg_path) for ifg_path in ifg_paths]

        for ifg in ifgs:
            if not ifg.is_open:
                ifg.open(readonly=False)

        phase_data = [i.phase_data for i in ifgs]
        if params[cf.PARALLEL]:
            ref_phs = Parallel(n_jobs=params[cf.PROCESSES],
                               verbose=joblib_log_level(cf.LOG_LEVEL))(
                delayed(_est_ref_phs_patch_median)(p, half_chip_size, refpx, refpy, thresh)
                for p in phase_data)

            for n, ifg in enumerate(ifgs):
                ifg.phase_data -= ref_phs[n]
        else:
            ref_phs = np.zeros(len(ifgs))
            for n, ifg in enumerate(ifgs):
                ref_phs[n] = _est_ref_phs_patch_median(phase_data[n], half_chip_size, refpx, refpy, thresh)

        return ref_phs
    
    process_ifgs_paths = mpiops.array_split(ifg_paths)
    ref_phs = _inner(process_ifgs_paths)
    return ref_phs   


def _est_ref_phs_patch_median(phase_data, half_chip_size, refpx, refpy, thresh):
    """
    Convenience function for ref phs estimate method 2 parallelisation
    """
    patch = phase_data[refpy - half_chip_size: refpy + half_chip_size + 1,
                       refpx - half_chip_size: refpx + half_chip_size + 1]
    patch = np.reshape(patch, newshape=(-1, 1), order='F')
    nanfrac = np.sum(~np.isnan(patch))
    if nanfrac < thresh:
        raise ReferencePhaseError('The data window at the reference pixel '
                                  'does not have enough valid observations. '
                                  'Actual = {}, Threshold = {}.'.format(
                                          nanfrac, thresh))
    ref_ph = nanmedian(patch)
    return ref_ph


def est_ref_phase_ifg_median(ifg_paths, params):
    """
    Reference phase estimation, calculated as the median of the whole
    interferogram image.

    :param list ifg_paths: List of interferogram paths or objects
    :param dict params: Dictionary of configuration parameters

    :return: ref_phs: Numpy array of reference phase values of size (nifgs, 1)
    :rtype: ndarray
    :return: ifgs: Reference phase data is removed interferograms in place
    """
    def _process_phase_sum(ifg_paths):
        if isinstance(ifg_paths[0], Ifg):
            proc_ifgs = ifg_paths
        else:
            proc_ifgs = [Ifg(ifg_path) for ifg_path in ifg_paths]

        for ifg in proc_ifgs:
            if not ifg.is_open:
                ifg.open(readonly=False)

        ifg_phase_data_sum = np.zeros(proc_ifgs[0].shape, dtype=np.float32)

        for ifg in proc_ifgs:
            ifg_phase_data_sum += ifg.phase_data

        return ifg_phase_data_sum

    def _inner(proc_ifgs, phase_data_sum):
        if isinstance(proc_ifgs[0], Ifg):
            proc_ifgs = proc_ifgs
        else:
            proc_ifgs = [Ifg(ifg_path) for ifg_path in proc_ifgs]

        for ifg in proc_ifgs:
            if not ifg.is_open:
                ifg.open(readonly=False)

        comp = np.isnan(phase_data_sum)
        comp = np.ravel(comp, order='F')

        if params[cf.PARALLEL]:
            log.info("Calculating ref phase using multiprocessing")
            ref_phs = Parallel(n_jobs=params[cf.PROCESSES], verbose=joblib_log_level(cf.LOG_LEVEL))(
                delayed(_est_ref_phs_ifg_median)(p.phase_data, comp) for p in proc_ifgs
            )
            for n, ifg in enumerate(proc_ifgs):
                ifg.phase_data -= ref_phs[n]
        else:
            log.info("Calculating ref phase")
            ref_phs = np.zeros(len(proc_ifgs))
            for n, ifg in enumerate(proc_ifgs):
                ref_phs[n] = _est_ref_phs_ifg_median(ifg.phase_data, comp)

        return ref_phs

    process_ifg_paths = mpiops.array_split(ifg_paths)
    if mpiops.MPI_INSTALLED:
        ifg_phase_data_sum = mpiops.comm.allreduce(_process_phase_sum(process_ifg_paths), mpiops.sum_op)
    else:
        ifg_phase_data_sum = _process_phase_sum(process_ifg_paths)

    ref_phs = _inner(process_ifg_paths, ifg_phase_data_sum)

    return ref_phs


def _update_phase_metadata(ifg):
    ifg.meta_data[ifc.PYRATE_REF_PHASE] = ifc.REF_PHASE_REMOVED
    ifg.write_modified_phase()
    log.debug(f"Reference phase corrected for {ifg.data_path}")


def _est_ref_phs_ifg_median(phase_data, comp):
    """
    Convenience function for ref phs estimate method 1 parallelisation
    """
    ifgv = np.ravel(phase_data, order='F')
    ifgv[comp == 1] = np.nan
    return nanmedian(ifgv)


def _update_phase_and_metadata(ifgs, ref_phs):

    def __inner(ifg, ref_ph):
        ifg.open()
        ifg.phase_data -= ref_ph
        ifg.meta_data[ifc.PYRATE_REF_PHASE] = ifc.REF_PHASE_REMOVED
        ifg.write_modified_phase()
        log.debug(f"Reference phase corrected for {ifg.data_path}")
        ifg.close()
    for i, rp in zip(mpiops.array_split(ifgs), mpiops.array_split(ref_phs)):
        __inner(i, rp)


class ReferencePhaseError(Exception):
    """
    Generic class for errors in reference phase estimation.
    """
    pass


def ref_phase_est_wrapper(params):
    """
    Wrapper for reference phase estimation.
    """
    ifg_paths = [ifg_path.tmp_sampled_path for ifg_path in params[cf.INTERFEROGRAM_FILES]]
    refpx, refpy = params[cf.REFX_FOUND], params[cf.REFY_FOUND]
    if len(ifg_paths) < 2:
        raise ReferencePhaseError(
            "At least two interferograms required for reference phase correction ({len_ifg_paths} "
            "provided).".format(len_ifg_paths=len(ifg_paths))
        )

    # this is not going to be true as we now start with fresh multilooked ifg copies - remove?
    if mpiops.run_once(shared.check_correction_status, ifg_paths, ifc.PYRATE_REF_PHASE):
        log.debug('Finished reference phase correction')
        return

    ifgs = [Ifg(ifg_path) for ifg_path in ifg_paths]
    # Save reference phase numpy arrays to disk.
    ref_phs_file = Configuration.ref_phs_file(params)

    if ref_phs_file.exists():
        ref_phs = np.load(ref_phs_file)
        _update_phase_and_metadata(ifgs, ref_phs)
        shared.save_numpy_phase(ifg_paths, params)
        return ref_phs, ifgs

    if params[cf.REF_EST_METHOD] == 1:
        log.info("Calculating reference phase as median of interferogram")
        ref_phs = est_ref_phase_ifg_median(ifg_paths, params)
    elif params[cf.REF_EST_METHOD] == 2:
        log.info('Calculating reference phase in a patch surrounding pixel (x, y): ({}, {})'.format(refpx, refpy))
        ref_phs = est_ref_phase_patch_median(ifg_paths, params, refpx, refpy)
    else:
        raise ReferencePhaseError("No such option, set parameter 'refest' to '1' or '2'.")

    if mpiops.rank == MAIN_PROCESS:
        collected_ref_phs = np.zeros(len(ifg_paths), dtype=np.float64)
        process_indices = mpiops.array_split(range(len(ifg_paths))).astype(np.uint16)
        collected_ref_phs[process_indices] = ref_phs
        for r in range(1, mpiops.size):
            process_indices = mpiops.array_split(range(len(ifg_paths)), r).astype(np.uint16)
            this_process_ref_phs = np.zeros(shape=len(process_indices),
                                            dtype=np.float64)
            mpiops.comm.Recv(this_process_ref_phs, source=r, tag=r)
            collected_ref_phs[process_indices] = this_process_ref_phs
        np.save(file=ref_phs_file, arr=collected_ref_phs)
    else:
        collected_ref_phs = np.empty(len(ifg_paths), dtype=np.float64)
        mpiops.comm.Send(ref_phs, dest=MAIN_PROCESS, tag=mpiops.rank)

    mpiops.comm.Bcast(collected_ref_phs, root=0)

    _update_phase_and_metadata(ifgs, collected_ref_phs)

    log.debug('Finished reference phase correction')

    mpiops.comm.barrier()
    shared.save_numpy_phase(ifg_paths, params)

    log.debug("Reference phase computed!")

    # Preserve old return value so tests don't break.
    return ref_phs, ifgs
