from flask import Flask, request, render_template_string, send_file, redirect, url_for, flash
import os
import pikepdf
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import hashlib
from OpenSSL import crypto

app = Flask(__name__)
app.secret_key = 'secret_key'

UPLOAD_HTML = """
<!doctype html>
<title>PDF Signer</title>
<h1>Upload a PDF to Sign</h1>
<form method="POST" action="/sign" enctype="multipart/form-data">
  <input type="file" name="pdf_file" accept="application/pdf" required>
  <input type="submit" value="Sign PDF">
</form>
{% with messages = get_flashed_messages() %}
  {% if messages %}
    <ul>
      {% for message in messages %}
        <li>{{ message }}</li>
      {% endfor %}
    </ul>
  {% endif %}
{% endwith %}
"""

@app.route('/')
def upload_file():
    return render_template_string(UPLOAD_HTML)

@app.route('/sign', methods=['POST'])
def sign_pdf():
    if 'pdf_file' not in request.files:
        flash("No file uploaded")
        return redirect(url_for('upload_file'))

    pdf_file = request.files['pdf_file']
    input_pdf_path = os.path.join('uploads', pdf_file.filename)
    signed_pdf_path = os.path.join('signed', 'signed_' + pdf_file.filename)
    private_key_path = './keys/private.pem'
    cert_path = './keys/public.pem'

    os.makedirs('uploads', exist_ok=True)
    os.makedirs('signed', exist_ok=True)
    pdf_file.save(input_pdf_path)

    try:
        # Step 1: Create an overlay with the signature text using ReportLab
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Helvetica-Bold", 12)
        can.drawString(100, 50, "Signed by: Sudip Phuyal")
        can.save()

        # Move to the beginning of the buffer
        packet.seek(0)
        overlay_pdf = pikepdf.Pdf.open(packet)

        # Step 2: Open the original PDF and add the overlay content using copy_foreign
        with pikepdf.Pdf.open(input_pdf_path) as original_pdf:
            for page_num, page in enumerate(original_pdf.pages):
                if page_num == 0:  # Add to the first page only
                    overlay_content = original_pdf.copy_foreign(overlay_pdf.pages[0].Contents)
                    if not page.Contents:
                        page.Contents = overlay_content
                    else:
                        page.contents_add(overlay_content)

            # Step 3: Create a cryptographic hash of the PDF
            with open(input_pdf_path, 'rb') as f:
                pdf_data = f.read()
                pdf_hash = hashlib.sha256(pdf_data).digest()

            # Step 4: Create a digital signature using the private key
            private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, open(private_key_path).read())
            signature = crypto.sign(private_key, pdf_hash, 'sha256')

            # NOTE: Embedding this signature in a PDF field requires a library or tool that can add digital signature fields.
            # This code creates the signature but does not embed it in the PDF.

            original_pdf.save(signed_pdf_path)

        flash("PDF signed successfully! Note: This does not include an embedded cryptographic signature recognized by PDF viewers.")
        return redirect(url_for('download_signed_pdf', filename='signed_' + pdf_file.filename))

    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for('upload_file'))

@app.route('/download/<filename>')
def download_signed_pdf(filename):
    file_path = os.path.join('signed', filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash("File not found")
        return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True)
