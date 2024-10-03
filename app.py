from flask import Flask, render_template, request, jsonify
import ga

app = Flask(__name__)

@app.route("/")
def hello_world():
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
    return jsonify({'mensaje'})

  # Obtener la ruta de OSRM
  ruta = ga.ga_request(central=central, pos=coords, departure_time=departureTime)
  if ruta:
      print("Ruta obtenida de OSRM:")
      print(ruta)
      return jsonify({'mensaje': 'Coordenadas procesadas y ruta obtenida exitosamente.'}), 200
  else:
      return jsonify({'mensaje': 'Coordenadas procesadas pero falló la obtención de la ruta.'}), 500
  
if __name__ == '__main__':
    app.run(debug=True)