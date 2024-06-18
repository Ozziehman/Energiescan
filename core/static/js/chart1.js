$(document).ready(function() {

    // chart1_current
    var options1_current = {
        chart: {
            type: 'area'
        },
        series: [{
            name: 'Power Generation',
            data: []
        }],
        xaxis: {
            categories: []
        },
        colors: ['#00FF00']
    }

    var chart1_current = new ApexCharts(document.querySelector("#chart1_current"), options1_current);
    chart1_current.render();

    // chart1_prediction
    var options1_prediction = {
        chart: {
            type: 'area'
        },
        series: [{
            name: 'Power Generation Prediction',
            data: []
        }],
        xaxis: {
            categories: []
        },
        colors: ['#FF0000']
    }

    var chart1_prediction = new ApexCharts(document.querySelector("#chart1_prediction"), options1_prediction);
    chart1_prediction.render();

    // initial data
    var usages1_current = [];
    var times1_current = [];

    setInterval(function() {
        $.ajax({
            url: getCSVDataUrl,
            type: "GET",
            success: function(data) {
                // get current time
                var data1_dateTime = data['Time'];
                var data1_usage = data['PV Productie (W)'];

                // add the new values to the arrays
                times1_current.push(data1_dateTime);
                usages1_current.push(data1_usage);
            
                // only keep the latest 100 values
                if (usages1_current.length > 100) {
                    usages1_current = usages1_current.slice(usages1_current.length - 100);
                    times1_current = times1_current.slice(times1_current.length - 100);
                }

                // update the chart
                chart1_current.updateSeries([{
                    name: 'Power Generation',
                    data: usages1_current
                }]);

                chart1_current.updateOptions({
                    xaxis: {
                        categories: times1_current,
                        min: Math.max(times1_current.length - 10, 0),
                    }
                });
            }
        });
    }, 300);

    // function to get prediction data
    function getPredictionData() {
        $.ajax({
            url: '/get_pv_prediction',
            type: 'GET',
            success: function(response) {
                var predictions = response['predictions'];

                var current_time = new Date();
                var times1_prediction = [];

                for (var i = 0; i < predictions.length; i++) {
                    current_time.setMinutes(current_time.getMinutes() + 15);
                    var time_string = current_time.getHours() + ":" + current_time.getMinutes();
                    times1_prediction.push(time_string);
                }

                // update the prediction chart
                chart1_prediction.updateSeries([{
                    name: 'Power Generation Prediction',
                    data: predictions
                }]);

                chart1_prediction.updateOptions({
                    xaxis: {
                        categories: times1_prediction,
                        min: 0
                    }
                });
            }
        });
    }

    // Call the prediction function initially and then every 5 minutes (300000 ms)
    getPredictionData();
    setInterval(getPredictionData, 300000);
});
