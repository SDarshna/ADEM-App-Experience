# ADEM-App-Experience
ADEM APIs to fetch user list with a specific App experience score.

Use case: Retrieve all end users with devices that have less than a given Experience Score

Script Input:
usage: app-score.py [-h] [-t1 T1SECRET] [-expScore EXPSCORE] [-days DAYS]

Retrieve all end users with devices that have less than a given Experience Score .

optional arguments:
  -h, --help            show this help message and exit
  -t1 T1SECRET, --T1Secret T1SECRET
                        Input secret file in .yml format for the tenant(T1)
  -expScore EXPSCORE, --expScore EXPSCORE
                        Experience score threshold below which the users will be listed
  -days DAYS, --Days DAYS
                        Data fetched for the last n days




Script Output:
(base) app-score % ./app-score.py -expScore 60 -days 30
+--------------------------+------------------+
| Users                    | Experience Score |
+==========================+==================+
| BlueyHeeler@panwsase.com | 58.9             |
+--------------------------+------------------+
