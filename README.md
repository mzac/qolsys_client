# qolsys_client

Python package to talk to Qolsys Alarm Panels

This package was inspired by a conversation on the Home Assistant forum:

<https://community.home-assistant.io/t/qolsys-iq-panel-2-and-3rd-party-integration/231405>

# NOTE:

***Please use the following project instead of this project.  It is much more mature compared to this initial implementation.***

<https://github.com/XaF/qolsysgw>

# Usage:

1. Run main.py (--help for parameters and help)

2. Publish JSON formatted messages to the mqtt topic (qolsys/requests by default):

```
{"event":"INFO", "token":"blah"}
{"event":"ARM", "arm_type":"stay", "partition_id": 0, "token":"blah"}
{"event":"ARM", "arm_type":"away", "partition_id": 0, "token":"blah"}
{"event":"DISARM", "usercode":"0000", "token":"blah"}
```

3. Events will publish to the following topics:
    - qolsys/INFO
    - qolsys/ZONE_EVENT
    - qolsys/ZONE_UPDATE

4. I have a node-red workflow listening to those events creating the sensors
