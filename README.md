# send-to-influx has moved

This project now lives at **<https://github.com/L337-org/send-to-influx>**.

Everything is there: source, issues, releases, and the APT repository.

## If you installed via the old APT repo

The old APT URL (`https://gavinlucas.github.io/send-to-influx/`) still works, but it serves a
**frozen snapshot** (last version: 4.2) and will never receive updates. Switch to the new,
permanent URL with:

```sh
sudo sed -i 's|https://gavinlucas.github.io/send-to-influx/|https://apt.l337.org/|' /etc/apt/sources.list.d/send-to-influx.list
curl -fsSL https://apt.l337.org/send-to-influx.gpg | sudo tee /usr/share/keyrings/send-to-influx.gpg >/dev/null
sudo apt update
```

The package signing key is unchanged; re-fetching it is just belt-and-braces.

## Why this repo exists

It holds the frozen APT snapshot on its `gh-pages` branch so that existing installs pointing at
the old URL keep working (a plain `apt update` succeeds) instead of breaking with an error.
Nothing else here is maintained — please file issues and pull requests at
[L337-org/send-to-influx](https://github.com/L337-org/send-to-influx).
