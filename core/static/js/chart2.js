$(document).ready(function() {
    // chart2_current
    var options2_current = {
        chart: {
            type: 'area'
        },
        series: [{
            name: 'Active Power Usage',
            data: []
        }, {
            name: 'Reactive Power Usage',
            data: []
        }],
        xaxis: {
            categories: []
        },
        colors: ['#0000FF', '#FF0000']
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
        colors: ['#FF0000']
    }

    var chart2_prediction = new ApexCharts(document.querySelector("#chart2_prediction"), options2_prediction);
    chart2_prediction.render();

    // initial data
    var global_active_power2_current = [];
    var global_reactive_power2_current = [];
    var times2_current = [];

    setInterval(function() {
        $.ajax({
            url: '/get_csv_data_household_power_consumption',
            type: "GET",
            success: function(data) {
                // get current time
                var data2_dateTime = data['DateTime'];
                var data2_globalActivePower = data['Global_active_power'];
                var data2_globalReactivePower = data['Global_reactive_power']; //This is just for demonstration of the graph!!!!!!!!!!!!!!!!!!

                // add the new values to the arrays
                global_active_power2_current.push(data2_globalActivePower);
                times2_current.push(data2_dateTime);
                global_reactive_power2_current.push(data2_globalReactivePower);

                // only keep the latest 100 values
                if (global_active_power2_current.length > 100) {
                    global_active_power2_current = global_active_power2_current.slice(global_active_power2_current.length - 100);
                    times2_current = times2_current.slice(times2_current.length - 100);
                    global_reactive_power2_current = global_reactive_power2_current.slice(global_reactive_power2_current.length - 100);
                }

                // update the chart
                chart2_current.updateSeries([{
                    name: 'Active Power Usage',
                    data: global_active_power2_current
                }, {
                    name: 'Reactive Power Usage',
                    data: global_reactive_power2_current
                }]);

                chart2_current.updateOptions({
                    xaxis: {
                        categories: times2_current,
                        min: Math.max(times2_current.length - 10, 0),
                    }
                });
            }
        });
    }, 300);

    // Function to get prediction data
    function getPredictionData(modelType) {
        $.ajax({
            url: '/get_household_power_consumption_prediction',
            type: 'GET',
            data: { model: modelType },
            success: function(response) {
                var predictions = response['predictions'];

                var current_time = new Date();
                var times2_prediction = [];

                for (var i = 0; i < predictions.length; i++) {
                    current_time.setMinutes(current_time.getMinutes() + 15);
                    var hours = current_time.getHours().toString().padStart(2, '0');
                    var minutes = current_time.getMinutes().toString().padStart(2, '0');
                    var time_string = hours + ":" + minutes;
                    times2_prediction.push(time_string);
                }

                // Update the prediction chart
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

    // Initial call to fetch prediction data with default model type
    getPredictionData(selectedModel);

    // Update prediction data when the user selects a different model
    $('#modelSelect2').change(function() {
        selectedModel = $(this).val();
        getPredictionData(selectedModel);
    });

    // Update prediction data every 5 minutes
    setInterval(function() {
        getPredictionData(selectedModel);
    }, 300000);
});
