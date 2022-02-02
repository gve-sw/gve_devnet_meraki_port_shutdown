# GVE DevNet Switch Port Shutdown Scheduling
This prototype allows for its user to (1) select a network, (2) consult the switch ports in that network, (3) declare a schedule for shutdown/start up of those ports, and (4) enable that schedule by using APIs for controlling the switch port status.

## Contacts
* Stien Vanderhallen

## Solution Components
*  Meraki REST API
*  Meraki

## High Level Overview

![](IMAGES/overview.png)

## Installation/Configuration

0. In your terminal, clone this repository

```
$ git clone https://wwwin-github.cisco.com/gve/gve_devnet_meraki_port_shutdown.git
$ cd gve_devnet_meraki_port_shutdown
```

1. In `settings.json`, enter your Meraki API key as `YOUR_MERAKI_API_KEY`. (You can find your Meraki API key under `My Profile` after logging into the [Meraki Dashboard](https://dashboard.meraki.com))

2. Install the required Python libraries

```
$ pip install -r requirements.txt
```

3. Start the application

```
$ python3 app.py
```

4. In a separate terminal, start the background script handling port shutdown/startup

```
$ python3 script.py
```

5. In a browser, navigate to `localhost:9999`

6. In the top right corner, click `Settings`

![](IMAGES/4image.png)

7. In the settings page, check your API key, click `Submit` and select the network you want to schedule the switch ports of.

![](IMAGES/2image.png)


8. Click `Save & Run`. You will be automatically redirected to the landing page.


## Usage

1. On the landing page (`localhost:9999`), consult the list of scheduled ports in your selected network.

![](IMAGES/1image.png)

2. On the right side of the landing page, declare the times at which you want to schedule port shutdwn, and port start-up. Afterwards, click `Schedule ports`. 

![](IMAGES/5image.png)

3. At any time, you can go back to the landing page, respectively the settings page by using the top right icons.

![](IMAGES/3image.png)

# Screenshots

- Settings page

![](IMAGES/2image.png)

- Landing page

![](IMAGES/1image.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.