from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfReader
import math  # Importa la libreria math per arrotondamento

# Inizializzazione dell'app Flask
app = Flask(__name__)

# Configurazioni per il caricamento dei file
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Funzione per verificare se il file caricato è un PDF
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Funzione per calcolare il numero di pagine di un PDF
def get_pdf_page_count(file_path):
    with open(file_path, "rb") as file:
        reader = PdfReader(file)
        return len(reader.pages)

# Route per la pagina iniziale (index.html)
@app.route('/')
def index():
    return render_template('index.html')  # Mostra la pagina del brand

# Route per la pagina del calcolatore (home.html)
@app.route('/home.html')
def home():
    return render_template('home.html')  # Mostra la pagina del calcolatore

@app.route('/contatti1.html')
def contatti():
    return render_template('contatti1.html')



# Route per il caricamento del file PDF e calcolo del prezzo
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Estrai il numero di pagine e calcola il prezzo
        num_pages = get_pdf_page_count(filepath)

        # Restituisci i valori selezionati
        color_option = request.form['colorOption']
        quality_option = request.form['qualityOption']
        binding = 'binding' in request.form

        # Calcola il prezzo
        price = calculate_price(num_pages, color_option, quality_option, binding)

        return jsonify({'price': price, 'num_pages': num_pages})

    return jsonify({'error': 'Invalid file format'}), 400

# Funzione per calcolare il prezzo
def calculate_price(num_pages, color_option, quality_option, binding):
    # Prezzi di base
    price_per_page_bw = 0.02
    price_per_page_color = 0.03

    # Prezzi aggiuntivi in base alla qualità
    additional_price = {
        "standard": 0.00,
        "high": 0.02,
        "max": 0.04
    }.get(quality_option, 0)

    price_per_page = price_per_page_bw if color_option == 'bw' else price_per_page_color
    total_price = num_pages * (price_per_page + additional_price)

    if binding:
        total_price += 1

    return math.ceil(total_price * 10) / 10

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
