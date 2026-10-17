@echo off
chcp 65001 > nul
echo ========================================================
echo  ColdChain DigitalTwin 24/7 MQTT to MySQL Daemon
echo ========================================================
echo.
py -3.10 cloud_backend\mqtt_to_mysql_daemon.py
pause
