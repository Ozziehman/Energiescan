$(document).ready(function() {

    // chart2_current
    var options2_current = {
        chart: {
            type: 'area'
        },
        series: [{
            name: 'Power Usage',
            data: []
        }],
        xaxis: {
            categories: []
        },
        colors: ['#00FF00']
    }

    var chart2_prediction_current = new ApexCharts(document.querySelector("#chart2_current"), options2_current);
    chart2_prediction_current.render();

    // initial data
    var usages2_current = [];
    var times2_current = [];

    setInterval(function() {
        $.ajax({
            url: newUsageUrl,
            type: "GET",
            success: function(newUsage) {
                // get current time
                var date2_current = new Date();
                var time2_current = date2_current.getHours() + ":" + date2_current.getMinutes() + ":" + date2_current.getSeconds();

                // Add the new values to the arrays
                usages2_current.push(newUsage);
                times2_current.push(time2_current);

                // Only keep the latest 10 values
                if (usages2_current.length > 10) {
                    usages2_current = usages2_current.slice(usages2_current.length - 10);
                    times2_current = times2_current.slice(times2_current.length - 10);
                }

                // Update the chart
                chart2_prediction_current.updateSeries([{
                    name: 'Power Usage',
                    data: usages2_current
                }]);

                chart2_prediction_current.updateOptions({
                    xaxis: {
                        categories: times2_current
                    }
                });
            }
        });
    }, 1000);

    // chart2_prediction
    var options2_prediction = {
        chart: {
            type: 'area'
        },
        series: [{
            name: 'Power Usage',
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
    var usages2_prediction = [];
    var times2_prediction = [];

    setInterval(function() {
        $.ajax({
            url: futureUsageUrl,
            type: "GET",
            success: function(newUsage) {
                // get current time and add 10 seconds
                var date2_prediction = new Date();
                date2_prediction.setSeconds(date2_prediction.getSeconds() + 10);
                var time2_prediction = date2_prediction.getHours() + ":" + date2_prediction.getMinutes() + ":" + date2_prediction.getSeconds();

                // Add the new values to the arrays
                usages2_prediction.push(newUsage);
                times2_prediction.push(time2_prediction);

                // Only keep the latest 10 values
                if (usages2_prediction.length > 10) {
                    usages2_prediction = usages2_prediction.slice(usages2_prediction.length - 10);
                    times2_prediction = times2_prediction.slice(times2_prediction.length - 10);
                }

                // Update the chart
                chart2_prediction.updateSeries([{
                    name: 'Power Usage',
                    data: usages2_prediction
                }]);

                chart2_prediction.updateOptions({
                    xaxis: {
                        categories: times2_prediction
                    }
                });
            }
        });
    }, 1000);
});