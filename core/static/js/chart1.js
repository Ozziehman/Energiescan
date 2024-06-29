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
        colors: ['#00FF00'],
        dataLabels: {
            enabled: false
        }
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
        colors: ['#FF0000'],
        dataLabels: {
            enabled: false
        }
    }

    var chart1_prediction = new ApexCharts(document.querySelector("#chart1_prediction"), options1_prediction);
    chart1_prediction.render();

    // initial data
    var usages1_current = [];
    var times1_current = [];

    setInterval(function() {
        $.ajax({
            url: '/get_csv_data_pv',
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
                        min: 0,
                    }
                });
            }
        });
    }, 1000);

    // Function to get prediction data
    function getPredictionData(modelType) {
        $.ajax({
            url: '/get_pv_prediction',
            type: 'GET',
            data: { model: modelType },
            success: function(response) {
                var predictions = response['predictions'];
    
                // Get the last real data time
                var last_real_time_str = times1_current[times1_current.length - 1];
    
                // Parse the last real time string into a Date object
                var last_real_time = new Date(last_real_time_str.replace(' ', 'T') + 'Z'); // Adding 'Z' to indicate UTC time
    
                var times1_prediction = [];
    
                // Start the prediction times 15 minutes after the last real time
                for (var i = 0; i < predictions.length; i++) {
                    last_real_time.setMinutes(last_real_time.getMinutes() + 15);
                    var year = last_real_time.getUTCFullYear();
                    var month = (last_real_time.getUTCMonth() + 1).toString().padStart(2, '0');
                    var day = last_real_time.getUTCDate().toString().padStart(2, '0');
                    var hours = last_real_time.getUTCHours().toString().padStart(2, '0');
                    var minutes = last_real_time.getUTCMinutes().toString().padStart(2, '0');
                    var seconds = last_real_time.getUTCSeconds().toString().padStart(2, '0');
                    var time_string = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
                    times1_prediction.push(time_string);
                }
    
                // Update the prediction chart
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

    var selectedModel = 'lstm'; // Default to lstm

    // Initial call to fetch prediction data with default model type
    getPredictionData(selectedModel);

    // Update prediction data when the user selects a different model
    $('#modelSelect').change(function() {
        selectedModel = $(this).val();
        getPredictionData(selectedModel);
    });

    // Update prediction data every 5 minutes
    setInterval(function() {
        getPredictionData(selectedModel);
    }, 1000);
});
