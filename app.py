from tensorflow.keras.models import load_model
from flask import request, jsonify
import matplotlib.pyplot as plt
from numpy import array, float_
from io import BytesIO
import pandas as pd
import base64
import flask

model = load_model('model/binary_class_model.h5', compile = True)

app = flask.Flask(__name__)

# get example http://localhost:5000/?img=1&data=[0,1,8,3],[0,0,0,0]&dates=[2019-06-30 00:00:00,2019-06-30 01:00:00]
# get example http://localhost:5000/?img=True&data=[0,1,8,3],[0,0,0,0]&dates=[2019-06-30 00:00:00,2019-06-30 01:00:00]
# get example http://localhost:5000/?img=false&data=[0,1,8,3],[0,0,0,0]&dates=[2019-06-30 00:00:00,2019-06-30 01:00:00]
@app.route('/', methods=['GET'])
def home():
    dates = ''
    try:
        try:
            data = request.args['data']
            if len(data) < 0:
                return 'No hay datos para predecir'
        except Exception as e:
            return f'Ocurrio un error al cargar los datos, por favor verifique si incluyo la variable data. - {str(e)}'
        
        data = data.replace('],[','|').replace('[','').replace(']','')
        data = [ d.split(',') for d in data.split('|')]
        data = array(float_(data))

        predictions = model.predict(data)
        predictions_list = [predictions.flat[i] for i in range(1,len(predictions.flat),2)]
        predictions_list = array(float_(predictions_list)) 
        try:
            img = request.args['img']
        except :
            img = ''
        if not (img.lower() in ['true','1']):
            return jsonify(predictions_list.tolist())
        else:
            try:
                dates = request.args['dates']
                if len(dates) < 0:
                    return 'No hay fechas para visualizar'
            except Exception as e:
                return f'Ocurrio un error al cargar las fechas, por favor verifique si incluyo la variable dates. - {str(e)}'
            dates = dates.replace(',','|').replace('[','').replace(']','')
            dates = dates.split('|')
            if len(dates) < len(data):
                return f'El numero de fechas debe ser igual al de series de datos'
            df=pd.DataFrame(list(zip(dates,predictions_list)),columns=['Fecha','Probabilidad'])
            df["Fecha"]= pd.to_datetime(df["Fecha"])
            df = df.set_index('Fecha')
            ax = df.plot(style="-o")
            plt.title('Probabilidad de inundación')
            plt.tick_params(axis='x', rotation=10)
            plt.xlabel('Fecha')
            plt.ylabel('Probabilidad')
            plt.ylim([0,1.15])

            fig = ax.get_figure()
            # Save it to a temporary buffer.
            buf = BytesIO()
            fig.savefig(buf, format="png")
            # Embed the result in the html output.
            data = base64.b64encode(buf.getbuffer()).decode("ascii")
            return f"<img src='data:image/png;base64,{data}'/>"
    except Exception as e:
        return str(e)
    

if __name__ == "__main__":
    app.run()