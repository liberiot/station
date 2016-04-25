#########################################################################
#
# Copyright (c) 2016 Daniel Berenguer <dberenguer@usapiens.com>
#
# This file is part of the lagarto project.
#
# lagarto  is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# lagarto is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with panLoader; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
# USA
#
#########################################################################
__author__="Daniel Berenguer"
__date__  ="$Apr 22, 2016$"
#########################################################################

from stationexception import StationException
import json

class SerialConfig:
    """
    Serial port class
    
    @param name name of the serial port
    @param speed serial bitrate
    """
    def __init__(self, name, speed):
        self.name = name
        self.speed = speed
        
    
class Config:
    """
    Config Class
    """
    def __init__(self, filename):
        """
        Class constructor
        
        @param filename path to the configuration file
        """
        ## List of serial ports
        self.serial_ports = []
        
        ## MQTT information
        self.config_mqtt_server = None
        self.config_mqtt_port = None
        self.config_mqtt_topic = None
        
        ## Config file
        try:
            config_file = open(filename)
            config = json.load(config_file)
            config_serial = config["serial"]
            config_mqtt = config["mqtt"]
            config_file.close()
            
            self.mqtt_server = config_mqtt["mqttserver"]
            self.mqtt_port = config_mqtt["mqttport"]
            self.mqtt_topic = config_mqtt["mqttmaintopic"]
            self.user_key = config_mqtt["userkey"]
            self.gateway_key = config_mqtt["gatewaykey"]
            
            # for each serial port
            for port in config_serial:
                if "port" in port and "speed" in port:
                    serial_config = SerialConfig(name=port["port"], speed=port["speed"])
                    self.serial_ports.append(serial_config)
                
        except IOError as ex:
            raise StationException("Unable to read config file " + filename)

