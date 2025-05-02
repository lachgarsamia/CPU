

var currentPage = 1;
var pageSize = 5; // Number of rows per page
var rowsNumber;

function displayTable() {
var table = document.getElementById("csvTable");

fetch("static/csv/process_table.csv")
.then(response => response.text())
.then(csvData => {
    // Split CSV data into rows
    var rows = csvData.trim().split("\n");
    rowsNumber = rows.length;

    // Clear existing table rows
    table.innerHTML = "";

    // Add header row with all columns
    var headers = rows[0].split(",");
    var headerRow = table.insertRow();
    headers.forEach(function(header) {
        var th = document.createElement("th");
        th.textContent = header;
        headerRow.appendChild(th);
    });

    // Calculate start and end index for current page
    var startIndex = (currentPage - 1) * pageSize + 1;
    var endIndex = Math.min(startIndex + pageSize - 1, rows.length - 1); // Adjusted to avoid accessing undefined row

    // Add data rows for current page with all columns
    for (var i = startIndex; i <= endIndex; i++) {
        var row = table.insertRow();
        var rowData = rows[i].split(",");
        rowData.forEach(function(cellData, index) {
var cell = row.insertCell();
var isEditable = index < 4 && index > 0; // Only first 4 columns are editable
if (isEditable) {
cell.contentEditable = true;
cell.row = i;
cell.idx =  index;
cell.addEventListener('input', debounce(function() {
    var rw = rows[cell.row].split(",");
    rw[cell.idx] = cell.textContent; // Update the cell value in rowData
    rows[cell.row] = rw.join(",");
    saveCSV(rows.join("\n")); // Pass the entire csvData to saveCSV function
    // Update scatter plot
    updateScatterPlot(rows);
}, 1000)); // Adjust delay as needed
}
cell.textContent = cellData;
});
    }

    // Destroy existing scatter plot if it exists
    var existingChart = Chart.getChart("scatterChart");
    if (existingChart) {
        existingChart.destroy();
    }

    // Generate scatter plot data using the first 4 columns
    var scatterData = [];
    for (var i = 1; i < rows.length; i++) {
        var rowData = rows[i].split(",");
        scatterData.push({
            x: parseInt(rowData[3]), // Assuming the 4th column is the x-axis data
            y: parseInt(rowData[1])  // Assuming the 2nd column is the y-axis data
        });
    }

    // Render scatter plot
    renderScatterPlot(scatterData);
});
}
function debounce(func, delay) {
let timer;
return function () {
const context = this;
const args = arguments;
clearTimeout(timer);
timer = setTimeout(() => {
    func.apply(context, args);
}, delay);
};
}
function updateScatterPlot(csvData) {
var existingChart = Chart.getChart("scatterChart");
    if (existingChart) {
        existingChart.destroy();
    }

var scatterData = [];
for (var i = 1; i < csvData.length; i++) {
var rowData = csvData[i].split(",");
scatterData.push({
    x: parseInt(rowData[3]), // Assuming the 4th column is the x-axis data
    y: parseInt(rowData[1])  // Assuming the 2nd column is the y-axis data
});
}
renderScatterPlot(scatterData);
}

function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        displayTable();
    }
}

function nextPage() {
    if (rowsNumber/pageSize  > currentPage){
        currentPage++;
        displayTable();
    }

}


function saveCSV(csvData) {
fetch('/save_csv', {
method: 'POST',
headers: {
    'Content-Type': 'application/json'
},
body: JSON.stringify({ csvData: csvData })
})
.then(response => {
if (!response.ok) {
    throw new Error('Failed to save CSV data');
}
console.log('CSV data saved successfully');
displayTable(); // Refresh table after successful save
fetch('static/js/timeline.js')
  .then(response => response.text())
  .then(scriptContent => eval(scriptContent));


fetch('static/js/csvTable.js')
  .then(response => response.text())
  .then(scriptContent => eval(scriptContent));

})




.catch(error => {
console.error('Error saving CSV data:', error);
});
}


function renderScatterPlot(data) {
Chart.defaults.font.size = 14;
Chart.defaults.elements.bar.borderWidth = 4;
    var ctx = document.getElementById('scatterChart').getContext('2d');


    var scatterChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Burst Time vs Arrival Time',
                data: data,
                backgroundColor: 'rgba(255, 99, 132, 0.5)', // Set the color of the dots
                pointRadius: 8, // Increase point size

            }]
        },
        options: {
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Arrival Time',
                        font: {
                            size: 14 // Increase label font size
                        }
                    },
                    ticks: {
                        font: {
                            size: 14 // Increase ticks font size
                        }
                    }
                },
                y: {
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Burst Time',
                        font: {
                            size: 14 // Increase label font size
                        }
                    },
                    ticks: {
                        font: {
                            size: 14 // Increase ticks font size
                        }
                    }
                }
            },
            layout: {
                padding: {
                    left: 15, // Adjust spacing between left edge and chart area
                    right: 15, // Adjust spacing between right edge and chart area
                    top: 15, // Adjust spacing between top edge and chart area
                    bottom: 15 // Adjust spacing between bottom edge and chart area
                }
            }
        }
    });
}




displayTable(); // Initial table display

