
// MQTT 
mqtt_host = 'wangdrew.net';	// hostname or IP address
mqtt_port = 9001;
topic = 'power';		// topic to subscribe to
useTLS = false;
username = null;
password = null;
// username = "jjolie";
// password = "aa";
cleansession = false;


// Influx DB
influxdb_host = '0.0.0.0'
influxdb_port = '8086'

// Kairos DB
kairosHost = 'wangdrew.net'
kairosPort = '8080'
kairosEndpoint = "http://" + kairosHost + ":" + kairosPort + "/api/v1/datapoints/query"