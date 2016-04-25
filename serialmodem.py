#########################################################################
#
# Copyright (c) 2016 panStamp <contact@panstamp.com>
# 
# This file is part of the panStamp project.
# 
# panStamp  is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
# 
# panStamp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with panStamp; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 
# USA
#
#########################################################################
__author__="Daniel Berenguer"
__date__ ="Apr 22, 2016"
#########################################################################

import time
from serialport import SerialPort
from stationexception import StationException


class SerialModem:
    """
    Class representing a serial panstamp modem
    """

    class Mode:
        """
        Serial modes
        """
        DATA = 0
        COMMAND = 1


    def stop(self):
        """
        Stop serial gateway
        """
        if self._serport is not None:
            self._serport.stop()


    def serial_packet_received(self, buf):
        """
        Serial packet received. This is a callback function called from
        the SerialPort object
        
        @param buf: Serial packet received in String format
        """        
        # If modem in command mode
        if self._sermode == SerialModem.Mode.COMMAND:
            self._atresponse = buf
            self.__atresponse_received = True
        # If modem in data mode
        else:
            # Waiting for ready signal from modem?
            if self._wait_modem_start == False:
                if buf == "Modem ready!":
                    self._wait_modem_start = True
            # Pass serial packet to parent class
            elif self._packet_received is not None:
                self._packet_received(buf)


    def set_rx_callback(self, funct):
        """
        Set callback reception function. Notify new CcPacket reception
        
        @param cbFunct: Definition of custom Callback function for the reception of packets
        """
        self._packet_received = funct
        

    def enter_command_mode(self):
        """
        Enter command mode (for AT commands)
        
        @return True if the serial gateway does enter Command Mode. Return false otherwise
        """
        if self._sermode == SerialModem.Mode.COMMAND:
            return True
        
        self._sermode = SerialModem.Mode.COMMAND
        response = self.runAtCommand("+++", 5000)

        if response is not None:
            if response[:2] == "OK":
                return True
        
        self._sermode = SerialModem.Mode.DATA
        return False


    def enter_data_mode(self):
        """
        Enter data mode (for Rx/Tx operations)
        
        @return True if the serial gateway does enter Data Mode. Return false otherwise
        """
        if self._sermode == SerialModem.Mode.DATA:
            return True
        
        response = self.run_at_command("ATO\r")
        
        if response is not None:
            if response[0:2] == "OK":
                self._sermode = SerialModem.Mode.DATA;
                return True;
        
        return False;

    
    def reset(self):
        """
        Reset serial gateway
        
        @return True if the serial gateway is successfully restarted
        """
        # Switch to command mode if necessary
        if self._sermode == SerialModem.Mode.DATA:
            self.enter_command_mode()
        
        # Default state after reset
        self._sermode = SerialModem.Mode.DATA
        # Run AT command
        response = self.run_at_command("ATZ\r")
        if response is None:
            return False
        
        if "ready" in response or response[0:2] == "OK":
            return True
        
        return False


    def run_at_command(self, cmd="AT\r", timeout=1000):
        """
        Run AT command on the serial gateway
        
        @param cmd: AT command to be run
        @param timeout: Period after which the function should timeout
        
        @return Response received from gateway or None in case of lack of response (timeout)
        """
        self.__atresponse_received = False
        # Send command via serial
        if self._serport is None:
            raise SwapException("Port " + self.portname + " is not open")

        # Skip wireless packets
        self._atresponse = "("
        # Send serial packet
        self._serport.send(cmd)
        
        # Wait for response from modem
        while len(self._atresponse) == 0 or self._atresponse[0] == '(':
            if not self._wait_for_response(timeout):
                return None
        # Return response received from gateway
        return self._atresponse


    def send(self, packet):
        """
        Send packet to serial modem
        
        @param packet: packet to be transmitted
        """
        self._serport.send(packet + "\r")

   
    def set_freq_channel(self, value):
        """
        Set frequency channel for the wireless gateway
        
        @param value: New frequency channel
        """
        # Check format
        if value > 0xFF:
            raise SwapException("Frequency channels must be 1-byte length")
        # Switch to command mode if necessary
        if self._sermode == SerialModem.Mode.DATA:
            self.goToCommandMode()
        # Run AT command
        response =  self.runAtCommand("ATCH=" + "{0:02X}".format(value) + "\r")
        if response is None:
            return False
        if response[0:2] == "OK":
            self.freq_channel = value
            return True
        return False


    def set_sync_word(self, value):
        """
        Set synchronization word for the wireless gateway
        
        @param value: New synchronization word
        """
        # Check format
        if value > 0xFFFF:
            raise SwapException("Synchronization words must be 2-byte length")
        # Switch to command mode if necessary
        if self._sermode == SerialModem.Mode.DATA:
            self.goToCommandMode()
        # Run AT command
        response = self.runAtCommand("ATSW=" + "{0:04X}".format(value) + "\r")
        if response is None:
            return False
        if response[0:2] == "OK":
            self.syncword = value
            return True
        else:
            return False


    def set_device_address(self, value):
        """
        Set device address for the serial gateway
        
        @param value: New device address
        """
        # Check format
        if value > 0xFF:
            raise SwapException("Device addresses must be 1-byte length")
        # Switch to command mode if necessary
        if self._sermode == SerialModem.Mode.DATA:
            self.goToCommandMode()
        # Run AT command
        response = self.runAtCommand("ATDA=" + "{0:02X}".format(value) + "\r")
        if response is None:
            return False
        if response[0:2] == "OK":
            self.devaddress = value
            return True
        else:
            return False
    
    def _wait_for_response(self, millis):
        """
        Wait a given amount of milliseconds for a response from the serial modem
        
        @param millis: Amount of milliseconds to wait for a response
        """
        loops = millis / 10
        while not self.__atresponse_received:
            time.sleep(0.01)
            loops -= 1
            if loops == 0:
                return False
        return True


    def __init__(self, portname="/dev/ttyUSB0", speed=38400, verbose=False):
        """
        Class constructor
        
        @param portname: Name/path of the serial port
        @param speed: Serial baudrate in bps
        @param verbose: Print out SWAP traffic (True or False)
        """
        # Serial mode (command or data modes)
        self._sermode = SerialModem.Mode.DATA
        # Response to the last AT command sent to the serial modem
        self._atresponse = ""
        # AT response received from modem
        self.__atresponse_received = None
        # "Packet received" callback function. To be defined by the parent object
        self._packet_received = None
        ## Name(path) of the serial port
        self.portname = portname
        ## Speed of the serial port in bps
        self.portspeed = speed
        ## Hardware version of the serial modem
        self.hwversion = None
        ## Firmware version of the serial modem
        self.fwversion = None

        try:
            # Open serial port
            self._serport = SerialPort(self.portname, self.portspeed, verbose)
            # Define callback function for incoming serial packets
            self._serport.set_rx_callback(self._serial_packet_received)
            # Run serial port thread
            self._serport.start()
               
            # This flags switches to True when the serial modem is ready
            self._wait_modem_start = False
            start = time.time()
            soft_reset = False
            while self._wait_modem_start == False:
                elapsed = time.time() - start
                if not soft_reset and elapsed > 5:
                    self.reset()
                    soft_reset = True
                elif soft_reset and elapsed > 10:
                    raise SwapException("Unable to reset serial modem")

            # Retrieve modem settings
            # Switch to command mode
            if not self.goToCommandMode():
                raise SwapException("Modem is unable to enter command mode")
    
            # Hardware version
            response = self.runAtCommand("ATHV?\r")
            if response is None:
                raise SwapException("Unable to retrieve Hardware Version from serial modem")
            self.hwversion = long(response, 16)
    
            # Firmware version
            response = self.runAtCommand("ATFV?\r")
            if response is None:
                raise SwapException("Unable to retrieve Firmware Version from serial modem")
            self.fwversion = long(response, 16)
    
            # Frequency channel
            response = self.runAtCommand("ATCH?\r")
            if response is None:
                raise SwapException("Unable to retrieve Frequency Channel from serial modem")
            ## Frequency channel of the serial gateway
            self.freq_channel = int(response, 16)
    
            # Synchronization word
            response = self.runAtCommand("ATSW?\r")
            if response is None:
                raise SwapException("Unable to retrieve Synchronization Word from serial modem")
            ## Synchronization word of the serial gateway
            self.syncword = int(response, 16)
    
            # Device address
            response = self.runAtCommand("ATDA?\r")
            if response is None:
                raise SwapException("Unable to retrieve Device Address from serial modem")
            ## Device address of the serial gateway
            self.devaddress = int(response, 16)
    
            # Switch to data mode
            self.goToDataMode()
        except:
            raise

