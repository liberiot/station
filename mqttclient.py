#########################################################################
#
# Copyright (c) 2016 Daniel Berenguer <dberenguer@panstamp.com>
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
__author__="panStamp S.L.U."
__date__  ="Apr 23, 2016"
#########################################################################

from stationexception import StationException
import paho.mqtt.client as mqtt
import threading
import time


class MqttClient(object):
    """
    MQTT client
    """

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback function: connection completed
        """
        print("Connected to MQTT broker " + self.mqtt_server + " on port " + str(self.mqtt_port))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        topic = self.TOPIC_CONTROL + "/#"
        client.subscribe(topic)   # Control topic
        self.publish_gateway_status("CONNECTED")


    def on_message(self, client, userdata, msg):
        """
        Callback function: message published from server
        """
        if self._packet_received is not None:
            self._packet_received(msg.payload)


    def publish_network_status(self, message):
        """
        Publish network data
        
        @param message text to be transmitted via MQTT
        """
        # Extract device address
        device_address = message[6:30]
        self.publish_lock.acquire()
        try:
            self.mqtt_client.publish(self.TOPIC_NETWORK + "/" + device_address, payload=message, qos=0, retain=False)
            
        finally:
            self.publish_lock.release()      


    def publish_gateway_status(self, status="RUNNING"):
        """
        Publish gateway status
        
        @param status gateway status
        """
        self.publish_lock.acquire()
        try:
            self.mqtt_client.publish(self.TOPIC_GATEWAY, payload=status, qos=0, retain=False)
            
        finally:
            self.publish_lock.release()
            

    def stop(self):
        """
        Stop MQTT client
        """
        self.mqtt_client.loop_stop()


    def set_rx_callback(self, funct):
        """
        Set callback reception function. Notify new MQTT reception
        
        @param funct: Definition of custom Callback function for the reception of packets
        """
        self._packet_received = funct
        
        
    def __init__(self, mqtt_server, mqtt_port, mqtt_topic, user_key, gateway_key):
        """
        Constructor
        
        @param mqtt_server MQTT server
        @param mqtt_port MQTT port
        @param mqtt_topic Main MQTT topic
        @param user_key User key
        @param gateway_key gateway key
        """
        ## Callback
        self._packet_received = None
        
        ## MQTT server information
        self.mqtt_server = mqtt_server
        self.mqtt_port = mqtt_port
        
        ## MQTT topics
        self.TOPIC_NETWORK = str(mqtt_topic + "/" + user_key + "/" + gateway_key + "/" + "network")
        self.TOPIC_CONTROL = str(mqtt_topic + "/" + user_key + "/" + gateway_key + "/" + "control")
        self.TOPIC_GATEWAY = str(mqtt_topic + "/" + user_key + "/" + gateway_key + "/" + "gateway")
        
        ## MQTT client
        self.mqtt_client = mqtt.Client()
       
        # Assign MQTT callbacks
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        
        try:
            # Connecto to MQTT broker
            self.mqtt_client.connect(mqtt_server, mqtt_port, 60)
            
            # Run MQTT thread
            self.mqtt_client.loop_start()
    
            self.publish_lock = threading.Lock()
            
            # Heart beat transmission thread
            hbeat_process = PeriodicHeartBeat(self.publish_gateway_status)
            hbeat_process.start()
            
        except Exception:
            print "Unable to connect to MQTT broker on address " + mqtt_server + "(port " + str(mqtt_port) + ")"


class PeriodicHeartBeat(threading.Thread):
    """
    Periodic transmission of Lagarto server heart beat
    """
    def run(self):
        """
        Start timer
        """
        while True:
            self.send_hbeat()
            time.sleep(60.0)
                      
    def __init__(self, send_hbeat):
        """
        Constructor
        
        @param send_hbeat: Heart beat transmission method
        """
        threading.Thread.__init__(self)
        # Configure thread as daemon
        self.daemon = True
        # Heart beat transmission method
        self.send_hbeat = send_hbeat
        
