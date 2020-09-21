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
"""
This Python module contains a collection of constants used in
various components of the PyRate software
"""

# lookup keys for the metadata fields in PyRate GeoTIFF files
PYRATE_NCOLS = 'NCOLS'
PYRATE_NROWS = 'NROWS'
PYRATE_X_STEP = 'X_STEP'
PYRATE_Y_STEP = 'Y_STEP'
PYRATE_LAT = 'LAT'
PYRATE_LONG = 'LONG'
FIRST_DATE = 'FIRST_DATE'
FIRST_TIME = 'FIRST_TIME'
SECOND_DATE = 'SECOND_DATE'
SECOND_TIME = 'SECOND_TIME'
EPOCH_DATE = 'EPOCH_DATE'
PYRATE_DATUM = 'DATUM'
PYRATE_TIME_SPAN = 'TIME_SPAN_YEAR'
PYRATE_WAVELENGTH_METRES = 'WAVELENGTH_METRES'
PYRATE_INCIDENCE_DEGREES = 'INCIDENCE_DEGREES'
PYRATE_HEADING_DEGREES = 'HEADING_DEGREES'
PYRATE_AZIMUTH_DEGREES = 'AZIMUTH_DEGREES'
PYRATE_RANGE_PIX_METRES = 'RANGE_PIX_METRES'
PYRATE_RANGE_N = 'RANGE_N'
PYRATE_RANGE_LOOKS = 'RANGE_LOOKS'
PYRATE_AZIMUTH_PIX_METRES = 'AZIMUTH_PIX_METRES'
PYRATE_AZIMUTH_N = 'AZIMUTH_N'
PYRATE_AZIMUTH_LOOKS = 'AZIMUTH_LOOKS'
PYRATE_PRF_HERTZ = 'PRF_HERTZ'
PYRATE_NEAR_RANGE_METRES = 'NEAR_RANGE_METRES'
PYRATE_SAR_EARTH_METRES = 'SAR_EARTH_METRES'
PYRATE_SEMI_MAJOR_AXIS_METRES = 'SEMI_MAJOR_AXIS_METRES'
PYRATE_SEMI_MINOR_AXIS_METRES = 'SEMI_MINOR_AXIS_METRES'
PYRATE_BASELINE_T = 'BASELINE_T'
PYRATE_BASELINE_C = 'BASELINE_C'
PYRATE_BASELINE_N = 'BASELINE_N'
PYRATE_BASELINE_RATE_T = 'BASELINE_RATE_T'
PYRATE_BASELINE_RATE_C = 'BASELINE_RATE_C'
PYRATE_BASELINE_RATE_N = 'BASELINE_RATE_N'
PYRATE_INSAR_PROCESSOR = 'INSAR_PROCESSOR'
PYRATE_WEATHER_ERROR = 'WEATHER_ERROR'
PYRATE_APS_ERROR = 'APS_ERROR'
PYRATE_MAXVAR = 'CVD_MAXVAR'
PYRATE_ALPHA = 'CVD_ALPHA'
IFG_LKSX = 'IFG_MULTILOOK_X'
IFG_LKSY = 'IFG_MULTILOOK_Y'
IFG_CROP = 'IFG_CROP_OPT'
MLOOKED_COH_MASKED_IFG = 'COHERENCE_MASKED_MULTILOOKED_IFG'
MULTILOOKED = 'MULTILOOKED_IFG'
MULTILOOKED_COH = 'MULTILOOKED_COH'
ORIG = 'ORIGINAL_IFG'
COH = 'ORIGINAL_COH'
DEM = 'ORIGINAL_DEM'
MLOOKED_DEM = 'MULTILOOKED_DEM'
LOOK = 'LOOK_ANGLE_MAP'
INCIDENCE = 'INCIDENCE_ANGLE_MAP'
AZIMUTH = 'AZIMUTH_ANGLE_MAP'
BPERP = 'PERPENDICULAR_BASELINE_MAP'
INCR = 'INCREMENTAL_TIME_SLICE'
CUML = 'CUMULATIVE_TIME_SLICE'
STACKRATE = 'STACKED_RATE_MAP'
STACKERROR = 'STACKED_RATE_ERROR'
STACKSAMP = 'STACKED_RATE_SAMPLES'
LINRATE = 'LINEAR_RATE_MAP'
LINERROR = 'LINEAR_RATE_ERROR'
LINSAMP = 'LINEAR_RATE_SAMPLES'
LINRSQ = 'LINEAR_RATE_RSQUARED'
LINICPT = 'LINEAR_RATE_INTERCEPT'
PYRATE_ORBITAL_ERROR = 'ORBITAL_ERROR'
ORB_REMOVED = 'REMOVED'
APS_REMOVED = 'REMOVED'
PYRATE_REF_PHASE = 'REFERENCE_PHASE'
REF_PHASE_REMOVED = 'REMOVED'
NAN_STATUS = 'NAN_STATUS'
NAN_CONVERTED = 'CONVERTED'
DATA_TYPE = 'DATA_TYPE'
DATA_UNITS = 'DATA_UNITS'
INPUT_TYPE = 'INPUT_TYPE'

PYRATE_REFPIX_X = 'REF_PIX_X'
PYRATE_REFPIX_Y = 'REF_PIX_Y'
PYRATE_REFPIX_LAT = 'REF_PIX_LAT'
PYRATE_REFPIX_LON = 'REF_PIX_LON'
PYRATE_MEAN_REF_AREA = 'REF_AREA_MEAN'
PYRATE_STDDEV_REF_AREA = 'REF_AREA_STDDEV'
SEQUENCE_POSITION = 'SEQUENCE_POSITION'

DAYS_PER_YEAR = 365.25  # span of year, not a calendar year
YEARS_PER_DAY = 1 / DAYS_PER_YEAR
SPEED_OF_LIGHT_METRES_PER_SECOND = 3e8
MM_PER_METRE = 1000
