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
__date__  ="Apr 24, 2016"
#########################################################################

from config import Config
from modemmanager import ModemManager
from stationexception import StationException
import signal
import os
import sys


class Station():
    """
    Master Station class
    """
    ## Config file
    CONFIG_FILE = "config.json"
    
       
    def __init__(self):
        """
        Class constructor
        """
        
        ## List of serial modems
        self.modem_managers = []
        
        ## Config file
        try:
            cfg_location = os.path.join(os.path.dirname(sys.argv[0]), Station.CONFIG_FILE)
            config = Config(cfg_location)
            
            # for each serial port
            for port_config in config.serial_ports:
                # Create and start serial modem
                modem_manager = ModemManager(port_config.name, port_config.speed, True, config.mqtt_server, config.mqtt_port, config.mqtt_topic, config.user_key, config.gateway_key)
                # Append modem to list
                self.modem_managers.append(modem_manager)
                
        except StationException:
            raise


def signal_handler(signal, frame):
    """
    Handle signal received
    """
    sys.exit(0)


if __name__ == '__main__':
   
    # Catch possible SIGINT signals
    signal.signal(signal.SIGINT, signal_handler)

    try:      
        # SWAP manager
        station = Station()     
    except StationException as ex:
        ex.display()

    signal.pause()

