    // Function to fetch CSV

console.log("bvhuejnvkl ")
    document.getElementById("processTableOutput").innerHTML = ""
function fetchCSV(url) {
  return fetch(url)
    .then(response => response.text())
    .then(text => {
      return text.split('\n').map(row => row.split(','));
    });
}

// Function to convert CSV data to HTML table
function convertToHTMLTable(csvData) {
  let html = '<table border="1">';
  csvData.forEach(row => {
    html += '<tr>';
    row.forEach(cell => {
      html += `<td>${cell}</td>`;
    });
    html += '</tr>';
  });
  html += '</table>';
  return html;
}

// Main function to fetch CSV and display as HTML table
function displayCSVAsHTMLTable(csvURL, outputElementId) {
  fetchCSV(csvURL)
    .then(csvData => {

        var att = 0;
        var awt = 0;
        for (var i = 1;i<csvData.length-1;i++){
            att+= parseFloat(csvData[i][4]);
            awt+= parseFloat(csvData[i][6]);
        }
        att /= (csvData.length-1)
        awt /= (csvData.length-1)
        document.getElementById("att").innerHTML+= att.toFixed(2)
        document.getElementById("awt").innerHTML+= awt.toFixed(2)

      const htmlTable = convertToHTMLTable(csvData);
      document.getElementById(outputElementId).innerHTML += htmlTable;
    })
    .catch(error => {
      console.error('Error fetching CSV:', error);
    });
}

// Example usage:
const csvURL = 'static/csv/result.csv'; 
const outputElementId = 'processTableOutput'; 
displayCSVAsHTMLTable(csvURL, outputElementId);
