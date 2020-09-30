# Monitoring
Monitoring things like Kostal Piko BA; BYD HV...

### Python Virtual - Environment
I suggest to install a virtual environment for your monitoring purposes in order
not to mess around with the local installations. For each monitoring there is a
requirements*.txt which contains the necessary packages. Those can be easily installed by
```bash
pip3 install requirements_USV.txt
```

### Edit config.ini
The config.ini needs to be adopted so that it fits to your environment/Passwords/IPs

### Enabling services
For each monitoring device the serivce needs to be enabled.
Make sure that the path within the *.service file has been adopted to your environment.
```bash
sudo systemctl link /home/pi/PythonProgs/monitoring/log_USV.service
sudo systemctl enable log_USV
sudo systemctl start log_USV
sudo systemctl daemon-reload
```
