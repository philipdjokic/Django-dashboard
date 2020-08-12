/* eslint-disable object-curly-newline */

/* global Chart */

/**
 * --------------------------------------------------------------------------
 * CoreUI Boostrap Admin Template (v3.2.0): main.js
 * Licensed under MIT (https://coreui.io/license)
 * --------------------------------------------------------------------------
 */

/* eslint-disable no-magic-numbers */
// random Numbers
var random = function random() {
  return Math.round(Math.random() * 100);
}; // eslint-disable-next-line no-unused-vars

// Aliasing the variable that is declared in the template.
var project = project_data;

aspects = {}

//Status:ok is in every aspect and should be removed
delete aspects['status']

var max = 0
var datasets = []

for ( i in project.data[3].aspect_f){
    
    datasets.push({
      label: project.data[3].aspect_f[i].label,
      backgroundColor: 'rgba(151, 187, 205, 0.5)',
      borderColor: 'rgba(151, 187, 205, 0.8)',
      highlightFill: 'rgba(151, 187, 205, 0.75)',
      highlightStroke: 'rgba(151, 187, 205, 1)',
      data: [ project.data[3].aspect_f[i].label__count]
    })
    if (project.data[3].aspect_f[i].label__count > max) {
      max = project.data[3].aspect_f[i].label__count
    }
}

var barChart = new Chart(document.getElementById('aspect_f'), {
  type: 'bar',
  data: {
    labels: ['Aspects'],
    datasets: datasets
  },
  options: {
    responsive: true,
    scales: {
      yAxes: [{
        display: true,
        ticks: {
          suggestedMin: 0,    // minimum will be 0, unless there is a lower value.
          suggestedMax: Math.floor(max * (120 / 100)) //tallest bar is always about 20% below the top of the chart
        }
      }]
    }
  }
}); // eslint-disable-next-line no-unused-vars

var pieChart = new Chart(document.getElementById('sentiment_f'), {
  type: 'pie',
  data: {
    labels: ['Positive', 'Negative', 'Neutral'],
    datasets: [{
      data: Object.values(project.data[1].sentiment_f[0]),
      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
      hoverBackgroundColor: ['#FF6384', '#36A2EB', '#FFCE56']
    }]
  },
  options: {
    responsive: true
  }
}); // eslint-disable-next-line no-unused-vars



var max_1 = 0
var datasets_1 = []


for ( i in project.data[4].aspect_s){
    
    datasets_1.push({
      label: project.data[4].aspect_s[i].label,
      backgroundColor: 'rgba(151, 187, 205, 0.5)',
      borderColor: 'rgba(151, 187, 205, 0.8)',
      highlightFill: 'rgba(151, 187, 205, 0.75)',
      highlightStroke: 'rgba(151, 187, 205, 1)',
      data: [project.data[4].aspect_s[i].positive, project.data[4].aspect_s[i].negative ,project.data[4].aspect_s[i].neutral]
    })
    
}
//

var aspect_s = new Chart(document.getElementById('aspect_s'), {
  type: 'bar',
  data: {
    labels: ['Aspects_sentiment',"1",'2'],
    datasets: datasets_1
  },
  options: {
    responsive: true,
    scales: {
      yAxes: [{
        display: true,
        ticks: {
          suggestedMin: 0,    // minimum will be 0, unless there is a lower value.
          suggestedMax: Math.floor(max_1 * (120 / 100)) //tallest bar is always about 20% below the top of the chart
        }
      }]
    }
  }
}); // eslint-disable-next-line no-unused-vars



var sentimentSourceChart = new Chart(document.getElementById('sentiment_source'), {
    type: 'bar',
    data: {
	labels: project_data.source_labels,
	datasets: project_data.source_datasets
    }
});

//# sourceMappingURL=charts.js.map
