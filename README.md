# Spacebridge

Hologram provides a service called Spacebridge that allows you to create secure, authenticated tunnels to send data to a device with a Hologram SIM card connected to the cellular network. With Spacebridge, you can send inbound traffic to any port on the device.

[Follow the guide here](https://www.hologram.io/guides/secure-tunneling-with-spacebridge)

## Useful Command Line Arguments for Spacebridge Client

* `--text-mode`: Display all prompts as text on the command line instead of in a GUI.
* `--apikey`: Specify your Hologram API key on the command line.
* `--forward`: Specify a forward in the format <linkid>:<device port>:<forwarded local port>. You can specify this option multiple times. Use this in combination with --text-mode to create a fully scripted tunneling setup.
* `--help`: Display additional options
