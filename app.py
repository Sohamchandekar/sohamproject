from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import io
import tempfile

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if request.method == 'POST':
        pdf_file = request.files['pdf_file']
        image_file = request.files['image_file']

        pdf_content = pdf_file.read()
        image_content = image_file.read()

        processed_pdf = add_image_to_pdf(pdf_content, image_content)

        return send_file(io.BytesIO(processed_pdf),
                         download_name="output.pdf", as_attachment=True)

def add_image_to_pdf(pdf_content, image_content):
    pdf_reader = PdfReader(io.BytesIO(pdf_content))
    pdf_writer = PdfWriter()

    image = Image.open(io.BytesIO(image_content))
    new_width = letter[0]
    new_height = (new_width / image.width) * image.height

    temp_image_path = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    resized_image = image.resize((int(new_width), int(new_height)))
    resized_image.save(temp_image_path.name)

    for page_number in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_number]

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        y_coordinate = letter[1] - new_height

        can.drawImage(temp_image_path.name, 0, y_coordinate, width=new_width, height=new_height)
        can.showPage()
        can.save()

        packet.seek(0)
        overlay = PdfReader(packet)
        page.merge_page(overlay.pages[0])

        pdf_writer.add_page(page)

    output_pdf = io.BytesIO()
    pdf_writer.write(output_pdf)

    return output_pdf.getvalue()

if __name__ == '__main__':
    app.run(debug=True)
