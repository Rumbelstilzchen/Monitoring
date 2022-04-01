# Monitoring
Monitoring things like Kostal Piko BA; BYD HV...

### Python Virtual - Environment
I suggest to install a virtual environment for your monitoring purposes in order
not to mess around with the local installations. For each monitoring there is a
requirements*.txt which contains the necessary packages. Those can be easily installed by
```bash
pip3 install -r requirements_USV.txt
```

### Edit config.ini
The config.sample.ini needs to be renamed to config.ini and then
adopted so that it fits to your environment/Passwords/IPs

### Database
Currently only MySQL/MariaDB is supported.
The Table structures, views, procedures and events are stored in:
```bash
./base_MYSQL/SQL_structure/
```
You might import them with:
```bash
mysql -u username -p name_of_DB < [sql-file].sql
```

### direct Usage
Each monitoring can bee called - e.g. for testing - directly:
```bash
[python path]/python monitoring_template.py [module_name]
```
module_name can currently be any of:
  * BYD
  * BYD_Cell_voltage
  * DWD
  * DWD_SIM
  * Kostal_Piko_BA
  * USV
  * Luxtronik
  * Elgris

### Enabling services
For each monitoring device the serivce needs to be enabled.
Make sure that the path within the *.service file has been adopted to your environment.
```bash
sudo systemctl link /home/pi/PythonProgs/monitoring/log_USV.service
sudo systemctl enable log_USV
sudo systemctl start log_USV
sudo systemctl daemon-reload
```

### Visualisation (Grafana)
The dashboards I have in use with grafana are placed within ./00_grafana/
Each Dashboard has its own *.json file. To give an impression what is within each boards a report
exported to *.pdf is attached

### Disclaimer
**Warning:**
Please note that you are responsible to operate this program and comply with regulations imposed on you by other
Website providers (such as e.g. the DWD website being polled)

Therefore, the author does not provide any guarantee or warranty concerning to correctness, functionality or
performance and does not accept any liability for damage caused by this module, examples or mentioned information.

   **Thus, use it on your own risk!**
