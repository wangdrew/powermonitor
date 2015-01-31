// Influx DB
kairosHost = 'wangdrew.net'
kairosPort = '8080'

//Query parameters
power_avg_window = "24h"

//Display parameters
pmeas_chartmax = 12000 // Max watts

// Seed values used for debugging
debug_daily_dollar_amt = 3.42
debug_month_dollar_amt = 13.23
debug_power_usage = 1500

//init vars
month_prev_query = -1
month_begin_cost = 0.0
query_limit = 3
query_count = 3

//How far back in millis should we look from current time to find a metric?
queryAcceptanceWindow = 5000

// How many milliseconds in a 24 hour day
millisPerDay = 86400000

// KairosDB query endpoint
kairosEndpoint = "http://" + kairosHost + ":" + kairosPort + "/api/v1/datapoints/query"


/* Query JSONs for KairosDB */
function getQueryInstantPower() {
    
    var timeNow = getCurrentMillis()

    return {
        "start_absolute": timeNow - acceptanceWindow,
        "end_absolute": timeNow,
        "metrics" : [{
            "name": "powerW",
            "tags" : {"channel": ["0"]},
            "limit": 1,
            "order": "desc" // most recent
        }]
    }
}

function getQueryAvg24Power() {
    
    var timeNow = getCurrentMillis()
    var time24HrAgo = timeNow - millisPerDay

    return {
        "start_absolute": time24HrAgo,
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
}

function getQueryCostAtDayBeginning() {
    
    var timeNow = getCurrentMillis()
    var timeBeginningDay = getDayBeginningMillis()

    return {
        "start_absolute": timeBeginningDay,
        "end_absolute": timeNow,
        "metrics" : [{
            "name": "cumCost",
            "tags" : {"channel": ["0"]},
            "limit": 1,
            "order": "asc" // earliest
        }]
    }
}

function getQueryCostAtMonthBeginning() { 

    var timeNow = getCurrentMillis()
    var timeBeginningMonth = getMonthBeginningMillis()

    return {
        "start_absolute": timeBeginningMonth,
        "end_absolute": timeNow,
        "metrics" : [{
            "name": "cumCost",
            "tags" : {"channel": ["0"]},
            "limit": 1,
            "order": "asc" // earliest
        }]
    }
}

/* Time utility functions */
function getCurrentMillis() {
    var d = new Date()
    return d.getTime()
}

function getDayBeginningMillis() {
    var d = new Date()
    var currentMillis = d.getTime()

    var beginningUtc = currentMillis - (currentMillis %  millisPerDay)
    return beginningUtc += d.getTimezoneOffset() * 60 * 1000
}

function getMonthBeginningMillis() {
    var d = new Date()
    var dBegin = new Date(
        d.getFullYear(), 
        d.getMonth(), 
        1, 0, 0, 0, 0);
    return dBegin.getTime()
}

/* Kairos DB query functions */
function queryKairosDb(queryJson) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", kairosEndpoint);
    xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xmlhttp.send(JSON.stringify(getQueryInstantPower()));
    var resp = xmlhttp.responseText;    // This needs to wait
    return jQuery.parseJSON(resp);
}


function queryInstantPower() {
    var resp = queryKairosDb(getQueryInstantPower())
    return parseKairosOutput(resp)
}

function queryAvg24Power() {

}

function parseKairosOutput(resp) {
    try {
        return resp['queries'][0]['results'][0]['values'][0][1]
    } catch {
        return "--"
    }
}



/* NVD3 chart initialization */
function overviewPie() {
	
	d3objHandles = {};
	debug_mode = false;
	  
	var powermeter = nv.models.pieChart()
	  .x(function(d) { return d.label })
	  .y(function(d) { return d.value })
	  .showLabels(false)     //Display pie labels
	  .showLegend(false)
	  .labelThreshold(.05)  //Configure the minimum slice size for labels to show up
	  .labelType("key") //Configure what type of data to show in the label. Can be "key", "value" or "percent"
	  .donut(true)          //Turn on Donut mode. Makes pie chart look tasty!
	  .donutRatio(0.76)     //Configure how big you want the donut hole size to be.
	  .color(['#222222', '#FF8000'])
	  .height(500)
	  .width(500)
	  ;

	// powermeter.pie
	// 	.startAngle(function(d) { return d.startAngle/2 - (3*Math.PI)/4; })
	// 	.endAngle(function(d) { return d.endAngle/2 - (Math.PI/4) ;})
	  	
	var updateInterval = 6000; 
	this.initData = [ {'label': 'nonusage', 'value' : pmeas_chartmax} ,
	                {'label' : 'usage', 'value' : 0} , 
	                {'label' : 'daily_cost', 'value' : 0.00} ];

	initializeChart();
	nv.addGraph(powermeter);
	setInterval( function() { update(); }, updateInterval);
    return;

    function parse_dboutput(data) {
        keys = data[0]['columns']
        power_usage_idx = keys.indexOf("power")
        daily_cost_idx = keys.indexOf("daily_cost")
        this.power_usage = data[0]['points'][0][power_usage_idx]
        daily_cost_cents = Math.round(data[0]['points'][0][daily_cost_idx] * 100)
        this.daily_cost = daily_cost_cents / 100
    }

    function parse_dboutput_power_avg(data) {
         keys = data[0]['columns']
         power_avg_idx = keys.indexOf("mean")
         this.power_avg_usage = data[0]['points'][0][power_avg_idx]
    }

    function query_beginning_of_month_cost() {
        curr_date = new Date()
        month_now = curr_date.getMonth()+1
        if (month_now != month_prev_query) {
            // find cost @ beginning of month
            year_now = curr_date.getYear() + 1900

            xmlHttp = new XMLHttpRequest();
            xmlHttp.open( "GET", "http://" + influxdb_host + ":" + influxdb_port + 
            "/db/powerdb/series?u=root&p=root&q=select%20cum_cost%20from%20power%20where" + 
            "%20time%20>%20'" + year_now + "-" + month_now + "-01%2008:01:00.000'%20and%20" + 
            "time%20<%20'" + year_now + "-" + month_now + "-01%2008:02:00.000'%20limit%201", false );
            xmlHttp.send( null );
            resp = xmlHttp.responseText
            resp = jQuery.parseJSON(resp)

            // if undef, find the earliest cum_cost value in DB
            if (resp.length == 0) {
                xmlHttp = new XMLHttpRequest();
                xmlHttp.open( "GET", "http://" + influxdb_host + ":" + influxdb_port + 
                "/db/powerdb/series?u=root&p=root&q=select%20last(cum_cost)%20from%20power", false );
                xmlHttp.send( null );
                resp = xmlHttp.responseText
                resp = jQuery.parseJSON(resp)
                data_idx = resp[0]['columns'].indexOf("last")
                this.month_begin_cost = resp[0]['points'][0][data_idx]
            } else {
                data_idx = resp[0]['columns'].indexOf("cum_cost")
                this.month_begin_cost = resp[0]['points'][0][data_idx]
            }
        }
        month_prev_query = month_now
        return this.month_begin_cost
    }

    function query_monthly_cost() {
        this.monthly_cost = query_current_cum_cost() - query_beginning_of_month_cost()
        this.monthly_cost = Math.round(this.monthly_cost * 100) / 100
    }

    function query_power_average() {
        xmlHttp = new XMLHttpRequest();
        xmlHttp.open( "GET", "http://" + influxdb_host + ":" + influxdb_port + 
            "/db/powerdb/series?u=root&p=root&q=SELECT%20MEAN(power)%20FROM%20power%20group" +
            "%20by%20time(" + power_avg_window + ")%20where%20time%20%3E%20now()%20-%20" + 
            power_avg_window + "%20limit%201", false );
        xmlHttp.send( null );
        resp = xmlHttp.responseText
        parse_dboutput_power_avg(jQuery.parseJSON(resp))
    }

    function query_current_cum_cost() {
        xmlHttp = new XMLHttpRequest();
        xmlHttp.open( "GET", "http://" + influxdb_host + ":" + influxdb_port + 
                "/db/powerdb/series?u=root&p=root&q=select%20first(cum_cost)%20from%20power", false );
        xmlHttp.send(null);
        resp = xmlHttp.responseText
        resp = jQuery.parseJSON(resp)
        data_idx = resp[0]['columns'].indexOf("first")
        this.current_cum_cost = resp[0]['points'][0][data_idx]
        return this.current_cum_cost
    }

    function query_kairosdb(queryJson) {

        var xmlHttp = new XMLHttpRequest();
        xmlhttp.open("POST", "/json-handler");
        xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xmlhttp.send(JSON.stringify(query_json))
        xmlHttp.open( "POST", "http://" + kairos_host + ":" + kairos_port + "api/v1/datapoints/query", false );
        xmlHttp.send( null );
        resp = xmlHttp.responseText
        console.log(resp)

    }

    function update() {
    	
		if (debug_mode) {
			debug_power_usage = debug_power_usage + Math.round((Math.random()*300)-150);
			if (debug_power_usage < 0 || debug_power_usage > 5000) {
				debug_power_usage = 900;
			}
			data = [ {'label': 'nonusage', 'value' : pmeas_chartmax - debug_power_usage},
				{'label' : 'usage', 'value' : debug_power_usage},
	            {'label' : 'daily_cost', 'value' : debug_daily_dollar_amt},
                {'label' : 'monthly_cost', 'value' : debug_month_dollar_amt} ];
            this.power_avg_usage = 1500
            this.monthly_cost = debug_month_dollar_amt
		}

		else {
            dollar_amt = 0.0
            power_usage = 0
            power_data_array = null

            try {

                query_kairosdb()
                var xmlHttp = null;
                xmlHttp = new XMLHttpRequest();
                
                // Get instantaneous datapoints - power, daily cost
                xmlHttp.open( "GET", "http://" + influxdb_host + ":" + influxdb_port + 
                    "/db/power_now/series?u=root&p=root&q=select%20*%20from%20power%20limit%201", false );

                xmlHttp.send( null );
                resp = xmlHttp.responseText
                parse_dboutput(jQuery.parseJSON(resp))

                // Limit these queries to speed up client performance
                if (query_count >= query_limit) {
                    console.log("query for data")
                    query_power_average()   // Get 24h average for power
                    query_monthly_cost()    // Get the monthly cost
                    query_count = 0;
                } else { query_count++; }


            }

            catch(err){
                console.log('Error getting influx data' + err);
            }

			data = [ {'label': 'nonusage', 'value' : pmeas_chartmax - this.power_usage},
				{'label' : 'usage', 'value' : this.power_usage},
	            {'label' : 'daily_cost', 'value' : this.daily_cost},
                {'label' : 'monthly_cost', 'value' : this.monthly_cost}];
		}

		// Updates text labels    	
        updateLabels(data);
    	
        // Updates circle meter
        d3.select('#power')
        	.datum(data.slice(0,2)) 
        	.transition().duration(1000)
        	.call(powermeter);
    }
    
    function initializeChart() {
        d3.select('#power')
	    	.datum(this.initData.slice(0,2))
	    	.transition().duration(1000)
	    	.call(powermeter);
        
        initLabels();
    }
    
    function initLabels() {
    	// kW top label
        kwtop_label = d3.select('#power')
        .append("text")
        .attr({'x': 252, 'y': 170, 'text-anchor': 'middle', 'fill' : '#FF8000'})
        .style('font-size', '30px')
        .style('font-weight', 'normal')
    	.text("watts");
        
        // kW amount
        kwamt_label = d3.select('#power')
        .append('text')
    	.attr({'x': 257, 'y': 265, 'text-anchor': 'middle', 'fill' : '#FFFFFF'})
    	.style('font-size', '100px') 
    	.style('font-weight', 'normal')
    	.text("0");
        
        // dollar amount
        dollarDayAmt_label = d3.select('#power')
        .append('text')
    	.attr({'x': 270, 'y': 325, 'text-anchor': 'end', 'fill' : '#FFFFFF'})
    	.style('font-weight', 'normal')
    	.style('font-size', '40px') 
    	.text("");
        
        // today text
        today_label = d3.select('#power')
        .append('text')
        .attr({'x': 305, 'y': 325, 'text-anchor': 'middle', 'fill' : '#FFFFFF'})
        .style('font-weight', '300px')
        .style('font-size', '20px') 
        .text("today"); // "today" 

        // dollar month amount
        dollarMoAmt_label = d3.select('#power')
        .append('text')
        .attr({'x': 275, 'y': 380, 'text-anchor': 'end', 'fill' : '#FFFFFF'})
        .style('font-weight', 'normal')
        .style('font-size', '40px') 
        .text("");
        
        // month text
        month_label = d3.select('#power')
        .append('text')
        .attr({'x': 310, 'y': 380, 'text-anchor': 'middle', 'fill' : '#FFFFFF'})
        .style('font-weight', '300px')
        .style('font-size', '20px') 
        .text("month"); // "month"
      	
        avg_triangle = d3.select('#power')
        .append('polygon')
        .attr({'points' : []})
        .style('fill', '#FF8000')

    	this.d3objHandles = {
    			"kwtop" : kwtop_label,
    			"kwamt" : kwamt_label,
    			"dollarDayAmt" : dollarDayAmt_label,
                "dollarMoAmt" : dollarMoAmt_label,
                "month_label" : month_label,
                "avgTriangle" : avg_triangle
    			}
    }
    
    function updateLabels(data) {
    	kwamt_raw = data[1]['value']
        kwamt_display = kwamt_raw
    	dollarDayAmt = data[2]['value']
        dollarMonthAmt = data[3]['value']

    	kwtop_handle = this.d3objHandles["kwtop"];
    	kwamt_handle = this.d3objHandles["kwamt"];
    	dollarDayAmt_handle = this.d3objHandles["dollarDayAmt"]
        dollarMoAmt_handle = this.d3objHandles["dollarMoAmt"]
        avgTriangle_handle = this.d3objHandles["avgTriangle"]
        monthLabel_handle = this.d3objHandles["month_label"]
		
        // Update the kilowatts/watts label and rounds the kwamt
    	if (kwamt_raw >= 1000) {
    		kwtop_handle.text("kilowatts");
    		kwamt_display = (kwamt_raw/1000).toPrecision(3);
    	} else if (kwamt_raw >= 10000) {
    		kwtop_handle.text("kilowatts");
    		kwamt_display = (kwamt_raw/1000).toPrecision(4);
    	} else {
    		kwtop_handle.text("watts");
    	}

        // Center the month labels and month amounts
        if (this.monthly_cost >= 10) {
            dollarMoAmt_handle.attr({'x': 284})
            monthLabel_handle.attr({'x': 320})
        } else {
            dollarMoAmt_handle.attr({'x': 270})
            monthLabel_handle.attr({'x': 310})
        }

        // Higher than average
        if (kwamt_raw >= this.power_avg_usage) {
            avgTriangle_handle.attr({'points' : [252,110, 238,130, 266,130]});
            avgTriangle_handle.style('fill', '#FF8000')
            kwtop_handle.attr({'fill': '#FF8000'})
            powermeter.pie.color(['#222222', '#FF8000'])
            kwamt_handle.attr({'fill': '#FFDAC2'})

        // Lower than average
        } else {
            avgTriangle_handle.attr({'points' : [252,130, 238,110, 266,110]});
            avgTriangle_handle.style('fill', '#6DD900')
            kwtop_handle.attr({'fill': '#6DD900'})
            powermeter.pie.color(['#222222', '#6DD900'])
            kwamt_handle.attr({'fill': '#E5FFC5'})

        }
    	
    	kwamt_handle.text(kwamt_display);
        dollarDayAmt_handle.text('$' + dollarDayAmt);
        dollarMoAmt_handle.text('$' + dollarMonthAmt);
        // dollarMoAmt_handle.text('$' + dollarMoAmt)
    }
}


/* init stuff */
overviewPie();



