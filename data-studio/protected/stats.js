let DailyPieChart = null
let TrendLineChart = null
let CountLineChart = null
let latest_date = null
let week_ago_date = null
let month_ago_date = null

function getAllDates(start_date, l_date){
    // get all date from 2023-05-12 to lastest date
    // end date is in the format of "YYYY-MM-DD" string
    // we have moment.js
    let startDate = moment(start_date);
    let endDate = moment(l_date);
    let dates = [];

    while (startDate.isSameOrBefore(endDate)) {
        dates.push(startDate.format("YYYY-MM-DD"));
        startDate.add(1, "day");
    }

    // reverse the dates array
    dates.reverse()

    return dates
}

function renderDateList(dates){
    $("#date-list").html('')
    for (let i = 0; i < dates.length; i++){
        $("#date-list").append('<button type="button" onclick="renderDailyRatingPie(\''+dates[i]+'\')" class="list-group-item list-group-item-action" id="date-list-item-'+dates[i]+'">'+dates[i]+'</button>')
    }
}

function renderDailyRatingPie(date){
    // the canvas element is #daily-rating-pie
    // the height of the canvas must be 300px

    // get the data
    // date should be in the format of "YYYY-MM-DD"
    let data = {
        "min_rating": 1,
        "max_rating": 5,
        "min_date": date,
        "max_date": date,
        "security_key": very_very_secure_key
    }

    $.ajax({
        url: "http://3.141.44.228:8001/get_conversation_with_filters",
        type: "POST",
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        data : JSON.stringify(data),
        success: function(result){
            console.log(result)
            let total_conv = result['results'].length
            let avg_rating = 0
            let confidenceInterval = 0
            let z = 1.96
            let std = 0
            let rating_count = [0, 0, 0, 0, 0]
            for (let i = 0; i < total_conv; i++){
                let rating = result['results'][i]['rating']
                avg_rating += rating
                rating_count[rating-1] += 1

                // calculate the std
                std += Math.pow(rating, 2)

                // calculate the confidence interval
                confidenceInterval += Math.pow(rating, 2)
            }
            avg_rating /= total_conv
            avg_rating = avg_rating.toFixed(2)



            // background color for the pie chart should be from green to red
            let backgrounds = [
                "#d3222c",
                "#ff681f",
                "#ff980e",
                "#079c56",
                "#016b3d"
            ]

            let chart_data = {
                labels: ['1 star', '2 stars', '3 stars', '4 stars', '5 stars'],
                datasets: [{
                    label: 'Total',
                    data: rating_count,
                    backgroundColor: backgrounds
                }]
            }

            let chart_options = {
                responsive: true,
                maintainAspectRatio: false,
                title: {
                    display: true,
                    text: 'Daily Rating Pie Chart'
                }
            }

            // destroy the old pie chart
            if (DailyPieChart != null){
                DailyPieChart.destroy()
            }

            // render the pie chart
            let ctx = document.getElementById('daily-rating-pie').getContext('2d');
            DailyPieChart = new Chart(ctx, {
                type: 'pie',
                data: chart_data,
                options: chart_options
            });

            // render the average rating
            $(".big-number").html(avg_rating)

            // render the total conversation
            $("#daily-total-conv").html("Count: "+total_conv)

            // render the confidence interval
            std = Math.sqrt(std/total_conv - Math.pow(avg_rating, 2))
            confidenceInterval = (z * std / Math.sqrt(total_conv)).toFixed(2)
            $("#daily-ci").html("CI: "+confidenceInterval)

            // add active class to the selected date
            $("#date-list button").removeClass("active")
            $("#date-list-item-"+date).addClass("active")

            
        },
        error: function(error){
            console.log(error)
        }
    })
}

async function renderTrendLineChart(option){
    // days will be an integer. It is the number of past days to be displayed in the chart
    
    let start_date = null
    if(option == 1){
        start_date = "2023-05-12"
    }else if(option == 2){
        start_date = "2023-06-13"
    }else{
        start_date = month_ago_date
    }

    $(".range-selector button").removeClass("btn-primary")
    $(".range-selector button").addClass("btn-outline-primary")

    $("#trend-option-"+option).removeClass("btn-outline-primary")
    $("#trend-option-"+option).addClass("btn-primary")

    console.log(start_date)

    let data = {
        "min_rating": 1,
        "max_rating": 5,
        "min_date": start_date,
        "max_date": latest_date,
        "security_key": very_very_secure_key
    }

    $.ajax({
        url: "http://3.141.44.228:8001/get_conversation_with_filters",
        type: "POST",
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        data : JSON.stringify(data),
        success: function(result){
            console.log(result)

            // get all the dates
            let dates = getAllDates(start_date, latest_date)

            // reverse the dates array
            dates.reverse()

            console.log(dates)

            // get daily rating average
            // use a dictionary to store the rating list for each date
            let daily_rating_avg = {}
            let daily_rating_avg_list = []
            let last_7_days_rating_avg = []
            let daily_rating_count = []
            for (let i = 0; i < dates.length; i++){
                daily_rating_avg[dates[i]] = []
            }

            // get the total rating for each date
            for (let i = 0; i < result['results'].length; i++){
                let date = result['results'][i]['start_at'].split("T")[0]
                let rating = result['results'][i]['rating']
                daily_rating_avg[date].push(rating)
            }

            // calculate the average rating for each date
            for (let i = 0; i < dates.length; i++){
                
                // if there is no rating for that date, remove that date from the list
                if (daily_rating_avg[dates[i]].length == 0){
                    dates.splice(i, 1)
                    i -= 1
                    continue
                }
                let sum = 0
                for (let j = 0; j < daily_rating_avg[dates[i]].length; j++){
                    sum += daily_rating_avg[dates[i]][j]
                }

                daily_rating_avg_list.push((sum / daily_rating_avg[dates[i]].length).toFixed(2))

                // get the total rating count for each date
                daily_rating_count.push(daily_rating_avg[dates[i]].length)
                console.log(daily_rating_avg[dates[i]].length)
            }

            // console.log(daily_rating_count)

            // calculate the running average for past 7 days at each date, if there is no 7 days, then use the available days. For example, day one's running average is the average of day one, day two's running average is the average of day one and day two, day three's running average is the average of day one, day two and day three, and so on.
            for (let i = 0; i < daily_rating_avg_list.length; i++){
                let sum = 0
                let count = 0
                for (let j = i; j >= 0; j--){
                    sum += parseFloat(daily_rating_avg_list[j])
                    count += 1
                    if (count == 7){
                        break
                    }
                }
                last_7_days_rating_avg.push((sum / count).toFixed(2))
            }

            // get the data for the chart, the x-axis is the date, the y-axis is the daily average rating and the running average rating
            let chart_data = {
                labels: dates,
                datasets: [{
                    label: 'Daily Average Rating',
                    data: daily_rating_avg_list,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)'
                },
                {
                    label: 'Last 7 Days Average Rating',
                    data: last_7_days_rating_avg,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)'
                }]
            }

            // get the options for the chart. The y-axis is the daily average rating. The x-axis is the date in the format of "YYYY-MM-DD"
            let chart_options = {
                responsive: true,
                maintainAspectRatio: false
            }

            // destroy the old line chart
            if (TrendLineChart != null){
                TrendLineChart.destroy()
            }

            //render the line chart
            let ctx = document.getElementById('trend-canvas').getContext('2d');
            TrendLineChart = new Chart(ctx, {
                type: 'line',
                data: chart_data,
                options: chart_options
            });

            // get the data for the chart, the x-axis is the date, the y-axis is the daily rating count
            let chart_data_2 = {
                labels: dates,
                datasets: [{
                    label: 'Daily Rating Count',
                    data: daily_rating_count,
                    backgroundColor: 'rgba(255,181,34, 0.2)',
                    borderColor: '#ffb522'
                }]
            }

            // get the options for the chart. The y-axis is the daily rating count
            let chart_options_2 = {
                title: {
                    display: true,
                    text: 'Daily Rating Count'
                },
                responsive: true,
                maintainAspectRatio: false
            }

            // destroy the old line chart
            if (CountLineChart != null){
                CountLineChart.destroy()
            }

            //render the line chart
            let ctx_2 = document.getElementById('count-canvas').getContext('2d');
            CountLineChart = new Chart(ctx_2, {
                type: 'line',
                data: chart_data_2,
                options: chart_options_2
            });
        },
        error: function(error){
            console.log(error)
        }
    })
}

// get latest date from database
async function getLatestDate(){
    let url = "http://3.141.44.228:8001/get_latest_conversation"
    let data = {
        "security_key": very_very_secure_key
    }

    let res = await $.ajax({
        url: url,
        type: "POST",
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        data : JSON.stringify(data)
    })

    let l_date = res['results']['start_at'].split("T")[0]
    return l_date
}

(async function(){
    // get all conversation
    // getAllConv()

    // get latest date from database
    latest_date = await getLatestDate()

    // get week ago date
    week_ago_date = moment(latest_date).subtract(6, 'days').format("YYYY-MM-DD")

    // get month ago date
    month_ago_date = moment(latest_date).subtract(29, 'days').format("YYYY-MM-DD")

    // render daily rating pie chart
    renderDateList(getAllDates("2023-05-12", latest_date))
    renderDailyRatingPie(latest_date)    
    renderTrendLineChart(1)
})();



