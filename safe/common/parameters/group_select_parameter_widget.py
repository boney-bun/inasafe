# coding=utf-8
"""Group Select Parameter Widget."""

from PyQt4.QtGui import (
    QDoubleSpinBox, QVBoxLayout, QRadioButton, QButtonGroup,
    QWidget, QLabel, QSizePolicy, QSpacerItem, QListWidget,
    QGridLayout, QAbstractItemView, QListWidgetItem)
from PyQt4.QtCore import Qt

from safe_extras.parameters.qt_widgets.generic_parameter_widget import (
    GenericParameterWidget)
from safe.definitions.constants import STATIC, SINGLE_DYNAMIC, MULTIPLE_DYNAMIC
import logging

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


class GroupSelectParameterWidget(GenericParameterWidget):

    """Widget class for Group Select Parameter."""

    def __init__(self, parameter, parent=None):
        """Constructor.

        :param parameter: A GroupSelectParameter object.
        :type parameter: GroupSelectParameter
        """
        QWidget.__init__(self, parent)
        self._parameter = parameter

        # Store spin box
        self.spin_boxes = {}

        # Create elements
        # Label (name)
        self.label = QLabel(self._parameter.name)

        # Layouts
        self.main_layout = QVBoxLayout()
        self.input_layout = QVBoxLayout()

        # _inner_input_layout must be filled with widget in the child class
        self.inner_input_layout = QVBoxLayout()

        self.radio_button_layout = QGridLayout()

        # Create radio button group
        self.input_button_group = QButtonGroup()

        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_widget.setDragDropMode(QAbstractItemView.DragDrop)
        self.list_widget.setDefaultDropAction(Qt.MoveAction)
        self.list_widget.setEnabled(False)

        for i, key in enumerate(self._parameter.options):
            value = self._parameter.options[key]
            radio_button = QRadioButton(value.get('label'))
            self.radio_button_layout.addWidget(radio_button, i, 0)
            if value.get('type') == SINGLE_DYNAMIC:
                double_spin_box = QDoubleSpinBox()
                self.radio_button_layout.addWidget(double_spin_box, i, 1)
                double_spin_box.setValue(value.get('value', 0))
                double_spin_box.setMinimum(value.get('constraint', {}).get(
                    'min', 0))
                double_spin_box.setMaximum(value.get('constraint', {}).get(
                    'max', 1))
                double_spin_box.setSingleStep(value.get('constraint', {}).get(
                    'step', 0.01))
                self.spin_boxes[key] = double_spin_box

                # Enable spin box depends on the selected option
                if self._parameter.selected == key:
                    double_spin_box.setEnabled(True)
                else:
                    double_spin_box.setEnabled(False)

            elif value.get('type') == STATIC:
                static_value = value.get('value', 0)
                if static_value is not None:
                    self.radio_button_layout.addWidget(
                        QLabel(str(static_value)), i, 1)
            elif value.get('type') == MULTIPLE_DYNAMIC:
                selected_fields = value.get('value', [])
                if self._parameter.selected == key:
                    self.list_widget.setEnabled(True)
                else:
                    self.list_widget.setEnabled(False)

            self.input_button_group.addButton(radio_button, i)
            if self._parameter.selected == key:
                radio_button.setChecked(True)

        self.inner_input_layout.addLayout(self.radio_button_layout)
        self.inner_input_layout.addWidget(self.list_widget)

        # Put elements into layouts
        self.input_layout.addWidget(self.label)
        self.input_layout.addLayout(self.inner_input_layout)
        self.input_layout.setStretch(0, 1)
        self.input_layout.setStretch(1, 0)

        self.main_layout.addLayout(self.input_layout)
        self.main_layout.addSpacerItem(QSpacerItem(0, 0))

        self.setLayout(self.main_layout)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        # Update list widget
        self.update_list_widget()

        # Connect signal
        self.input_button_group.buttonClicked.connect(
            self.radio_buttons_clicked)

    def get_parameter(self):
        """Obtain list parameter object from the current widget state.

        :returns: A DefaultValueParameter from the current state of widget
        :rtype: DefaultValueParameter
        """
        # Set value for each key
        for key, value in self._parameter.options.items():
            if value.get('type') == STATIC:
                continue
            elif value.get('type') == SINGLE_DYNAMIC:
                new_value = self.spin_boxes.get(key).value()
                self._parameter.set_value_for_key(key, new_value)
            elif value.get('type') == MULTIPLE_DYNAMIC:
                # Need to iterate through all items
                items = []
                for index in xrange(self.list_widget.count()):
                    items.append(self.list_widget.item(index))
                new_value = [i.text() for i in items]
                self._parameter.set_value_for_key(key, new_value)

        # Get selected radio button
        radio_button_checked_id = self.input_button_group.checkedId()
        # No radio button checked, then default value = None
        if radio_button_checked_id == -1:
            self._parameter.selected = None
        else:
            self._parameter.selected = self._parameter.options.keys()[
                radio_button_checked_id]

        return self._parameter

    def update_list_widget(self):
        """Update list widget when radio button is clicked."""
        # Get selected radio button
        radio_button_checked_id = self.input_button_group.checkedId()
        # No radio button checked, then default value = None
        if radio_button_checked_id > -1:
            selected_dict = self._parameter.options.values()[
                radio_button_checked_id]
            if selected_dict.get('type') == MULTIPLE_DYNAMIC:
                for field in selected_dict.get('value'):
                    # Update list widget
                    field_item = QListWidgetItem(self.list_widget)
                    field_item.setFlags(
                        Qt.ItemIsEnabled |
                        Qt.ItemIsSelectable |
                        Qt.ItemIsDragEnabled)
                    field_item.setData(Qt.UserRole, field)
                    field_item.setText(field)
                    self.list_widget.addItem(field_item)

    def radio_buttons_clicked(self):
        """Handler when selected radio button changed."""
        # Disable all spin boxes
        for spin_box in self.spin_boxes.values():
            spin_box.setEnabled(False)
        # Disable list widget
        self.list_widget.setEnabled(False)

        # Get selected radio button
        radio_button_checked_id = self.input_button_group.checkedId()

        if radio_button_checked_id > -1:
            selected_value = self._parameter.options.values()[
                radio_button_checked_id]
            if selected_value.get('type') == MULTIPLE_DYNAMIC:
                # Enable list widget
                self.list_widget.setEnabled(True)
            elif selected_value.get('type') == SINGLE_DYNAMIC:
                selected_key = self._parameter.options.keys()[
                    radio_button_checked_id]
                self.spin_boxes[selected_key].setEnabled(True)

    def select_radio_button(self, key):
        """Helper to select a radio button with key.

        :param key: The key of the radio button.
        :type key: str
        """
        key_index = self._parameter.options.keys().index(key)
        radio_button = self.input_button_group.button(key_index)
        radio_button.click()
