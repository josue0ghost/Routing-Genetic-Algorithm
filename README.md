# Genetic-Algorithm

pip install -r ./requirements.txt

# OSRM 
Ejemplo para Guatemala. Instrucciones más detalladas en (https://rpubs.com/HAVB/osrm)

cd Guatemala

wget https://download.geofabrik.de/central-america/guatemala-latest.osm.pbf

Extracción para el modo automóvil (car) con:

docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/Guatemala/guatemala-latest.osm.pbf

Dividir el grafo en celdas, ejecutando:

docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/Guatemala/guatemala-latest.osrm

Asignar “peso” a cada celda del grafo con:

docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/Guatemala/guatemala-latest.osrm

Iniciar el servicio de ruteo:

docker run -t -i -p 5000:5000 -v "${PWD}:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/Guatemala/guatemala-latest.osrm