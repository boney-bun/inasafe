"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Functionality related to shake data files.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'imajimatika@gmail.com'
__version__ = '0.5.0'
__date__ = '12/12/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import os
import sys
from safe.storage.converter import convert_netcdf2tif
from safe.storage.vector import Vector
from safe.engine.interpolation import tag_polygons_by_grid
from safe.storage.core import read_layer
from download_netcdf import (download_file_url,
                             netcdf_url,
                             list_all_netcdf_files)

flood_directory = '/home/sunnii/Documents/inasafe/inasafe_real_flood'\
                  '/flood/'
polygons_path = '../inasafe_data/boundaries/rw_jakarta.shp'

def check_environment():
    os.mkdir('/home/sunnii/Documents/inasafe/inasafe-dev/pret')
    if not os.path.isfile(polygons_path):
        return False, 'Polygon file %s is not valid.' % polygons_path
    if not os.path.isdir(flood_directory):
        return False, 'flood_directory %s is not valid.' % flood_directory
    return True, 'Environment is ready....'


def processFloodEvent(netcdf_file=None, hours=12):
    """A function to process netcdf_file to a forecast file.
    """
    print 'Start flood forecasting'

    if netcdf_file is None:
        # retrieve data from the web
        netcdf_file = download_file_url(netcdf_url)
    else:
        netcdf_file = download_file_url(netcdf_url, name=netcdf_file)
    print 'Do flood forecasting for %s ...' % netcdf_file

    # check if a forecasting file has been created or not
    is_exist, polyforecast_filepath = get_result_file_name(netcdf_file)

    if is_exist:
        print 'Current flood forecasting has been already created.'
        print 'You can look it at %s' % polyforecast_filepath
        return

    # convert to tif
    tif_file = convert_netcdf2tif(netcdf_file, hours, verbose=False)
    tif_file = read_layer(tif_file)
    my_polygons = read_layer(polygons_path)
    my_result = tag_polygons_by_grid(my_polygons, tif_file, threshold=0.3,
        tag='affected')

    new_geom = my_result.get_geometry()
    new_data = my_result.get_data()

    date = os.path.split(netcdf_file)[-1].split('_')[0]
    # Create style
    style_classes = [dict(label=('Not Flooded'), min=0, max=0,
        colour='#1EFC7C', transparency=0, size=1),
                     dict(label=('Flooded'), min=1, max=1,
                         colour='#F31A1C', transparency=0, size=1)]
    style_info = dict(target_field='affected',
        style_classes=style_classes)

    v = Vector(geometry=new_geom, data=new_data,
        projection=my_result.projection,
        keywords={'category': 'hazard',
                  'subcategory': 'flood',
                  'title': ('%d hour flood forecast regions '
                            'in Jakarta at %s' % (hours,
                                                  date))},
        style_info=style_info)

    v.write_to_file(polyforecast_filepath)
    print 'Wrote tagged polygons to %s' % polyforecast_filepath

def usage():
    """Print how to use the main function.
    """
    sys.exit('Usage:\n%s [optional forecast file name]\nor\n%s --list'
             '\nor\n%s --run-all' % (
        sys.argv[0], sys.argv[0], sys.argv[0]))


def get_result_file_name(netcdf_file):
    """Function to get result file name from a netcdf_file.
    It will return a boolean value and the result file path.
    If the file path is exist, it will return true, otherwise false
    """
    polyforecast_filename = os.path.split(netcdf_file)[1].replace('.nc',
        '_regions.shp')
    date_file = polyforecast_filename.split('_')[0]
    if not os.path.isdir(os.path.join(flood_directory, date_file)):
        os.mkdir(os.path.join(flood_directory, date_file))
    polyforecast_filepath = os.path.join(flood_directory, date_file,
        polyforecast_filename)

    return os.path.isfile(polyforecast_filepath), polyforecast_filepath

if __name__ == '__main__':
    # Checking all environment is valid
    my_check, msg = check_environment()
    print msg
    if not my_check:
        exit()

    # Checking argument which has been given is valid
    if len(sys.argv) > 2:
        usage()
    elif len(sys.argv) == 1:
        processFloodEvent()
        exit()

    argv_1 = sys.argv[1]
    if argv_1 in '--list':
        # list all netcdf files from the web
        print 'List all netcdf file...'
        list_files = list_all_netcdf_files()
        for my_file in list_files:
            print my_file
    elif argv_1 in '--run-all':
        # run forecasting for all netcdf files from the web
        print 'Run forecasting for all data in the server.' \
              'This may take a little while.'
        list_files = list_all_netcdf_files()
        print len(list_files)
        for my_netcdf_file in list_files:
            processFloodEvent(netcdf_file=my_netcdf_file)
    else:
        # run specific file
        processFloodEvent(argv_1)
    exit()
