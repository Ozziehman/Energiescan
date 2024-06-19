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
                data2_dateTime = data['DateTime'];
                data2_globalActivePower = data['Global_active_power'];
                data2_globalReactivePower = data['Global_reactive_power'];
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

//     // chart2_prediction
//     var options2_prediction = {
//         chart: {
//             type: 'area'
//         },
//         series: [{
//             name: 'Power Usage',
//             data: []
//         }],
//         xaxis: {
//             categories: []
//         },
//         colors: ['#FF0000']
//     }

//     var chart2_prediction = new ApexCharts(document.querySelector("#chart2_prediction"), options2_prediction);
//     chart2_prediction.render();

//     // initial data
//     var usages2_prediction = [];
//     var times2_prediction = [];

//     setInterval(function() {
//         $.ajax({
//             url: futureUsageUrl,
//             type: "GET",
//             success: function(newUsage) {
//                 // get current time and add 10 seconds
//                 var date2_prediction = new Date();
//                 date2_prediction.setSeconds(date2_prediction.getSeconds() + 10);
//                 var time2_prediction = date2_prediction.getHours() + ":" + date2_prediction.getMinutes() + ":" + date2_prediction.getSeconds();

//                 // add the new values to the arrays
//                 usages2_prediction.push(newUsage);
//                 times2_prediction.push(time2_prediction);

//                 // only keep the latest 10 values
//                 if (usages2_prediction.length > 100) {
//                     usages2_prediction = usages2_prediction.slice(usages2_prediction.length - 100);
//                     times2_prediction = times2_prediction.slice(times2_prediction.length - 100);
//                 }

//                 // update the chart
//                 chart2_prediction.updateSeries([{
//                     name: 'Power Usage',
//                     data: usages2_prediction
//                 }]);

//                 chart2_prediction.updateOptions({
//                     xaxis: {
//                         categories: times2_prediction,
//                         min: Math.max(times2_prediction.length - 10, 0),
//                     }
//                 });
//             }
//         });
//     }, 1000);
});