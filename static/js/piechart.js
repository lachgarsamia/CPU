  function generateRandomBrightColor(i) {
            const brightColors = [
                'red', 'blue', 'green', 'orange', 'yellow', 'cyan', 'magenta',
                'lime', 'pink', 'turquoise', 'gold', 'purple', 'violet', 'skyblue', 'coral',
                'teal', 'lavender', 'maroon', 'olive', 'navy', 'peach', 'indigo',
                'tomato', 'orchid', 'slateblue', 'seagreen', 'peru', 'crimson', 'darkorange', 'salmon'
            ];

            i = i % 30;

            return brightColors[i];
        }
    let sum_burst = 0;
const csvUrl2 = 'static/csv/process_table.csv';
fetchCSV(csvUrl2)
  .then(data => {
let dt = [];
for (var i = 1;i<data.length;i++){
    sum_burst += parseInt(data[i][1]);
    dt.push(data[i][1]);
}

    var cpu_idle =  Math.abs(sum_burst - parseInt('{{ total }}'));
    var perc = 100 * sum_burst / (sum_burst + cpu_idle);
    document.getElementById("cpuUtil").innerHTML += perc + "%";
      var lbls = dt.map((value, index) => `Process ${index + 1}`);


        // Generate colors for each data point
        const colors = dt.map((value, index) => generateRandomBrightColor(index +1));

        colors.push("black")
        lbls.push("CPU IDLE")
        dt.push(cpu_idle)

        // Get canvas element
        const ctx = document.getElementById('myPieChart').getContext('2d');

        // Create pie chart
        const myPieChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: lbls, // Labels for each data point
                datasets: [{
                    data: dt,
                    backgroundColor: colors
                }]
            },
            options: {
                responsive: false
            }
        });

  });








