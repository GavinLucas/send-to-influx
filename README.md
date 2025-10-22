HueToInflux
===========

https://github.com/GavinLucas/send-to-influx
-----------------------------------------

Script to take data from various APIs and post it to InfluxDB in order to view the data in Grafana.

Hue Bridge
----------
It currently supports Hue Bridges and also MyEnergi Zappi car chargers.

It will collect occupancy, temperature and light readings from Hue Motion Sensors, on/off state 
of Smart Plugs and the brightness of lights, but could be modified to collect other data from the bridge.

- Temperature data uses the units specified in the settings file
- Light level is in lux
- Occupancy (movement) is output as boolean 0 or 1 (1 for movement detected)
- Smart Plugs state is also output as boolean 0 or 1 (1 for on)
- Brightness of dimmable lights is output as a percentage

To create a username and password for the Hue Bridge, follow the instructions 
here: https://developers.meethue.com/develop/get-started-2/

MyEnergi Zappi
--------------

Information on how to obtain your API key is available here:
https://support.myenergi.com/hc/en-gb/articles/5069627351185-How-do-I-get-an-API-key

Some information on the API fields is available here:
https://github.com/twonk/MyEnergi-App-Api

Running the script
------------------
- copy example_settings.yaml to settings.yaml
  - Change the permissions of the file, e.g. `chmod 600 settings.yaml`, so that it's not readable 
  by other users
  - Fill in the values for your devices and InfluxDB
- Install the requirements with `pip install -r requirements.txt`
- Leave the script running in a screen session and sit back and watch the data roll in.

There are a few options that can be passed to the script and a couple of these can help you to debug and also to help you understand your data:

- To specify the data source, you can use the 'source' option, e.g. `sendtoinflux.py --source zappi`.
- To dump all the data from the Hue Bridge in order to see the names, etc., run `sendtoinflux.py --dump` 
and it will output all the data returned as json.
- To print the data rather than send it to InfluxDB, run `sendtoinflux.py --print` and it will output the
parsed data structure as json.

Usage
-----
>$ ./.venv/bin/python ./sendtoinflux.py --help  
>usage: sendtoinflux.py [-h] [-d] [-p] -s SOURCE
>
>Send Hue Data to InfluxDB
>
>options:  
> &emsp; -h, --help            show this help message and exit  
> &emsp; -d, --dump            dump the data to the console  
> &emsp; -p, --print           print the data rather than sending it to InfluxDB  
> &emsp; -s, --source SOURCE   the source of the data to send to InfluxDB (hue,
>                        zappi, etc.) - default is "hue"  
