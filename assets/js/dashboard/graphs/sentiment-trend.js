import { metadataFiltersURL, normalFiltersURL} from "../helpers/filters";
import { update } from "../helpers/helpers";
let chart;
let def = 1;
let div = document.querySelector("#sentiment-trend-graph");
export function createGraph() {
    update.startUpdate();
    if (chart) {
        chart.destroy();
    }
    div.innerHTML = "Loading...";
    document.getElementById("sentiment-trend-total").innerHTML = 0;
    document.getElementById("sentiment-trend-total-positives").innerHTML = 0;
    document.getElementById("sentiment-trend-total-negatives").innerHTML = 0;
    var projectId = window.project_id;
    let urlParams = new URLSearchParams({
        default: def,
    })+ "&" +  metadataFiltersURL()+ "&" + normalFiltersURL();
    fetch(`/api/sentiment-trend/${projectId}/?` + urlParams)
        .then((response) => response.json())
        .then((data) => {
            def = 0;
            let chartOptions = {
                series: [],
                colors: ["#28C76F", "#EA5455"],
                chart: {
                    height: 320,
                    type: data.length === 1 ? "scatter":"line",
                    toolbar: {
                        show: false,
                    },
                },

                dataLabels: {
                    enabled: false,
                },
                stroke: {
                    curve: "smooth",
                    width: 3,
                },
                legend: {
                    show: false,
                },
                xaxis: {
                    categories: [],
                },
                tooltip: {
                    x: {
                        format: "MM/yyyy",
                    },
                },
            };
            let positives = [];
            let negatives = [];
            let categories = [];
            let totalPositives = 0;
            let totalNegatives = 0;
            if (Object.keys(data).length !== 0) {
                for (let element of data) {
                    totalPositives += element.positivesCount;
                    totalNegatives += element.negativesCount;
                    positives.push(totalPositives);
                    negatives.push(totalNegatives);
                    categories.push(element.date);
                }
                chartOptions.series.push(
                    { name: "Positives", data: positives },
                    { name: "Negatives", data: negatives }
                );

                chartOptions.xaxis.categories = categories;

                document.getElementById("sentiment-trend-total").innerHTML =
                    (totalPositives + totalNegatives).toLocaleString();
                document.getElementById(
                    "sentiment-trend-total-positives"
                ).innerHTML = totalPositives.toLocaleString();
                document.getElementById(
                    "sentiment-trend-total-negatives"
                ).innerHTML = totalNegatives.toLocaleString();
                div.innerHTML = "";
                chart = new ApexCharts(div, chartOptions);

                chart.render();
            } else {
                div.innerHTML = "";
            }
            update.finishUpdate();
        });
}
