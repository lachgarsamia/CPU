   function calculateFrequency(values, numBins) {
            const min = Math.min(...values);
            const max = Math.max(...values);
            const binSize = (max - min) / numBins;
            const frequencies = Array(numBins).fill(0);

            values.forEach(value => {
                const binIndex = Math.floor((value - min) / binSize);
                frequencies[binIndex]++;
            });

            return frequencies;
        }

        // Create the bar plot
      function createBarPlot(values, numBins, chartID, color,lbl,titl) {
    const frequencies = calculateFrequency(values, numBins);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const binSize = (max - min) / numBins;
    const bins = Array.from({ length: numBins }, (_, i) => {
        const binStart = min + i * binSize;
        const binEnd = binStart + binSize;
        return `${binStart.toFixed(2)} - ${binEnd.toFixed(2)}`;
    });

    const ctx = document.getElementById(chartID).getContext('2d');
    const myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: bins,
            datasets: [{
                label: 'Frequency',
                data: frequencies,
                backgroundColor: color,
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: titl
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: lbl
                    }
                }
            }
        }
    });
}
        // Call the function with your values and desired number of bins
function fetchCSV(url) {
  return fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.text();
    })
    .then(csvData => {
      // Split CSV into lines
      const rows = csvData.split('\n');

      // Remove empty lines
      const nonEmptyRows = rows.filter(row => row.trim() !== '');

      // Split each line into an array with ',' separator
      const data = nonEmptyRows.map(row => row.split(','));

      return data;
    })
    .catch(error => {
      console.error('There was a problem with the fetch operation:', error);
    });
}
  const color1 = 'rgba(255, 99, 132, 0.5)';
    const color2 = 'rgba(54, 162, 235, 0.5)';
   const color3 = 'rgba(255, 206, 86, 0.5)';
const csvUrl = 'static/csv/SpecialFile.csv';
fetchCSV(csvUrl)
  .then(data => {
    // Do something with the fetched CSV data
      console.log(data)
      data[0].pop()
      data[1].pop()
      data[2].pop()
        createBarPlot(data[0],5,'myChart1', color1,"Max Waiting Time","Distribution of max waiting time");
    createBarPlot(data[1],5, 'myChart2',color2,"Total Waiting Time","Distribution of total waiting time");
    createBarPlot(data[2],5,'myChart3', color3,"Turnaround time","Distribution of Turnaround time");









  });



