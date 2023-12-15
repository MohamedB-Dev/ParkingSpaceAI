console.log('Hello from main.js');

function updateParkingStatus(data) {
    try {
        const eventData = JSON.parse(data);

        const parkingStatusElement = document.getElementById('parking-status');
        parkingStatusElement.innerHTML = '';

        let rowElement = '';

        for (const area of eventData.area_status) {
            const isOccupied = !area.isOccupied;
            const bgColorClass = isOccupied ? 'danger' : 'success';

            const iconElement = isOccupied ? '<i class="bi bi-car-front text-black display-3"></i>' : '';

            rowElement += `<td class="bg-${bgColorClass} border border-4 border-dark col-2 py-2">${iconElement}</td>`;
        }

        parkingStatusElement.innerHTML = `<tr>${rowElement}</tr>`;

        const totalFreeSpacesElement = document.getElementById('total-free-spaces');
        totalFreeSpacesElement.textContent = `Total Available Parking: ${eventData.total_free_spaces}`;
    } catch (error) {
        console.error('Error parsing JSON data:', error);
    }
}

// Create a new EventSource to receive Server-Sent Events
const eventSource = new EventSource('/events');

// Listen for the 'message' event and call the updateParkingStatus function
eventSource.addEventListener('message', function (event) {
    updateParkingStatus(event.data);
});

// Handle errors and close events
eventSource.onerror = function (error) {
    console.error('EventSource failed:', error.message);
    eventSource.close();
};

eventSource.onclose = function () {
    if (eventSource.readyState === 2) {
        console.warn('EventSource closed unexpectedly.');
    } else {
        console.log('EventSource closed.');
    }
};
