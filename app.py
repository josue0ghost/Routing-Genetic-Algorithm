from flask import Flask, render_template, request, jsonify, json
import pandas as pd
import ga
import polyline

app = Flask(__name__)

@app.route("/")
def index():
  return render_template('index.html')

@app.route('/calc_route', methods=['POST'])
def calc_route():
  data = request.get_json()
  central = data.get('central')
  coords = data.get('coords', [])
  departureTime = data.get('departureTime')

  if not central:
    return jsonify({'mensaje': 'No se recibió central de carga.'}), 400
  
  if not coords:
    return jsonify({'mensaje': 'No se recibieron coordenadas.'}), 400

  if not departureTime:
    return jsonify({'mensaje': 'No se recibió hora de salida.'}), 400

  # Obtener la ruta de OSRM
  result_df = ga.ga_request(central=central, pos=coords, departure_time=departureTime)
  
  result_df['accion'] = result_df.apply(
    lambda row: 
      '<button class="bg-primary text-primary-foreground p-2 rounded-md" onclick="mostrarPolilineas({polilineas})">Mostrar rutas</button>'
      .format(polilineas=json.dumps([polyline.decode(line) for line in row.values[-2]])), 
      axis=1)
  
  if not result_df.empty:
      showing_df = result_df.drop('Polilineas', axis=1)
      return jsonify({'mensaje': showing_df.to_html(classes='w-full table-auto', escape=False)})
  else:
      return jsonify({'mensaje': 'Coordenadas procesadas pero falló la obtención de la ruta.'}), 500

if __name__ == '__main__':
    app.run(debug=True)