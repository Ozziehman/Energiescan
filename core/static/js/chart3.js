$(document).ready(function() {

    // chart3_current
    var options3_current = {
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
        colors: ['#00FF00'],
        dataLabels: {
            enabled: false
        }
    }

    var chart3_current = new ApexCharts(document.querySelector("#chart3_current"), options3_current);
    chart3_current.render();

    // initial data
    var usages3_current = [];
    var times3_current = [];

    setInterval(function() {
        $.ajax({
            url: newUsageUrl,
            type: "GET",
            success: function(newUsage) {
                // get current time
                var date3_current = new Date();
                var time3_current = date3_current.getHours() + ":" + date3_current.getMinutes() + ":" + date3_current.getSeconds();

                // Add the new values to the arrays
                usages3_current.push(newUsage);
                times3_current.push(time3_current);

                // only keep the latest 10 values
                if (usages3_current.length > 100) {
                    usages3_current = usages3_current.slice(usages3_current.length - 100);
                    times3_current = times3_current.slice(times3_current.length - 100);
                }

                // update the chart
                chart3_current.updateSeries([{
                    name: 'Power Usage',
                    data: usages3_current
                }]);

                chart3_current.updateOptions({
                    xaxis: {
                        categories: times3_current,
                        min: Math.max(times3_current.length - 10, 0),
                    }
                });
            }
        });
    }, 1000);

    // chart3_prediction
    var options3_prediction = {
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
        colors: ['#FF0000'],
        dataLabels: {
            enabled: false
        }
    }

    var chart3_prediction = new ApexCharts(document.querySelector("#chart3_prediction"), options3_prediction);
    chart3_prediction.render();

    // initial data
    var usages3_prediction = [];
    var times3_prediction = [];

    setInterval(function() {
        $.ajax({
            url: futureUsageUrl,
            type: "GET",
            success: function(newUsage) {
                // get current time and add 10 seconds
                var date3_prediction = new Date();
                date3_prediction.setSeconds(date3_prediction.getSeconds() + 10);
                var time3_prediction = date3_prediction.getHours() + ":" + date3_prediction.getMinutes() + ":" + date3_prediction.getSeconds();

                // add the new values to the arrays
                usages3_prediction.push(newUsage);
                times3_prediction.push(time3_prediction);

                // only keep the latest 10 values
                if (usages3_prediction.length > 100) {
                    usages3_prediction = usages3_prediction.slice(usages3_prediction.length - 100);
                    times3_prediction = times3_prediction.slice(times3_prediction.length - 100);
                }

                // update the chart
                chart3_prediction.updateSeries([{
                    name: 'Power Usage',
                    data: usages3_prediction
                }]);

                chart3_prediction.updateOptions({
                    xaxis: {
                        categories: times3_prediction,
                        min: Math.max(times3_prediction.length - 10, 0),
                    }
                });
            }
        });
    }, 1000);
});