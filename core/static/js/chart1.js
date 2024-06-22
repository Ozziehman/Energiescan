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
                        min: Math.max(times1_current.length - 10, 0),
                    }
                });
            }
        });
    }, 300);

    // Function to get prediction data
    function getPredictionData(modelType) {
        $.ajax({
            url: '/get_pv_prediction',
            type: 'GET',
            data: { model: modelType },
            success: function(response) {
                var predictions = response['predictions'];

                var current_time = new Date();
                var times1_prediction = [];

                for (var i = 0; i < predictions.length; i++) {
                    current_time.setMinutes(current_time.getMinutes() + 15);
                    var hours = current_time.getHours().toString().padStart(2, '0');
                    var minutes = current_time.getMinutes().toString().padStart(2, '0');
                    var time_string = hours + ":" + minutes;
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
    }, 300000);
});
