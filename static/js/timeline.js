function generateRandomBrightColor(i) {
    const brightColors = [
        'red', 'blue', 'green', 'orange', 'yellow', 'cyan', 'magenta',
        'lime', 'pink', 'turquoise', 'gold', 'purple', 'violet', 'skyblue', 'coral',
         'teal', 'lavender', 'maroon', 'olive', 'navy', 'peach', 'indigo',
        'tomato', 'orchid', 'slateblue', 'seagreen', 'peru', 'crimson', 'darkorange','salmon'
    ];  

    i = i % 30;

    return brightColors[i];
}



document.getElementsByClassName("ruler")[0].innerHTML = "";

fetch("static/csv/execution.csv") // Replace 'yourfile.csv' with the URL of your CSV file
    .then(response => response.text())
    .then(csvText => {
        const rows = csvText.trim().split('\n');
        const headers = rows[0].trim().split(',');

        const events = [];
        for (let i = 1; i < rows.length; i++) {
            const values = rows[i].trim().split(',');
            if (values.length === headers.length) {
                const obj = {};
                for (let j = 0; j < headers.length; j++) {
                    obj[headers[j]] = values[j];
                }
                events.push(obj);
            }
        }
        console.log(events)

        const timeline = document.querySelector(".timeline");
        const ruler = document.querySelector(".ruler");
        events.forEach(event => {
            const eventElement = document.createElement("div");
            eventElement.classList.add("event");
            eventElement.setAttribute("id", "event" + event.id); // Set id attribute
            const maxEndTime = Math.max(...events.map(event => event.end));
            eventElement.style.left = event.start * 100 / maxEndTime + "%";

            eventElement.style.width = (event.end - event.start) * 100 / maxEndTime + "%";
            if (event.id == "Context_Switch") {
                eventElement.style.backgroundColor = 'black';
            } else {
                eventElement.style.backgroundColor = generateRandomBrightColor(event.id);
            }
            if (event.id != "Context_Switch") {
                eventElement.textContent = "P" + event.id; // Display event id
            }

            timeline.appendChild(eventElement);
        });

        const maxEndTime = Math.max(...events.map(event => event.end));
        const numTicks = 10;
        const tickInterval = maxEndTime / numTicks;

        for (let i = 0; i <= numTicks; i++) {
            const tickPosition = (i / numTicks) * maxEndTime;
            const tickElement = document.createElement("div");
            tickElement.classList.add("tick");
            tickElement.style.left = tickPosition * 100 / maxEndTime + "%";

            const tickLabel = document.createElement("span");
            tickLabel.classList.add("tick-label");
            tickLabel.textContent = Math.round(i * tickInterval);
            tickElement.appendChild(tickLabel);

            ruler.appendChild(tickElement);
        }
    })
    
    

  
