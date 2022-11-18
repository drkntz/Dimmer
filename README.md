# Dimmer
A peripheral for microprocessor control of 120V AC.

This project originally started in 2020 as a proof of concept for an AC motor controller, but can be used for many projects involving variable duty cycle AC control. It supports operation for low current (<5A) AC driving as a low-side switch. 

The original board included both an AC triac control and a 5V non-isolated power supply (linkswitch LNK3206). This unit was meant for use in situations where the device is fully enclosed in an insulated housing. However, if fully isolated operation is desired, the Dimmer may be used with an external 5V power supply, as it contains optically isolated triac drive and zero-crossing detection circuits.

The software in this project was used for a raspberry pi to connect with the rev1 board. 

TODO: Schematic printout needs some work, is missing interface header J1. Rev2 will fix this.

# Schematic rev 1
![SCH](https://github.com/drkntz/Dimmer/blob/master/Docs/Dimmer-SCH-V01.png)

# PCB Layout rev 1
![LAY](https://github.com/drkntz/Dimmer/blob/master/Docs/Dimmer-LAY-V01.png)

# PCB 3-D Model rev 1
![3D](https://github.com/drkntz/Dimmer/blob/master/Docs/Dimmer-3D-V01.png)
