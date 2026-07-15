# send-to-influx APT repository (FROZEN — project has moved)

This branch is a **frozen snapshot** of the send-to-influx flat APT repository, kept so that
existing installs pointing at `https://gavinlucas.github.io/send-to-influx/` keep working.
**Last published version: 4.2. It will never receive updates.**

The project now lives at <https://github.com/L337-org/send-to-influx>, and the live APT
repository is at **<https://apt.l337.org/>**. To switch an existing install:

```sh
sudo sed -i 's|https://gavinlucas.github.io/send-to-influx/|https://apt.l337.org/|' /etc/apt/sources.list.d/send-to-influx.list
curl -fsSL https://apt.l337.org/send-to-influx.gpg | sudo tee /usr/share/keyrings/send-to-influx.gpg >/dev/null
sudo apt update
```
