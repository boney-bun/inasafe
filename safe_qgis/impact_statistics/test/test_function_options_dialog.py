"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'misugijunz@gmail.com'
__date__ = '15/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import unittest
import sys
import os
import logging

from PyQt4.QtGui import QLineEdit

from safe.common.testing import get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..///'))
sys.path.append(pardir)

from safe_qgis.safe_interface import get_plugins
from third_party.odict import OrderedDict

from safe_qgis.impact_statistics.function_options_dialog import (
    FunctionOptionsDialog)
# pylint: disable=W0611
# pylint: enable=W0611

LOGGER = logging.getLogger('InaSAFE')


class FunctionOptionsDialogTest(unittest.TestCase):
    """Test the InaSAFE GUI for Configurable Impact Functions"""

    def setUp(self):
        """Fixture run before all tests"""
        pass

    def tearUp(self):
        """Fixture run before each test"""
        pass

    def tearDown(self):
        """Fixture run after each test"""
        pass

    def test_buildForm(self):
        """Test that we can build a form by passing it a function and params.
        """
        # noinspection PyUnresolvedReferences
        # pylint: disable=W0612
        from safe.engine.impact_functions_for_testing import \
            itb_fatality_model_configurable
        # pylint: enable=W0612
        myFunctionId = 'I T B Fatality Function Configurable'
        myFunctionList = get_plugins(myFunctionId)
        assert len(myFunctionList) == 1
        assert myFunctionList[0].keys()[0] == myFunctionId

        myDialog = FunctionOptionsDialog(None)
        myParameters = {
            'thresholds': [1.0],
            'postprocessors': {
                'Gender': {'on': True},
                'Age': {
                    'on': True,
                    'params': {
                        'youth_ratio': 0.263,
                        'elderly_ratio': 0.078,
                        'adult_ratio': 0.659}}}}

        myDialog.build_form(myParameters)

        assert myDialog.tabWidget.count() == 2

        myChildren = myDialog.tabWidget.findChildren(QLineEdit)
        assert len(myChildren) == 4

    def test_buildFormMinimumNeeds(self):
        """Test that we can build a form by passing it a function and params.
        """
        myFunctionId = 'Flood Evacuation Function Vector Hazard'
        myFunctionList = get_plugins(myFunctionId)
        assert len(myFunctionList) == 1
        assert myFunctionList[0].keys()[0] == myFunctionId

        myDialog = FunctionOptionsDialog(None)
        myParameters = {
            'thresholds': [1.0],
            'postprocessors': {
                'Gender': {'on': True},
                'Age': {
                    'on': True,
                    'params': {
                        'youth_ratio': 0.263,
                        'elderly_ratio': 0.078,
                        'adult_ratio': 0.659}}}}

        myDialog.build_form(myParameters)

        assert myDialog.tabWidget.count() == 2

        myChildren = myDialog.tabWidget.findChildren(QLineEdit)
        assert len(myChildren) == 4

    def test_buildWidget(self):
        myDialog = FunctionOptionsDialog(None)
        value = myDialog.build_widget(myDialog.configLayout, 'foo', [2.3])
        myWidget = myDialog.findChild(QLineEdit)

        # initial value must be same with default
        assert value() == [2.3]

        # change to 5.9
        myWidget.setText('5.9')
        assert value() == [5.9]

        myWidget.setText('5.9, 70')
        assert value() == [5.9, 70]

        myWidget.setText('bar')
        try:
            value()
        except ValueError:
            ## expected to raises this exception
            pass
        else:
            raise Exception("Fail: must be raise an exception")

    def test_parse_input(self):
        function_input = {
            'thresholds': lambda: [1.0],
            'postprocessors': {
                'Gender': {'on': lambda: True},
                'Age': {
                    'on': lambda: True,
                    'params': {
                        'youth_ratio': lambda: 0.263,
                        'elderly_ratio': lambda: 0.078,
                        'adult_ratio': lambda: 0.659}}}}

        dialog = FunctionOptionsDialog(None)
        result = dialog.parse_input(function_input)
        print result
        expected = OrderedDict([
            ('thresholds', [1.0]),
            ('postprocessors', OrderedDict([
                ('Gender', OrderedDict([('on', True)])),
                ('Age', OrderedDict([
                    ('on', True),
                    ('params', OrderedDict([
                        ('elderly_ratio', 0.078),
                        ('youth_ratio', 0.263),
                        ('adult_ratio', 0.659)]))]))]))])
        # noinspection PyPep8Naming
        self.maxDiff = None
        self.assertDictEqual(result, expected)

if __name__ == '__main__':
    suite = unittest.makeSuite(FunctionOptionsDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
