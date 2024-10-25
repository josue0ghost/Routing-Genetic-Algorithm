// DOM Elements
const dateTimeInput = document.getElementById('departure-time');

const centralelement = document.getElementById('central-name');
const centralLatInput = document.getElementById('central-lat');
const centralLngInput = document.getElementById('central-lng');
const addCentralButton = document.getElementById('add-central');

const poselement = document.getElementById('pos-name')
const posLatInput = document.getElementById('pos-lat');
const posLngInput = document.getElementById('pos-lng');
const posAvg1 = document.getElementById('pos-avg1');
const posAvg2 = document.getElementById('pos-avg2');
const posAvg3 = document.getElementById('pos-avg3');
const posAvg4 = document.getElementById('pos-avg4');
const posAvg5 = document.getElementById('pos-avg5');
const posAvg6 = document.getElementById('pos-avg6');
const posAvg7 = document.getElementById('pos-avg7');
const posAvg8 = document.getElementById('pos-avg8');
const posAvg9 = document.getElementById('pos-avg9');
const addPosButton = document.getElementById('add-pos');

// Initialize leaflet map
var map = L.map('map').setView([15.70, -90.30], 7); // Guatemala View

// Global variables
var coords = localStorage.getItem("coords") ? JSON.parse(localStorage.getItem("coords")) : [];
var central = localStorage.getItem("central") ? JSON.parse(localStorage.getItem("central")) : {};
var markers = {}; 
var polylinesList = [];
var datetime = '';

// Generate unique id
function genID() {
  return '_' + Math.random().toString(36).substr(2, 9);
}

if (JSON.stringify(central) != '{}') {
  updateCentral();
  setExistingMarkers(central)
}
if (coords != []) {
  updateList();
  coords.forEach(function(coord, index) {
    setExistingMarkers(coord)
  });
}

function setExistingMarkers(coord) {
  
  var marker = L.marker({lat: coord.lat, lng: coord.lng}).addTo(map)
      .bindPopup(`Punto: ${coord.name}`)
      .openPopup();

  markers[coord.id] = marker
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

function createInput(type, placeholder, value, func) {
  var element = document.createElement('input');
  element.className = 'bg-input md:w-1/4 text-foreground p-2 rounded-md border border-border';
  element.type = type;
  element.placeholder = placeholder;
  element.value = value;
  element.onchange = func

  return element
}
// Update coordinates list on page view
function updateList() {
  const posMarkersList = document.getElementById('pos-markers-list');
  posMarkersList.innerHTML = ''

  coords.forEach(function(coord, index) {
    const markerItem = document.createElement('div');
    markerItem.className = 'flex justify-between items-center bg-muted text-muted-foreground p-2 rounded-md gap-2';
    
    // Name input
    var element = createInput('text', 'Nombre', coord.name, function() {
      coord.name = this.value;
      // Update marker's popup name
      var popupContent = coord.name ? `Punto: ${coord.name}` : `Latitud: ${coord.lat.toFixed(5)}, Longitud: ${coord.lng.toFixed(5)}`;
      markers[coord.id].bindPopup(popupContent);
      updateList();
    })

    // lat Input
    var latInput = createInput('number', 'Latitud', coord.lat.toFixed(5),  function() {
      var nuevoLat = parseFloat(this.value);
      if (isNaN(nuevoLat) || nuevoLat < -90 || nuevoLat > 90) {
          alert('Por favor, ingresa una latitud válida entre -90 y 90.');
          this.value = coord.lat.toFixed(5);
          return;
      }
      coord.lat = nuevoLat;
      updateMarker(coord);
      updateList();
    })
    

    // lng input
    var lngInput = createInput('number', 'Longitud', coord.lng.toFixed(5), function() {
      var nuevoLng = parseFloat(this.value);
      if (isNaN(nuevoLng) || nuevoLng < -180 || nuevoLng > 180) {
          alert('Por favor, ingresa una longitud válida entre -180 y 180.');
          this.value = coord.lng.toFixed(5);
          return;
      }
      coord.lng = nuevoLng;
      updateMarker(coord);
      updateList();
    })
    

    // entree_time input
    var entree_time = createInput('number', 'Tiempo de entrada prom. (s)', coord.entree_time.toFixed(5), function() {
      var newEntree_time = parseFloat(this.value);
      if (isNaN(newEntree_time)) {
        alert('Por favor, ingresa un tiempo válido en segundos');
        this.value = coord.entree_time.toFixed(5);
        return;
      }
      coord.entree_time = newEntree_time;
      updateMarker(coord);
      updateList();
    })

    // unloading_time input
    var unloading_time = createInput('number', 'Tiempo de descarga prom. (s)', coord.unloading_time.toFixed(5), function() {
      var newunloading_time = parseFloat(this.value);
      if (isNaN(newunloading_time)) {
        alert('Por favor, ingresa un tiempo válido en segundos');
        this.value = coord.unloading_time.toFixed(5);
        return;
      }
      coord.unloading_time = newunloading_time;
      updateMarker(coord);
      updateList();
    })
    
    // journey2pos_time input
    var journey2pos_time = createInput('number', 'Tiempo de viaje de ida al local prom. (s)', coord.journey2pos_time.toFixed(5), function() {
      var newjourney2pos_time = parseFloat(this.value);
      if (isNaN(newjourney2pos_time)) {
        alert('Por favor, ingresa un tiempo válido en segundos');
        this.value = coord.journey2pos_time.toFixed(5);
        return;
      }
      coord.journey2pos_time = newjourney2pos_time;
      updateMarker(coord);
      updateList();
    })

    // delivery_time input
    var delivery_time = createInput('number', 'Tiempo de entrega prom. (s)', coord.delivery_time.toFixed(5), function() {
      var newdelivery_time = parseFloat(this.value);
      if (isNaN(newdelivery_time)) {
        alert('Por favor, ingresa un tiempo válido en segundos');
        this.value = coord.delivery_time.toFixed(5);
        return;
      }
      coord.delivery_time = newdelivery_time;
      updateMarker(coord);
      updateList();
    })

    // journey2unloadingpoint_time input
    var journey2unloadingpoint_time = createInput('number', 'Tiempo de viaje de regreso al camión prom. (s)', coord.journey2unloadingpoint_time.toFixed(5), function() {
      var newjourney2unloadingpoint_time = parseFloat(this.value);
      if (isNaN(newjourney2unloadingpoint_time)) {
        alert('Por favor, ingresa un tiempo válido en segundos');
        this.value = coord.journey2unloadingpoint_time.toFixed(5);
        return;
      }
      coord.journey2unloadingpoint_time = newjourney2unloadingpoint_time;
      updateMarker(coord);
      updateList();
    })

    // checkout_time input
    var checkout_time = createInput('number', 'Tiempo de salida prom. (s)', coord.checkout_time.toFixed(5), function() {
      var newcheckout_time = parseFloat(this.value);
      if (isNaN(newcheckout_time)) {
        alert('Por favor, ingresa un tiempo válido en segundos');
        this.value = coord.checkout_time.toFixed(5);
        return;
      }
      coord.checkout_time = newcheckout_time;
      updateMarker(coord);
      updateList();
    })

    // min_travels input
    var min_travels = createInput('number', 'Mínimo de viajes necesarios', coord.min_travels.toFixed(5), function() {
      var newmin_travels = parseFloat(this.value);
      if (isNaN(newmin_travels)) {
        alert('Por favor, ingresa número válido');
        this.value = coord.min_travels.toFixed(5);
        return;
      }
      coord.min_travels = newmin_travels;
      updateMarker(coord);
      updateList();
    })

    // max_travels input
    var max_travels = createInput('number', 'Máximo de viajes necesarios', coord.max_travels.toFixed(5), function() {
      var newmax_travels = parseFloat(this.value);
      if (isNaN(newmax_travels)) {
        alert('Por favor, ingresa número válido');
        this.value = coord.max_travels.toFixed(5);
        return;
      }
      coord.max_travels = newmax_travels;
      updateMarker(coord);
      updateList();
    })

    // extra_times input
    var extra_times = createInput('number', 'Tiempos extras (s)', coord.extra_times.toFixed(5), function() {
      var newextra_times = parseFloat(this.value);
      if (isNaN(newextra_times)) {
        alert('Por favor, ingresa un tiempo válido en segundos');
        this.value = coord.extra_times.toFixed(5);
        return;
      }
      coord.extra_times = newextra_times;
      updateMarker(coord);
      updateList();
    })

    var deleteBtn = document.createElement('button');
    deleteBtn.className = 'md:w-1/4 bg-destructive text-destructive-foreground p-2 rounded-md'
    deleteBtn.textContent = 'Eliminar';
    deleteBtn.onclick = function() {
      deleteCoord(coord.id);
    };

    // Add inputs to infoDiv
    markerItem.appendChild(element);
    markerItem.appendChild(latInput);
    markerItem.appendChild(lngInput);
    markerItem.appendChild(entree_time);
    markerItem.appendChild(unloading_time);
    markerItem.appendChild(journey2pos_time);
    markerItem.appendChild(delivery_time);
    markerItem.appendChild(journey2unloadingpoint_time);
    markerItem.appendChild(checkout_time);
    markerItem.appendChild(min_travels);
    markerItem.appendChild(max_travels);
    markerItem.appendChild(extra_times);
    markerItem.appendChild(deleteBtn);

    posMarkersList.appendChild(markerItem);
  });

  localStorage.setItem("coords", JSON.stringify(coords))
}

// Update coordinates list on page view
function updateCentral() {
  const centralMarkersList = document.getElementById('central-markers-list');
  centralMarkersList.innerHTML = ''

  const markerItem = document.createElement('div');
  markerItem.className = 'flex justify-between items-center bg-muted text-muted-foreground p-2 rounded-md gap-2';
  
  // Name input
  var element = document.createElement('input');
  element.className = 'bg-input md:w-1/3 text-foreground p-2 rounded-md border border-border';
  element.type = 'text';
  element.placeholder = 'Nombre';
  element.value = central.name;
  element.onchange = function() {
    central.name = this.value;
    // Update marker's popup name
    var popupContent = central.name ? `Punto: ${central.name}` : `Latitud: ${central.lat.toFixed(5)}, Longitud: ${central.lng.toFixed(5)}`;
    markers[central.id].bindPopup(popupContent);
    updateCentral();
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
      updateCentral();
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
      updateCentral();
  };

  // Add inputs to infoDiv
  markerItem.appendChild(element);
  markerItem.appendChild(latInput);
  markerItem.appendChild(lngInput);

  centralMarkersList.appendChild(markerItem);

  localStorage.setItem("central", JSON.stringify(central))
}

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
    entree_time: 0,
    unloading_time: 0,
    journey2pos_time: 0,
    delivery_time: 0,
    journey2unloadingpoint_time: 0,
    checkout_time: 0,
    min_travels: 1,
    max_travels: 1,
    extra_times: 0,
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
  const name = centralelement.value
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
  const name = poselement.value
  const lat = parseFloat(posLatInput.valueAsNumber);
  const lng = parseFloat(posLngInput.valueAsNumber);
  const entree_time = parseFloat(posAvg1.valueAsNumber);
  const unloading_time = parseFloat(posAvg2.valueAsNumber);
  const journey2pos_time = parseFloat(posAvg3.valueAsNumber);
  const delivery_time = parseFloat(posAvg4.valueAsNumber);
  const journey2unloadingpoint_time = parseFloat(posAvg5.valueAsNumber);
  const checkout_time = parseFloat(posAvg6.valueAsNumber);
  const min_travels = parseFloat(posAvg7.valueAsNumber);
  const max_travels = parseFloat(posAvg8.valueAsNumber);
  const extra_times = parseFloat(posAvg9.valueAsNumber);
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
      entree_time: entree_time,
      unloading_time: unloading_time,
      journey2pos_time: journey2pos_time,
      delivery_time: delivery_time,
      journey2unloadingpoint_time: journey2unloadingpoint_time,
      checkout_time: checkout_time,
      min_travels: min_travels,
      max_travels: max_travels,
      extra_times: extra_times,
    };
    coords.push(coord);
    
    updateList();
  }
});

dateTimeInput.onchange = function() {
  datetime = dateTimeInput.value;
};

// Handling sending coordinates
document.getElementById('send-btn').addEventListener('click', function() {
  if (datetime == '' || new Date(datetime) < new Date()) {
    alert('Please, insert a valid date and time for calculations. Must be greater than todays date.');
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

  departureTime = `${datetime}:00.000000-06:00`;

  fetch('/calc_route', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({departureTime: departureTime, coords: coords, central: central}),
  })
  .then(response => response.json())
  .then(data => {
    document.getElementById('mensaje').innerHTML = data.mensaje;
  })
  .catch((error) => {
    console.error('Error:', error);
    document.getElementById('mensaje').textContent = 'Something happened while calculating the route.';
  });
});

function mostrarPolilineas(polilineasData) {
  // Parsear las polilíneas de texto JSON a un array de coordenadas
  const polylines = polilineasData;
  
  // limpiar polylineas antiguas
  if (polylinesList.length != 0) {
    polylinesList.forEach(function (item) {
      map.removeLayer(item)
    });
    polylinesList = []
  }

  // Crear cada polilínea en el mapa
  polylines.forEach((coords) => {
      const polyline = L.polyline(coords, {color: 'blue'}).addTo(map);
      polylinesList.push(polyline);
      // Ajustar el mapa para incluir la polilínea
      map.fitBounds(polyline.getBounds());
  });
}