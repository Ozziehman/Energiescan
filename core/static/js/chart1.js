$(document).ready(function() {

    // chart1_current
    var options1_current = {
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

    var chart1_current = new ApexCharts(document.querySelector("#chart1_current"), options1_current);
    chart1_current.render();

    // initial data
    var usages1_current = [];
    var times1_current = [];

    setInterval(function() {
        $.ajax({
            url: newUsageUrl,
            type: "GET",
            success: function(newUsage) {
                // get current time
                var date1_current = new Date();
                var time1_current = date1_current.getHours() + ":" + date1_current.getMinutes() + ":" + date1_current.getSeconds();

                // Add the new values to the arrays
                usages1_current.push(newUsage);
                times1_current.push(time1_current);

                // Only keep the latest 10 values
                if (usages1_current.length > 100) {
                    usages1_current = usages1_current.slice(usages1_current.length - 100);
                    times1_current = times1_current.slice(times1_current.length - 100);
                }

                // Update the chart
                chart1_current.updateSeries([{
                    name: 'Power Usage',
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
    }, 1000);

    // chart1_prediction
    var options1_prediction = {
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

    var chart1_prediction = new ApexCharts(document.querySelector("#chart1_prediction"), options1_prediction);
    chart1_prediction.render();

    // initial data
    var usages1_prediction = [];
    var times1_prediction = [];

    setInterval(function() {
        $.ajax({
            url: futureUsageUrl,
            type: "GET",
            success: function(newUsage) {
                // get current time and add 10 seconds
                var date1_prediction = new Date();
                date1_prediction.setSeconds(date1_prediction.getSeconds() + 10);
                var time1_prediction = date1_prediction.getHours() + ":" + date1_prediction.getMinutes() + ":" + date1_prediction.getSeconds();

                // Add the new values to the arrays
                usages1_prediction.push(newUsage);
                times1_prediction.push(time1_prediction);

                // Only keep the latest 10 values
                if (usages1_prediction.length > 100) {
                    usages1_prediction = usages1_prediction.slice(usages1_prediction.length - 100);
                    times1_prediction = times1_prediction.slice(times1_prediction.length - 100);
                }

                // Update the chart
                chart1_prediction.updateSeries([{
                    name: 'Power Usage',
                    data: usages1_prediction
                }]);

                chart1_prediction.updateOptions({
                    xaxis: {
                        categories: times1_prediction,
                        min: Math.max(times1_prediction.length - 10, 0),
                    }
                });
            }
        });
    }, 1000);
});