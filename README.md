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

### Disclaimer
**Warning:**
Please note that you are responsible to operate this program and comply with regulations imposed on you by other Website providers (such as the DWD website being polled)

Therefore, the author does not provide any guarantee or warranty concerning to correctness, functionality or performance and does not accept any liability for damage caused by this module, examples or mentioned information.

   **Thus, use it on your own risk!**
