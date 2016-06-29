import os
import rospy

from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QWidget

from sunfish_ecu.msg import Depth
from sunfish_ecu.msg import INS
from sunfish_ecu.msg import MagField
from sunfish_ecu.msg import Power
from sunfish_ecu.msg import Status
from sensor_msgs.msg import Temperature

class MyPlugin(Plugin):

    def __init__(self, context):
        super(MyPlugin, self).__init__(context)
        # Give QObjects reasonable names
        self.setObjectName('MyPlugin')
        rospy.loginfo("Remora: ECU Console")

        # Process standalone plugin command-line arguments
        from argparse import ArgumentParser
        parser = ArgumentParser()
        # Add argument(s) to the parser.
        parser.add_argument("-q", "--quiet", action="store_true",
                      dest="quiet",
                      help="Put plugin in silent mode")
        args, unknowns = parser.parse_known_args(context.argv())
        if not args.quiet:
            print 'arguments: ', args
            print 'unknowns: ', unknowns

        # Create QWidget
        self._widget = QWidget()
        # Get path to UI file which is a sibling of this file
        # in this example the .ui and .py file are in the same folder
        ui_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ecu_console.ui')
        # Extend the widget with all attributes and children from UI file
        loadUi(ui_file, self._widget)
        # Give QObjects reasonable names
        self._widget.setObjectName('MyPluginUi')
        # Show _widget.windowTitle on left-top of each plugin (when
        # it's set in _widget). This is useful when you open multiple
        # plugins at once. Also if you open multiple instances of your
        # plugin at once, these lines add number to make it easy to
        # tell from pane to pane.
        self._widget.setWindowTitle('ECU')
        if context.serial_number() > 1:
          self._widget.setWindowTitle(self._widget.windowTitle()+(' (%d)'% context.serial_number()))

        # Add widget to the user interface
        context.add_widget(self._widget)

        self.firstStatusMsg = False

        # Register all subsribers here
        self.intTempSub_  = rospy.Subscriber('/sunfish/ecu/int_temp', Temperature, self.callback_IntTemp)
        self.extTempSub_  = rospy.Subscriber('/sunfish/ecu/ext_temp', Temperature, self.callback_ExtTemp)
        self.depthSub_    = rospy.Subscriber('/sunfish/ecu/depth',    Depth,       self.callback_Depth)
        self.insSub_      = rospy.Subscriber('/sunfish/ecu/INS',      INS,         self.callback_INS)
        self.magFieldSub_ = rospy.Subscriber('/sunfish/ecu/MST',      MagField,    self.callback_MagField)
        self.statusSub_   = rospy.Subscriber('/sunfish/ecu/status',   Status,      self.callback_Status)
        return

    def shutdown_plugin(self):
        self.intTempSub_.unregister()
        self.extTempSub_.unregister()
        self.depthSub_.unregister()
        self.insSub_.unregister()
        self.magFieldSub_.unregister()
        self.statusSub_.unregister()
        pass

    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        # TODO restore intrinsic configuration, usually using:
        # v = instance_settings.value(k)
        pass

    #def trigger_configuration(self):
        # Comment in to signal that the plugin has a way to configure
        # This will enable a setting button (gear icon) in each dock widget title bar
        # Usually used to open a modal configuration dialog

    def formatFloat(self, f):
        return ("%2.2f" % f)

    def callback_IntTemp(self, value):
        self._widget.intTempData.setText(self.formatFloat(value.temperature))
        return

    def callback_ExtTemp(self, value):
        self._widget.extTempData.setText(self.formatFloat(value.temperature))
        return

    def callback_Depth(self, value):
        self._widget.pressureData.setText(self.formatFloat(value.Pressure))
        self._widget.tempData.setText(self.formatFloat(value.Temperature))
        return

    def callback_INS(self, value):
        self._widget.ab_data_0.setText(self.formatFloat(value.AbsOrientation[0]))
        self._widget.ab_data_1.setText(self.formatFloat(value.AbsOrientation[1]))
        self._widget.ab_data_2.setText(self.formatFloat(value.AbsOrientation[2]))

        self._widget.av_Data_0.setText(self.formatFloat(value.AngularVelocity[0]))
        self._widget.av_Data_1.setText(self.formatFloat(value.AngularVelocity[1]))
        self._widget.av_Data_2.setText(self.formatFloat(value.AngularVelocity[2]))

        self._widget.af_data_0.setText(self.formatFloat(value.AccelerationVector[0]))
        self._widget.af_data_1.setText(self.formatFloat(value.AccelerationVector[1]))
        self._widget.af_data_2.setText(self.formatFloat(value.AccelerationVector[2]))

        self._widget.la_Data_0.setText(self.formatFloat(value.LinearAcceleration[0]))
        self._widget.la_Data_1.setText(self.formatFloat(value.LinearAcceleration[1]))
        self._widget.la_Data_2.setText(self.formatFloat(value.LinearAcceleration[2]))

        self._widget.gv_data_0.setText(self.formatFloat(value.GravityVector[0]))
        self._widget.gv_data_1.setText(self.formatFloat(value.GravityVector[1]))
        self._widget.gv_data_2.setText(self.formatFloat(value.GravityVector[2]))
        return

    def callback_MagField(self, value):
        self._widget.mf_data_0.setText(self.formatFloat(value.MagneticField[0]))
        self._widget.mf_data_1.setText(self.formatFloat(value.MagneticField[1]))
        self._widget.mf_data_2.setText(self.formatFloat(value.MagneticField[2]))
        return

    def callback_Status(self, value):
        if self.firstStatusMsg == False:
          self._widget.hwdData.setText("Hwd: " + value.Hardware)
          self._widget.firmwareData.setText("Firmware:" + value.Firmware)
          self.firstStatusMsg = True

        self._widget.voltData.setText(("%2.1f" % value.Voltage))
        self._widget.currentData.setText(("%2.2f" % value.Current))
        self._widget.pwm_lcd_0.display(10)
        self._widget.pwm_lcd_1.display(10)
        self._widget.pwm_lcd_2.display(10)
        self._widget.pwm_lcd_3.display(10)

        self._widget.pwm_lcd_4.display(50)
        self._widget.pwm_lcd_5.display(50)
        self._widget.pwm_lcd_6.display(50)
        self._widget.pwm_lcd_7.display(50)

        self._widget.pwm_lcd_8.display(100)
        self._widget.pwm_lcd_9.display(100)
        self._widget.pwm_lcd_10.display(100)
        self._widget.pwm_lcd_11.display(100)
        return

