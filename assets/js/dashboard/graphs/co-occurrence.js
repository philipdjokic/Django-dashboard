import {update} from '../helpers/helpers'
import { metadataFiltersURL, normalFiltersURL} from "../helpers/filters";
let div = document.querySelector("#co-occurrence-graph")
export function createGraph(){
    update.startUpdate()
    div.innerHTML = "Loading..."
    var chartOptions = {
        series: [],
        chart: {
            height: 480,
            type: "heatmap",
        },
        plotOptions: {
            heatmap: {
                shadeIntensity: 0.5,
                radius: 0,
    
                colorScale: {
                    ranges: [
                        {
                            from: -10,
                            to: 20,
                            name: "0-20 %",
                            color: "#E2E0FB",
                        },
                        {
                            from: 20,
                            to: 40,
                            name: "20-40 %",
                            color: "#D4D0FA",
                        },
                        {
                            from: 40,
                            to: 60,
                            name: "40-60 %",
                            color: "#C6C1F8",
                        },
                        {
                            from: 60,
                            to: 80,
                            name: "60-80 %",
                            color: "#968DF3",
                        },
                        {
                            from: 80,
                            to: 100,
                            name: "80-100 %",
                            color: "#8075F1",
                        }
                    ],
                },
            },
        },
        tooltip: {
            y: {
                formatter: function (val) {
                    return val+'%';
                },
            },
        },
        dataLabels: {
            enabled: false,
            style: {
                fontSize: "14px",
                fontFamily: "Helvetica, Arial, sans-serif",
                fontWeight: "bold",
            },
        },
        legend: {
            position: "bottom",
    
            markers: {
                width: 30,
            },
        },
    
        stroke: {
            width: 1,
        },
        xaxis: {
            type: "category",
            categories: [],
        },
    };
    let project_id = window.project_id;
    fetch(`/api/co-occurence/${project_id}/?` + "&" +  metadataFiltersURL()+ "&" + normalFiltersURL())
        .then((response) => response.json())
        .then((data) => {
            chartOptions.series = data
            div.innerHTML = ""
            if(Object.keys(data).length !== 0){
                chartOptions.chart.height = 50 * data.length
                if(chartOptions.chart.height < 300){
                    chartOptions.chart.height = 300
                }
                let chart = new ApexCharts(
                    div,
                    chartOptions
                );
                chart.render();
            }
            update.finishUpdate()
        });     
}
