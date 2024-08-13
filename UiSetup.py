import os
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QCheckBox, QLabel, QSlider, QScrollArea, QSizePolicy, QMenuBar, QMenu, QToolBar, QToolButton, QAction
from PySide2.QtCore import Qt, QMetaObject
from PySide2.QtGui import QIcon

from DrawingArea import DrawingArea

class Ui_MainWindow:
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 1500)
        MainWindow.centralWidget = QWidget(MainWindow)
        MainWindow.setCentralWidget(MainWindow.centralWidget)

        # Main layout
        MainWindow.mainLayout = QHBoxLayout(MainWindow.centralWidget)

        # Options layout
        MainWindow.optionsLayout = QVBoxLayout()
        MainWindow.optionsLayout.setSpacing(5)  # Minimal spacing

        # Dropdown to select grid
        MainWindow.gridLabel = QLabel("Select Grid:", MainWindow)
        MainWindow.optionsLayout.addWidget(MainWindow.gridLabel)
        MainWindow.gridDropdown = QComboBox(MainWindow)
        MainWindow.gridDropdown.addItem("Select Grid")
        MainWindow.optionsLayout.addWidget(MainWindow.gridDropdown)

        # Dropdown to select grid color bar
        MainWindow.gridColorBarLabel = QLabel("Select Grid Color Bar:", MainWindow)
        MainWindow.optionsLayout.addWidget(MainWindow.gridColorBarLabel)
        MainWindow.gridColorBarDropdown = QComboBox(MainWindow)
        MainWindow.gridColorBarDropdown.addItem("Rainbow") 
        MainWindow.optionsLayout.addWidget(MainWindow.gridColorBarDropdown)

        # Dropdown to select zone
        MainWindow.zoneLabel = QLabel("Select Zone:", MainWindow)
        MainWindow.optionsLayout.addWidget(MainWindow.zoneLabel)
        MainWindow.zoneDropdown = QComboBox(MainWindow)
        MainWindow.zoneDropdown.addItem("Select Zone")
        MainWindow.optionsLayout.addWidget(MainWindow.zoneDropdown)

        # Dropdown to select zone attribute
        MainWindow.zoneAttributeLabel = QLabel("Select Zone Attribute:", MainWindow)
        MainWindow.optionsLayout.addWidget(MainWindow.zoneAttributeLabel)
        MainWindow.zoneAttributeDropdown = QComboBox(MainWindow)
        MainWindow.zoneAttributeDropdown.addItem("Select Zone Attribute")
        MainWindow.optionsLayout.addWidget(MainWindow.zoneAttributeDropdown)

        # Dropdown to select zone color bar
        MainWindow.zoneAttributeColorBarLable = QLabel("Select Zone Color Bar:", MainWindow)
        MainWindow.optionsLayout.addWidget(MainWindow.zoneAttributeColorBarLable)
        MainWindow.zoneAttributeColorBarDropdown = QComboBox(MainWindow)
        MainWindow.zoneAttributeColorBarDropdown.addItem("Rainbow")
        MainWindow.optionsLayout.addWidget(MainWindow.zoneAttributeColorBarDropdown)

        # Checkbox to show/hide UWI labels
        MainWindow.uwiCheckbox = QCheckBox("Show UWI Labels", MainWindow)
        MainWindow.uwiCheckbox.setChecked(True)
        MainWindow.optionsLayout.addWidget(MainWindow.uwiCheckbox)

        MainWindow.uwiWidthLabel = QLabel("UWI Size:", MainWindow)
        MainWindow.optionsLayout.addWidget(MainWindow.uwiWidthLabel)

        # Slider to change the width of the lines
        MainWindow.uwiWidthSlider = QSlider(Qt.Horizontal, MainWindow)
        MainWindow.uwiWidthSlider.setMinimum(1)
        MainWindow.uwiWidthSlider.setMaximum(100)
        MainWindow.uwiWidthSlider.setValue(25)
        MainWindow.optionsLayout.addWidget(MainWindow.uwiWidthSlider)

        # Label for the opacity slider
        MainWindow.opacityLabel = QLabel("UWI Label Opacity:", MainWindow)
        MainWindow.optionsLayout.addWidget(MainWindow.opacityLabel)

        # Slider to change the opacity of UWI labels
        MainWindow.opacitySlider = QSlider(Qt.Horizontal, MainWindow)
        MainWindow.opacitySlider.setMinimum(0)
        MainWindow.opacitySlider.setMaximum(100)
        MainWindow.opacitySlider.setValue(50)
        MainWindow.optionsLayout.addWidget(MainWindow.opacitySlider)

        # Label for the line width slider
        MainWindow.lineWidthSliderLabel = QLabel("Line Width:", MainWindow)
        MainWindow.optionsLayout.addWidget(MainWindow.lineWidthSliderLabel)

        # Slider to change the width of the lines
        MainWindow.lineWidthSlider = QSlider(Qt.Horizontal, MainWindow)
        MainWindow.lineWidthSlider.setMinimum(1)
        MainWindow.lineWidthSlider.setMaximum(200)
        MainWindow.lineWidthSlider.setValue(25)
        MainWindow.optionsLayout.addWidget(MainWindow.lineWidthSlider)

        MainWindow.lineLabel = QLabel("Line Opacity", MainWindow)
        MainWindow.optionsLayout.addWidget(MainWindow.lineLabel)

        # Slider to change the line opacity
        MainWindow.lineOpacitySlider = QSlider(Qt.Horizontal, MainWindow)
        MainWindow.lineOpacitySlider.setMinimum(0)
        MainWindow.lineOpacitySlider.setMaximum(100)
        MainWindow.lineOpacitySlider.setValue(50)
        MainWindow.optionsLayout.addWidget(MainWindow.lineOpacitySlider)

        # Adding a spacer to push everything to the top
        MainWindow.optionsLayout.addStretch()

        MainWindow.mainLayout.addLayout(MainWindow.optionsLayout, 1)  # Occupy 1/8th of the window

        # Scroll area for the drawing area
        MainWindow.scrollArea = QScrollArea(MainWindow.centralWidget)
        MainWindow.scrollArea.setObjectName("scrollArea")
        MainWindow.scrollArea.setWidgetResizable(True)
        MainWindow.drawingArea = DrawingArea(MainWindow)
        MainWindow.drawingArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        MainWindow.scrollArea.setWidget(MainWindow.drawingArea)
        MainWindow.mainLayout.addWidget(MainWindow.scrollArea, 7)
        MainWindow.drawingArea.leftClicked.connect(MainWindow.handle_left_click)
        MainWindow.drawingArea.rightClicked.connect(MainWindow.handle_right_click)

        # Menu bar
        MainWindow.menu_bar = QMenuBar(MainWindow)
        MainWindow.setMenuBar(MainWindow.menu_bar)

        file_menu = MainWindow.menu_bar.addMenu("Project")

        MainWindow.new_project_action = QAction("Create", MainWindow)
        file_menu.addAction(MainWindow.new_project_action)

        MainWindow.open_action = QAction("Open", MainWindow)
        file_menu.addAction(MainWindow.open_action)

        # Launch menu
        MainWindow.launch_menu = MainWindow.menu_bar.addMenu("Launch")
        MainWindow.launch_menu.setEnabled(False)
        MainWindow.plot_action = QAction("Zone Viewer", MainWindow)
        MainWindow.launch_menu.addAction(MainWindow.plot_action)
        MainWindow.color_action = QAction("Color Editor", MainWindow)
        MainWindow.launch_menu.addAction(MainWindow.color_action)
        MainWindow.zone_viewer_action = QAction("Zone Properties", MainWindow)
        MainWindow.launch_menu.addAction(MainWindow.zone_viewer_action)

        MainWindow.calculate_menu = MainWindow.menu_bar.addMenu("Calculate")
        MainWindow.calculate_menu.setEnabled(False)
        MainWindow.calc_stage_action = QAction("Calculate Stages", MainWindow)
        MainWindow.calculate_menu.addAction(MainWindow.calc_stage_action)
        MainWindow.calc_zone_attribute_action = QAction("Calculate Zone Attributes", MainWindow)
        MainWindow.calculate_menu.addAction(MainWindow.calc_zone_attribute_action)
        MainWindow.calc_well_attribute_action = QAction("Calculate Well Attributes", MainWindow)
        MainWindow.calculate_menu.addAction(MainWindow.calc_well_attribute_action)
        MainWindow.calc_inzone_action = QAction("Calculate in Zone", MainWindow)
        MainWindow.calculate_menu.addAction(MainWindow.calc_inzone_action)


        MainWindow.import_menu = MainWindow.menu_bar.addMenu("Import")
        MainWindow.import_menu.setEnabled(False)
        MainWindow.data_loader_menu_action = QAction("SeisWare Grid and Wells", MainWindow)
        MainWindow.import_menu.addAction(MainWindow.data_loader_menu_action)
        MainWindow.dataload_well_zones_action = QAction("CSV Well Zones and Attributes", MainWindow)
        MainWindow.import_menu.addAction(MainWindow.dataload_well_zones_action)

        MainWindow.export_menu = MainWindow.menu_bar.addMenu("Export")
        MainWindow.export_menu.setEnabled(False)

        MainWindow.export_action = QAction("Export Results", MainWindow)
        MainWindow.export_menu.addAction(MainWindow.export_action)
        MainWindow.export_properties = QAction("Export SWMap Properties", MainWindow)
        MainWindow.export_menu.addAction(MainWindow.export_properties)
        MainWindow.zone_to_sw = QAction("Send Zones to SeisWare", MainWindow)
        MainWindow.export_menu.addAction(MainWindow.zone_to_sw)

        MainWindow.toolbar = QToolBar("Main Toolbar", MainWindow)
        MainWindow.addToolBar(MainWindow.toolbar)

        MainWindow.setWindowIcon(QIcon("icons/ZoneAnalyzer.png"))
        MainWindow.plot_icon = QIcon("icons/plot.ico")
        MainWindow.gun_barrel_icon = QIcon("icons/gunb.ico")
        MainWindow.zoom_in_icon = QIcon("icons/Zoom_in.ico")
        MainWindow.zoom_out_icon = QIcon("icons/Zoom_out.ico")
        MainWindow.exportSw_icon = QIcon("icons/export.ico")
        MainWindow.color_editor_icon = QIcon("icons/color_editor.ico")

        MainWindow.plot_tool_action = QAction(MainWindow.plot_icon, "QC Zones", MainWindow)
        MainWindow.toolbar.addAction(MainWindow.plot_tool_action)

        MainWindow.gun_barrel_action = QAction(MainWindow.gun_barrel_icon, "Create Gun Barrel", MainWindow)
        MainWindow.toolbar.addAction(MainWindow.gun_barrel_action)

        MainWindow.color_editor_action = QAction(MainWindow.color_editor_icon, "Edit Grid Colors", MainWindow)
        MainWindow.toolbar.addAction(MainWindow.color_editor_action)

        # Zoom controls
        MainWindow.zoomOut = QAction(MainWindow.zoom_out_icon, "Zoom Out", MainWindow)
        MainWindow.toolbar.addAction(MainWindow.zoomOut)

        MainWindow.zoomIn = QAction(MainWindow.zoom_in_icon, "Zoom In", MainWindow)
        MainWindow.toolbar.addAction(MainWindow.zoomIn)

        MainWindow.exportSw = QAction(MainWindow.exportSw_icon, "Send to SeisWare", MainWindow)
        MainWindow.toolbar.addAction(MainWindow.exportSw)

        # Toggle button for draw/pan mode
        MainWindow.toggle_button = QToolButton(MainWindow)
        MainWindow.toggle_button.setCheckable(True)
        MainWindow.toggle_button.setIcon(QIcon('icons/pan_icon.png'))  # Default to pan mode icon
        MainWindow.toggle_button.setToolTip("Toggle Draw Mode")
        MainWindow.toggle_button.setChecked(False)  # Default to off
        MainWindow.toolbar.addWidget(MainWindow.toggle_button)

        self.populate_color_bar_dropdowns()

        self.retranslateUi()
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self):
        pass  # If you need to retranslate UI, you can add the code here

    def populate_color_bar_dropdowns(self):
        """Populate the color bar dropdowns with file names from the Palettes directory."""
        palettes_path = r'C:\Users\jerem\source\repos\Well Attribute Viewer\Palettes'
        color_bar_files = [f.split('.')[0] for f in os.listdir(palettes_path) if f.endswith('.pal')]

        self.zoneAttributeColorBarDropdown.addItems(color_bar_files)
        self.gridColorBarDropdown.addItems(color_bar_files)
