
function displayGraphs(dataobj, alldata) {
   

    document.getElementById("chart-title").innerHTML = dataobj['chartTitle'];
    var check = this;
  try {
    //bar chart
    $('#removeGraph').hide();

        $('#barChart').remove(); // this is my <canvas> element
        $('#graph-container').append('<canvas id="barChart"><canvas>');
        var ctx = document.getElementById("barChart");
        if (ctx) {
          var myChart = new Chart(ctx, {
            type: 'bar',
            defaultFontFamily: 'Poppins',
            data: {
              labels: dataobj['labels'],
              datasets: [
                {
                  label: "Positive",
                  data: dataobj['positive'],
                  borderColor: "rgba(0, 123, 255, 0.9)",
                  borderWidth: "0",
                  backgroundColor:"#000075",
                  fontFamily: "Poppins"
                },
                {
                  label: "Negative",
                  data: dataobj['negative'],
                  borderColor: "rgba(0,0,0,0.09)",
                  borderWidth: "0",
                  backgroundColor: "#7366BD",
                  fontFamily: "Poppins"
                }
              ]
            },
            responsive: true,
            options: {
              legend: {
                position: 'top',
                labels: {
                    fontFamily: 'Poppins'
                }
              },
              tooltips: {
                callbacks: {
                  label: (tooltipItem, data, alldata) => {
                    if(dataobj['chartTitle'] == "Overall Results across all Domains"){
                      displayGraphonHoover(dataobj['score'][tooltipItem['index']]);
                    } 
                    return tooltipItem['yLabel'];
                    
                  },
                },
                custom: function(tooltipModel) {
                  if (tooltipModel.opacity === 0) {
                    $('#removeGraph').hide();
                  }
                }
              },
              scales: {
                xAxes: [{
                  ticks: {
                    fontFamily: "Poppins",
                    "autoSkip": false
                  }
                }],
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'Number of Comments'
                    },
                    ticks: {
                        beginAtZero: true,
                        fontFamily: "Poppins"
                    }
                }]
              }
            }
          });
        }


        }
        catch (error) {
        console.log(error);
        }


  try {

    //doughnut chart
      $('#doughnutChart').remove(); // this is my <canvas> element
      $('#doughnut-container').append('<canvas id="doughnutChart"><canvas>');
    var ctx = document.getElementById("doughnutChart");
    if (ctx) {
      var myChart = new Chart(ctx, {
        type: 'doughnut',
      data: {
          datasets: [{
            data: dataobj['both'],
            backgroundColor: [
              "#A2A2D0",
              "#ACE5EE",
              "#126180",
              "#000075",
              "#7366BD"
            ],

          }],
          labels: dataobj['labels']
        },
        options: {
          legend: {
            position: 'top',
            labels: {
              fontFamily: 'Poppins'
            }

          },
          responsive: true
        }
      });
    }


  } catch (error) {
    console.log(error);
  }

}
