// timeline.js - Improved version for CPU Scheduler Simulator
document.addEventListener('DOMContentLoaded', function() {
    initializeTimeline();
});

function initializeTimeline() {
    // Load the execution data
    fetch('static/csv/execution.csv')
        .then(response => response.text())
        .then(data => {
            if (data.trim() === '') {
                console.log('No execution data available');
                return;
            }
            renderTimeline(parseCSV(data));
        })
        .catch(error => console.error('Error loading execution data:', error));
}

function parseCSV(csvText) {
    // Parse CSV data
    const lines = csvText.trim().split('\n');
    
    // Handle empty CSV
    if (lines.length <= 1) {
        return [];
    }
    
    const executions = [];
    
    // Skip header row (assuming first row is header)
    for (let i = 1; i < lines.length; i++) {
        const parts = lines[i].split(',');
        if (parts.length >= 3) {
            executions.push({
                processId: parts[0].trim(),
                startTime: parseInt(parts[1]),
                endTime: parseInt(parts[2])
            });
        }
    }
    
    return executions;
}

function renderTimeline(executions) {
    if (!executions || executions.length === 0) {
        console.log('No execution data to render');
        return;
    }
    
    const timelineContainer = document.querySelector('.timeline');
    const rulerContainer = document.querySelector('.ruler');
    
    if (!timelineContainer || !rulerContainer) {
        console.error('Timeline or ruler container not found');
        return;
    }
    
    // Clear previous content
    timelineContainer.innerHTML = '';
    rulerContainer.innerHTML = '';
    
    // Calculate total execution time
    const maxEndTime = Math.max(...executions.map(exec => exec.endTime));
    
    // Get a list of unique process IDs for consistent coloring
    const uniqueProcessIds = [...new Set(executions.map(exec => exec.processId))];
    
    // Create timeline segments
    executions.forEach(execution => {
        const segment = document.createElement('div');
        segment.className = 'timeline-segment';
        
        // Calculate position and width based on start and end times
        const startPercent = (execution.startTime / maxEndTime) * 100;
        const duration = execution.endTime - execution.startTime;
        const widthPercent = (duration / maxEndTime) * 100;
        
        // Set segment styles
        segment.style.position = 'absolute';
        segment.style.left = `${startPercent}%`;
        segment.style.width = `${widthPercent}%`;
        segment.style.height = '100%';
        segment.style.top = '0';
        
        // Set background color based on process ID for consistency
        const colorIndex = uniqueProcessIds.indexOf(execution.processId);
        segment.style.backgroundColor = generateRandomBrightColor(colorIndex);
        
        // Add tooltip with process information
        segment.title = `Process ${execution.processId}: ${execution.startTime} - ${execution.endTime} (Duration: ${duration})`;
        
        // Add label to segment
        const label = document.createElement('span');
        label.className = 'segment-label';
        label.textContent = `P${execution.processId}`;
        label.style.position = 'absolute';
        label.style.top = '50%';
        label.style.left = '50%';
        label.style.transform = 'translate(-50%, -50%)';
        label.style.color = 'white';
        label.style.fontSize = '12px';
        label.style.fontWeight = 'bold';
        label.style.textShadow = '0 0 2px rgba(0,0,0,0.5)';
        
        // Only show label if segment is wide enough
        if (widthPercent > 3) {
            segment.appendChild(label);
        }
        
        timelineContainer.appendChild(segment);
    });
    
    // Create time ruler markers
    // Create about 10 markers for readability
    const markerCount = 10;
    const markerInterval = Math.ceil(maxEndTime / markerCount);
    
    for (let i = 0; i <= maxEndTime; i += markerInterval) {
        const marker = document.createElement('div');
        marker.className = 'ruler-marker';
        
        // Position marker
        const position = (i / maxEndTime) * 100;
        marker.style.position = 'absolute';
        marker.style.left = `${position}%`;
        marker.style.width = '1px';
        marker.style.height = '10px';
        marker.style.backgroundColor = '#95a5a6';
        marker.style.bottom = '0';
        
        // Add time label
        const label = document.createElement('span');
        label.className = 'ruler-label';
        label.textContent = i;
        label.style.position = 'absolute';
        label.style.bottom = '-20px';
        label.style.left = '0';
        label.style.transform = 'translateX(-50%)';
        label.style.fontSize = '10px';
        label.style.color = '#7f8c8d';
        
        marker.appendChild(label);
        rulerContainer.appendChild(marker);
    }
    
    // Add CSS to timeline container for better visualization
    timelineContainer.style.position = 'relative';
    timelineContainer.style.height = '60px';
    timelineContainer.style.backgroundColor = '#f8f9fa';
    timelineContainer.style.borderRadius = '5px';
    timelineContainer.style.marginBottom = '10px';
    timelineContainer.style.overflow = 'hidden';
    
    rulerContainer.style.position = 'relative';
    rulerContainer.style.height = '30px';
    rulerContainer.style.marginTop = '5px';
}

// Function to generate consistent colors for processes
// (Reusing the function from the main file)
function generateRandomBrightColor(i) {
    const brightColors = [
        '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', 
        '#1abc9c', '#d35400', '#34495e', '#16a085', '#c0392b',
        '#27ae60', '#8e44ad', '#2980b9', '#f1c40f', '#e67e22',
        '#95a5a6', '#7f8c8d', '#f0932b', '#eb4d4b', '#6ab04c',
        '#4834d4', '#be2edd', '#22a6b3', '#0097e6', '#8c7ae6',
        '#e84393', '#ff9ff3', '#f368e0', '#48dbfb', '#0abde3'
    ];

    i = i % brightColors.length;
    return brightColors[i];
}