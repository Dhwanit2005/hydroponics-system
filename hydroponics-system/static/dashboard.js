// Update sensor readings and log entries
function updateData() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            // Update sensor values
            document.getElementById('tds').textContent = data.tds.toFixed(0) + ' ppm';
            document.getElementById('ph').textContent = data.ph.toFixed(2);
            document.getElementById('temperature').textContent = data.temperature.toFixed(1) + ' °C';
            document.getElementById('water_level').textContent = data.water_level.toFixed(1) + ' cm';

            // Update timestamp
            const timestamp = new Date(data.timestamp);
            document.getElementById('timestamp').textContent = timestamp.toLocaleString();
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

// Initial data update
updateData();

// Update data every 5 seconds
setInterval(updateData, 5000);

// Manual pump control
document.getElementById('dose_nutrient').addEventListener('click', function() {
    if(confirm('Dose 10ml of nutrients?')) {
        fetch('/dose/nutrient/10')
            .then(response => response.json())
            .then(data => {
                if(data.success) {
                    alert('Nutrients dosed successfully');
                } else {
                    alert('Error dosing nutrients');
                }
            });
    }
});

document.getElementById('dose_ph').addEventListener('click', function() {
    if(confirm('Dose 5ml of pH adjuster?')) {
        fetch('/dose/ph/5')
            .then(response => response.json())
            .then(data => {
                if(data.success) {
                    alert('pH adjuster dosed successfully');
                } else {
                    alert('Error dosing pH adjuster');
                }
            });
    }
});