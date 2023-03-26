# 📦 box-stuff 📦
🚚 stuff for a box

## Files/Usage

1. `hvac.py`: main script, run from terminal with `./hvac.py debug` to print log messages to terminal (default log file = `hvac_messages.log`)

1. `hvac_off.py`: when `hvac.py` does not terminate gracefully while the GPIO relay_pin is on, this will shut it off

1. `hvac.service`: template for running on startup
    * replace \<\<these_paths\>\> with actual paths to files
    * save to `/lib/systemd/system/hvac.service`
    * enable: `sudo systemctl enable hvac.service`
    * start: `sudo systemctl start hvac.service`
    * restart: `sudo systemctl restart hvac.service`
    * stop: `sudo systemctl stop hvac.service`


