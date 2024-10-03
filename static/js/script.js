// DOM Elements
const dateTimeInput = document.getElementById('departure-time');
const timeZoneInput = document.getElementById('utc-timezone');

const centralNameInput = document.getElementById('central-name');
const centralLatInput = document.getElementById('central-lat');
const centralLngInput = document.getElementById('central-lng');
const addCentralButton = document.getElementById('add-central');

const posNameInput = document.getElementById('pos-name')
const posLatInput = document.getElementById('pos-lat');
const posLngInput = document.getElementById('pos-lng');
const addPosButton = document.getElementById('add-pos');

// Global variables
var coords = [];
var central = {};
var markers = {}; 
var datetime = '';
var timezone = timeZoneInput.value;

// Generate unique id
function genID() {
  return '_' + Math.random().toString(36).substr(2, 9);
}

// Función para actualizar el contenido del popup
function updatePopup(coord) {
  var contenido;
  if (coord.name.trim() !== '') {
      contenido = `Punto: ${coord.name}`;
  } else {
      contenido = `Latitud: ${coord.lat.toFixed(5)}, Longitud: ${coord.lng.toFixed(5)}`;
  }
  markers[coord.id].bindPopup(contenido);
}

// Función para actualizar el marcador en el mapa
function updateMarker(coord) {
  var marker = markers[coord.id];
  if (marker) {
      var nuevaLatLng = L.latLng(coord.lat, coord.lng);
      marker.setLatLng(nuevaLatLng);
      // Actualizar el popup
      updatePopup(coord);
  }
}

// Delete a coordinate
function deleteCoord(id) {
  // Remove from coord list
  coords = coords.filter(function(coord) {
    return coord.id !== id;
  });

  // Remove marker from map
  map.removeLayer(markers[id]);
  delete markers[id];

  updateList();
}

// Update coordinates list on page view
function updateList() {
  const posMarkersList = document.getElementById('pos-markers-list');
  posMarkersList.innerHTML = ''

  coords.forEach(function(coord, index) {
    const markerItem = document.createElement('div');
    markerItem.className = 'flex justify-between items-center bg-muted text-muted-foreground p-2 rounded-md gap-2';
    
    // Name input
    var nameInput = document.createElement('input');
    nameInput.className = 'bg-input md:w-1/4 text-foreground p-2 rounded-md border border-border';
    nameInput.type = 'text';
    nameInput.placeholder = 'Nombre';
    nameInput.value = coord.name;
    nameInput.onchange = function() {
      coord.name = this.value;
      // Update marker's popup name
      var popupContent = coord.name ? `Punto: ${coord.name}` : `Latitud: ${coord.lat.toFixed(5)}, Longitud: ${coord.lng.toFixed(5)}`;
      markers[coord.id].bindPopup(popupContent);
    };

    // lat Input
    var latInput = document.createElement('input');
    latInput.className = 'bg-input md:w-1/4 text-foreground p-2 rounded-md border border-border';
    latInput.type = 'number';
    latInput.placeholder = 'Latitud';
    latInput.value = coord.lat.toFixed(5);
    latInput.onchange = function() {
        var nuevoLat = parseFloat(this.value);
        if (isNaN(nuevoLat) || nuevoLat < -90 || nuevoLat > 90) {
            alert('Por favor, ingresa una latitud válida entre -90 y 90.');
            this.value = coord.lat.toFixed(5);
            return;
        }
        coord.lat = nuevoLat;
        updateMarker(coord);
    };

    // Input para la longitud
    var lngInput = document.createElement('input');
    lngInput.className = 'bg-input md:w-1/4 text-foreground p-2 rounded-md border border-border';
    lngInput.type = 'number';
    lngInput.placeholder = 'Longitud';
    lngInput.value = coord.lng.toFixed(5);
    lngInput.onchange = function() {
        var nuevoLng = parseFloat(this.value);
        if (isNaN(nuevoLng) || nuevoLng < -180 || nuevoLng > 180) {
            alert('Por favor, ingresa una longitud válida entre -180 y 180.');
            this.value = coord.lng.toFixed(5);
            return;
        }
        coord.lng = nuevoLng;
        updateMarker(coord);
    };

    var deleteBtn = document.createElement('button');
    deleteBtn.className = 'md:w-1/4 bg-destructive text-destructive-foreground p-2 rounded-md'
    deleteBtn.textContent = 'Eliminar';
    deleteBtn.onclick = function() {
      deleteCoord(coord.id);
    };

    // Add inputs to infoDiv
    markerItem.appendChild(nameInput);
    markerItem.appendChild(latInput);
    markerItem.appendChild(lngInput);
    markerItem.appendChild(deleteBtn);

    posMarkersList.appendChild(markerItem);
  });
}

// Update coordinates list on page view
function updateCentral() {
  const centralMarkersList = document.getElementById('central-markers-list');
  centralMarkersList.innerHTML = ''

  const markerItem = document.createElement('div');
  markerItem.className = 'flex justify-between items-center bg-muted text-muted-foreground p-2 rounded-md gap-2';
  
  // Name input
  var nameInput = document.createElement('input');
  nameInput.className = 'bg-input md:w-1/3 text-foreground p-2 rounded-md border border-border';
  nameInput.type = 'text';
  nameInput.placeholder = 'Nombre';
  nameInput.value = central.name;
  nameInput.onchange = function() {
    central.name = this.value;
    // Update marker's popup name
    var popupContent = central.name ? `Punto: ${central.name}` : `Latitud: ${central.lat.toFixed(5)}, Longitud: ${central.lng.toFixed(5)}`;
    markers[central.id].bindPopup(popupContent);
  };

  // lat Input
  var latInput = document.createElement('input');
  latInput.className = 'bg-input md:w-1/3 text-foreground p-2 rounded-md border border-border';
  latInput.type = 'number';
  latInput.placeholder = 'Latitud';
  latInput.value = central.lat.toFixed(5);
  latInput.onchange = function() {
      var nuevoLat = parseFloat(this.value);
      if (isNaN(nuevoLat) || nuevoLat < -90 || nuevoLat > 90) {
          alert('Por favor, ingresa una latitud válida entre -90 y 90.');
          this.value = central.lat.toFixed(5);
          return;
      }
      central.lat = nuevoLat;
      updateMarker(central);
  };

  // Input para la longitud
  var lngInput = document.createElement('input');
  lngInput.className = 'bg-input md:w-1/3 text-foreground p-2 rounded-md border border-border';
  lngInput.type = 'number';
  lngInput.placeholder = 'Longitud';
  lngInput.value = central.lng.toFixed(5);
  lngInput.onchange = function() {
      var nuevoLng = parseFloat(this.value);
      if (isNaN(nuevoLng) || nuevoLng < -180 || nuevoLng > 180) {
          alert('Por favor, ingresa una longitud válida entre -180 y 180.');
          this.value = central.lng.toFixed(5);
          return;
      }
      central.lng = nuevoLng;
      updateMarker(central);
  };

  // Add inputs to infoDiv
  markerItem.appendChild(nameInput);
  markerItem.appendChild(latInput);
  markerItem.appendChild(lngInput);

  centralMarkersList.appendChild(markerItem);

}

// Initialize leaflet map
var map = L.map('map').setView([15.70, -90.30], 7); // Guatemala View

// Add a tiles layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Handle clicks on map
map.on('click', function(e) {
  var latlng = e.latlng;
  var id = genID();
  var coord = {
    id: id,
    name: id,
    lat: latlng.lat,
    lng: latlng.lng,
    avgTime: 0,
  };
  coords.push(coord);

  // Add marker to the map
  var marker = L.marker(latlng).addTo(map)
    .bindPopup(`Punto: ${coord.name}`)
    .openPopup();
  markers[id] = marker;

  updateList();
});

addCentralButton.addEventListener('click', () => {
  const name = centralNameInput.value
  const lat = parseFloat(centralLatInput.valueAsNumber);
  const lng = parseFloat(centralLngInput.valueAsNumber);

  if (lat && lng && name) {
    // Add central marker logic here
    // Add marker to the map
    var marker = L.marker({lat: lat, lng: lng}).addTo(map)
      .bindPopup(`Punto: ${name}`)
      .openPopup();

    var id = genID();
    markers[id] = marker;

    var coord = {
      id: id,
      name: name,
      lat: lat,
      lng: lng,
      avgTime: 0,
    };
    central = coord;
    
    updateCentral();
  }
});

addPosButton.addEventListener('click', () => {
  const name = posNameInput.value
  const lat = parseFloat(posLatInput.valueAsNumber);
  const lng = parseFloat(posLngInput.valueAsNumber);

  if (name && lat && lng) {
    // Add marker to the map
    var marker = L.marker({lat: lat, lng: lng}).addTo(map)
      .bindPopup(`Punto: ${name}`)
      .openPopup();

    var id = genID();
    markers[id] = marker;

    var coord = {
      id: id,
      name: name,
      lat: lat,
      lng: lng,
      avgTime: 0,
    };
    coords.push(coord);
    
    updateList();
  }
});

dateTimeInput.onchange = function() {
  datetime = dateTimeInput.value;
};

timeZoneInput.onchange = function() {
  timezone = timeZoneInput.value;
};

// Handling sending coordinates
document.getElementById('send-btn').addEventListener('click', function() {
  if (datetime == '' || new Date(datetime) < new Date()) {
    alert('Please, insert a valid date and time for calculations. Must be greater than todays date.');
    return;
  }
  if (timezone == '') {
    alert('Please, select a time zone');
    return;
  }
  if (central == {}) {
    alert('Please, insert a Central coordinates.');
    return;
  }
  if (coords.length === 0) {
    alert('Please, insert at least one POS coordinates by clicking in the map.');
    return;
  }

  departureTime = `${datetime}:00.000000${timezone}`;

  fetch('/calc_route', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({departureTime: departureTime, coords: coords, central: central}),
  })
  .then(response => response.json())
  .then(data => {
    document.getElementById('message').textContent = data.message;
  })
  .catch((error) => {
    console.error('Error:', error);
    document.getElementById('message').textContent = 'Something happened while calculating the route.';
  });
});

