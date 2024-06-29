$(document).ready(function() {
    // chart2_current
    var options2_current = {
        chart: {
            type: 'area'
        },
        series: [{
            name: 'Active Power Usage',
            data: []
        }],
        xaxis: {
            categories: []
        },
        colors: ['#0000FF'],
        dataLabels: {
            enabled: false
        }
    }

    var chart2_current = new ApexCharts(document.querySelector("#chart2_current"), options2_current);
    chart2_current.render();

    // chart2_prediction
    var options2_prediction = {
        chart: {
            type: 'area'
        },
        series: [{
            name: 'Power Usage Prediction',
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

    var chart2_prediction = new ApexCharts(document.querySelector("#chart2_prediction"), options2_prediction);
    chart2_prediction.render();

    // initial data
    var global_active_power2_current = [];
    var times2_current = [];

    setInterval(function() {
        $.ajax({
            url: '/get_csv_data_household_power_consumption',
            type: "GET",
            success: function(data) {
                // get current time
                var data2_dateTime = data['DateTime'];
                var data2_globalActivePower = data['Global_active_power'];

                // add the new values to the arrays
                global_active_power2_current.push(data2_globalActivePower);
                times2_current.push(data2_dateTime);

                // only keep the latest 50 values
                if (global_active_power2_current.length > 50) {
                    global_active_power2_current = global_active_power2_current.slice(global_active_power2_current.length - 50);
                    times2_current = times2_current.slice(times2_current.length - 50);
                }

                // update the chart
                chart2_current.updateSeries([{
                    name: 'Active Power Usage',
                    data: global_active_power2_current
                }]);

                chart2_current.updateOptions({
                    xaxis: {
                        categories: times2_current,
                        min: 0,
                    }
                });
            }
        });
    }, 1000);

    function getPredictionData(modelType) {
        $.ajax({
            url: '/get_household_power_consumption_prediction',
            type: 'GET',
            data: { model: modelType },
            success: function(response) {
                var predictions = response['predictions'];

                // get the last real data time
                var last_real_time_str2 = times2_current[times2_current.length - 1];
    
                // parse the last real time string into a Date object
                var last_real_time2 = new Date(last_real_time_str2.replace(' ', 'T') + 'Z'); // Z for UTC time
    
                var times2_prediction = [];
    
                // start the prediction times 15 minutes after the last real time
                for (var i = 0; i < predictions.length; i++) {
                    last_real_time2.setMinutes(last_real_time2.getMinutes() + 15);
                    var year = last_real_time2.getUTCFullYear();
                    var month = (last_real_time2.getUTCMonth() + 1).toString().padStart(2, '0');
                    var day = last_real_time2.getUTCDate().toString().padStart(2, '0');
                    var hours = last_real_time2.getUTCHours().toString().padStart(2, '0');
                    var minutes = last_real_time2.getUTCMinutes().toString().padStart(2, '0');
                    var seconds = last_real_time2.getUTCSeconds().toString().padStart(2, '0');
                    var time_string = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
                    times2_prediction.push(time_string);
                }

                // update the prediction chart
                chart2_prediction.updateSeries([{
                    name: 'Power Usage Prediction',
                    data: predictions
                }]);

                chart2_prediction.updateOptions({
                    xaxis: {
                        categories: times2_prediction,
                        min: 0
                    }
                });
            }
        });
    }

    var selectedModel = 'lstm'; // Default to lstm

    // initial call to fetch prediction data with default model type
    getPredictionData(selectedModel);

    // update prediction data when the user selects a different model
    $('#modelSelect2').change(function() {
        selectedModel = $(this).val();
        getPredictionData(selectedModel);
    });

    // uspdate prediction data every 5 minutes
    setInterval(function() {
        getPredictionData(selectedModel);
    }, 1000);
});
