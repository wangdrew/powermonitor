
pmeas_chartmax = 12000 // Max watts

// Seed values used for debugging
global_dollar_amt = 3.42
global_power_usage = 1500

// Influx DB
influxdb_host = '192.168.1.102'
influxdb_port = '8086'

function overviewPie() {
	
	d3objHandles = {};
	debug_mode = true;
	  
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
	  	
	var updateInterval = 2000; 
	this.initData = [ {'label': 'nonusage', 'value' : pmeas_chartmax} ,
	                {'label' : 'usage', 'value' : 0} , 
	                {'label' : 'dollar_value', 'value' : 0.00} ];

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
    
    function update() {
    	
		if (debug_mode) {
			global_power_usage = global_power_usage + Math.round((Math.random()*300)-150);
			if (global_power_usage < 0 || global_power_usage > 5000) {
				global_power_usage = 900;
			}
			data = [ {'label': 'nonusage', 'value' : pmeas_chartmax - global_power_usage},
				{'label' : 'usage', 'value' : global_power_usage},
	            {'label' : 'dollar_value', 'value' : global_dollar_amt} ];
		}

		else {
            dollar_amt = 0.0
            power_usage = 0
            power_data_array = null

            try {
                var xmlHttp = null;
                xmlHttp = new XMLHttpRequest();
                xmlHttp.open( "GET", "http://" + influxdb_host + ":" + influxdb_port + 
                    "/db/power_now/series?u=root&p=root&q=select%20*%20from%20power%20limit%201", false );
                xmlHttp.send( null );
                resp = xmlHttp.responseText
                parse_dboutput(jQuery.parseJSON(resp))
            }

            catch(err){
                console.log('Error getting influx data' + err);
            }

			data = [ {'label': 'nonusage', 'value' : pmeas_chartmax - this.power_usage},
				{'label' : 'usage', 'value' : this.power_usage},
	            {'label' : 'dollar_value', 'value' : this.daily_cost} ];
		}

		// Updates text labels    	
        updateLabels(data);
    	
        // Updates circle meter
        d3.select('#power')
        	.datum(data.slice(0,2)) 
        	.transition().duration(2000)
        	.call(powermeter);
    }
    
    function initializeChart() {
        d3.select('#power')
	    	.datum(this.initData.slice(0,2))
	    	.transition().duration(2000)
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
    	.attr({'x': 213, 'y': 325, 'text-anchor': 'middle', 'fill' : '#FFFFFF'})
    	.style('font-weight', 'normal')
    	.style('font-size', '40px') 
    	.text("");
        
        // today text
        today_label = d3.select('#power')
        .append('text')
        .attr({'x': 315, 'y': 325, 'text-anchor': 'middle', 'fill' : '#FFFFFF'})
        .style('font-weight', '300px')
        .style('font-size', '20px') 
        .text("today"); // "today" 

        // dollar month amount
        dollarMoAmt_label = d3.select('#power')
        .append('text')
        .attr({'x': 213, 'y': 380, 'text-anchor': 'middle', 'fill' : '#FFFFFF'})
        .style('font-weight', 'normal')
        .style('font-size', '40px') 
        .text("$21");
        
        // month text
        month_label = d3.select('#power')
        .append('text')
        .attr({'x': 300, 'y': 380, 'text-anchor': 'middle', 'fill' : '#FFFFFF'})
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
                "avgTriangle" : avg_triangle
    			}
    }
    
    function updateLabels(data) {
    	kwamt_raw = data[1]['value']
        kwamt_display = kwamt_raw
    	dollarDayAmt = data[2]['value']

    	kwtop_handle = this.d3objHandles["kwtop"];
    	kwamt_handle = this.d3objHandles["kwamt"];
    	dollarDayAmt_handle = this.d3objHandles["dollarDayAmt"]
        avgTriangle_handle = this.d3objHandles["avgTriangle"]
		
    	if (kwamt_raw >= 1000) {
    		kwtop_handle.text("kilowatts");
    		kwamt_display = (kwamt_raw/1000).toPrecision(3);
    	} else if (kwamt_raw >= 10000) {
    		kwtop_handle.text("kilowatts");
    		kwamt_display = (kwamt_raw/1000).toPrecision(4);
    	} else {
    		kwtop_handle.text("watts");
    	}

        // TODO: Use averages

        // Higher than average
        if (kwamt_raw > 1500) {
            avgTriangle_handle.attr({'points' : [252,110, 238,130, 266,130]});
            avgTriangle_handle.style('fill', '#FF8000')
            kwtop_handle.attr({'fill': '#FF8000'})
            powermeter.pie.color(['#222222', '#FF8000'])

        // Lower than average
        } else {
            avgTriangle_handle.attr({'points' : [252,130, 238,110, 266,110]});
            avgTriangle_handle.style('fill', '#6DD900')
            kwtop_handle.attr({'fill': '#6DD900'})
            powermeter.pie.color(['#222222', '#6DD900'])
        }
    	
    	kwamt_handle.text(kwamt_display);
        dollarDayAmt_handle.text('$' + dollarDayAmt);
        // dollarMoAmt_handle.text('$' + dollarMoAmt)
    }
}


/* init stuff */
overviewPie();



