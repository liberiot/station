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
__date__  ="Apr 22, 2016"
#########################################################################

from serialmodem import SerialModem
from mqttclient import MqttClient
from stationexception import StationException


class ModemManager():
    """
    Serial modem management Class
    """
    
    def serial_packet_received(self, packet):
        """
        Function called whenever a serial frame is received by the serial modem
        
        @param packet serial packet received
        """
        self.mqtt_client.publish_network_status(packet)


    def mqtt_packet_received(self, packet):
        """
        Function called whenever a MQTT message is received
        
        @param packet mqtt packet received
        """
        self.modem.send(packet)
        
        
    def __init__(self, portname, speed, verbose, mqtt_server, mqtt_port, mqtt_topic, user_key, gateway_key):
        """
        Class constructor
        
        @param portname: Name/path of the serial port
        @param speed: Serial baudrate in bps
        @param verbose: Print out SWAP traffic (True or False)
        @param mqtt_server MQTT server
        @param mqtt_port MQTT port
        @param mqtt_topic Main MQTT topic
        @param user_key User key
        @param gateway_key gateway key
        """
        try:
            # Create and start serial modem
            self.modem = SerialModem(portname, speed, verbose)
            # Declare receiving callback function
            self.modem.set_rx_callback(self.serial_packet_received)
            
            # MQTT client
            self.mqtt_client = MqttClient(mqtt_server, mqtt_port, mqtt_topic, user_key, gateway_key)
            # Declare receiving callback function
            self.mqtt_client.set_rx_callback()
            
        except StationException as ex:
            ex.show()

