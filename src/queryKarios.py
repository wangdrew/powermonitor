import requests
import json
import time

KAIROS_URL = "http://wangdrew.net:8080/api/v1/datapoints/query"

timeNow = int(time.time() * 1000)
time24Ago = int((time.time() - 86400) * 1000)

timeMidnight = 1422662400000
timeMonthStart = 1420070400000
acceptanceWindow = 5000

# Instant power
# query = {
# 	"start_absolute": timeNow - acceptanceWindow,
# 	"end_absolute": timeNow,
# 	"metrics" : [{
# 		"name": "powerW",
# 		"tags" : {"channel": ["0"]},
# 		"limit": 1,
# 		"order": "desc" # most recent
# 	}]
# }

# Avg 24hr power
query =  {
            "start_absolute": time24Ago,
            "end_absolute": timeNow,
            "metrics" : [
                {"name" : "powerW",
                 "tags" : {"channel": ["0"]},
                 "limit" : 1,
                    "aggregators": [
                        {"name" : "avg",
                         "sampling": {
                            "value" : 24,
                            "unit" : "hours"}
                        }
                    ]
                }
        	]
        }

# Current cost
# query = {
# 	"start_absolute": timeNow - acceptanceWindow,
# 	"end_absolute": timeNow,
# 	"metrics" : [{
# 		"name": "cumCost",
# 		"tags" : {"channel": ["0"]},
# 		"limit": 1,
#       "order": "desc" # most recent
# 	}]
# }

# Cost at midnight
# query = {
# 	"start_absolute": timeMidnight,
# 	"end_absolute": timeNow,
# 	"metrics" : [{
# 		"name": "cumCost",
# 		"tags" : {"channel": ["0"]},
# 		"limit": 1,
#       	"order": "asc" # earliest
# 	}]
# }


# Cost at 1st of month
# query = {
# 	"start_absolute": timeMonthStart,
# 	"end_absolute": timeNow,
# 	"metrics" : [{
# 		"name": "cumCost",
# 		"tags" : {"channel": ["0"]},
# 		"limit": 1,
#       	"order": "asc" # earliest
# 	}]
# }

resp = requests.post(KAIROS_URL, json.dumps(query))

print(resp.text)