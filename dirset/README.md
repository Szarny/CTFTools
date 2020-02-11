# CTFTools/dirset
Directory setter for CTFd.

# Usage
After setting `config.json`, execute the following command.
```
python dirset.py
```

# config.json
|key|value|
|:-:|:-|
|url|URL of the top page of CTFd.|
|savedir|Directory to save.|
|session|`session` value of your Cookie.|
|solver|File name of the solver script.|
|mode|set `moderate` then reduce the server's load (but it's time-consuming).|


## Example
```json
{
    "url": "https://demo.ctfd.io/",
    "savedir": "./chal",
    "session": "",
    "solver": "solver.py",
    "mode": "moderate"
}
```