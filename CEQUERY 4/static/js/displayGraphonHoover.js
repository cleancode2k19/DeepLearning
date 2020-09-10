
function displayGraphonHoover(dataobj) {
  var index = []
  for(var i = 1 ;i < dataobj.length;i++){
    index.push(i);
  }
  try {
    //bar chart
    $('#hooverbarChart').remove(); // this is my <canvas> element
    $('#removeGraph').show();
    $('#graph-hoover-container').append('<canvas id="hooverbarChart"><canvas>');
    var ctx = document.getElementById("hooverbarChart");
    if (ctx) {
      var myChart = new Chart(ctx, {
        type: 'line',
        defaultFontFamily: 'Poppins',
        data: {
          labels: index,
          datasets: [
            {
              label: "Score",
              data: dataobj,
              borderColor: "rgba(0, 123, 255, 0.9)",
              borderWidth: "0",
              backgroundColor:"#000075",
              fontFamily: "Poppins",
              fill:false
            },
          ]
        },
        options: {
          legend: {
              position: 'top',
              labels: {
                  fontFamily: 'Poppins'
              }
          },
          scales: {
            yAxes: [{
                stacked: false,
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

}
