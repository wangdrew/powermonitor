
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
                xmlHttp.open( "GET", "http://" + influxdb_host + ":" + influxdb_port + "/db/power_now/series?u=root&p=root&q=select%20*%20from%20power%20limit%201", false );
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
        .attr({'x': 252, 'y': 170, 'text-anchor': 'middle', 'fill' : '#FFFFFF'})
        .style('font-size', '36px')
    	.text("watts");
        
        // kW amount
        kwamt_label = d3.select('#power')
        .append('text')
    	.attr({'x': 257, 'y': 280, 'text-anchor': 'middle', 'fill' : '#FFFFFF'})
    	.style('font-size', '102px') 
    	.style('font-weight', 'normal')
    	.text("0");
        
        // dollar amount
        dollaramt_label = d3.select('#power')
        .append('text')
    	.attr({'x': 250, 'y': 360, 'text-anchor': 'middle', 'fill' : '#FF8000'})
    	.style('font-weight', 'normal')
    	.style('font-size', '42px') 
    	.text("$");
        
        // today text
        today_label = d3.select('#power')
        .append('text')
        .attr({'x': 250, 'y': 390, 'text-anchor': 'middle', 'fill' : '#FF8000'})
        .style('font-weight', 'normal')
        .style('font-size', '24px') 
        .text("today");
      	
    	this.d3objHandles = {
    			"kwtop" : kwtop_label,
    			"kwamt" : kwamt_label,
    			"dollaramt" : dollaramt_label,
    			}
    }
    
    function updateLabels(data) {
    	kwamt = data[1]['value']
    	dollaramt = data[2]['value']

    	kwtop_handle = this.d3objHandles["kwtop"];
    	kwamt_handle = this.d3objHandles["kwamt"];
    	dollaramt_handle = this.d3objHandles["dollaramt"]
		
    	if (kwamt >= 1000) {
    		kwtop_handle.text("kilowatts");
    		kwamt = (kwamt/1000).toPrecision(3);
    	} else if (kwamt >= 10000) {
    		kwtop_handle.text("kilowatts");
    		kwamt = (kwamt/1000).toPrecision(4);
    	} else {
    		kwtop_handle.text("watts");
    	}
    	
    	kwamt_handle.text(kwamt);
        dollaramt_handle.text('$' + dollaramt);
    }
}


/* init stuff */
overviewPie();



