# app.py - Simple Invoice Generator
# Save this in your ClientInvoice-Pro folder
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from flask import Flask, render_template_string, request, send_file
from fpdf import FPDF
from datetime import datetime
import os

app = Flask(__name__)

# Create folder for saved invoices
if not os.path.exists('invoices'):
    os.makedirs('invoices')

# Simple HTML page (no separate files needed!)
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>ClientInvoice Pro</title>
    <style>
        body { 
            font-family: Arial; 
            max-width: 600px; 
            margin: 50px auto; 
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #2c3e50; text-align: center; }
        input, textarea { 
            width: 100%; 
            padding: 10px; 
            margin: 8px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }
        button {
            background: #27ae60;
            color: white;
            padding: 12px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
            font-size: 16px;
        }
        button:hover { background: #219a52; }
        .field-group {
            margin-bottom: 15px;
        }
        label {
            font-weight: bold;
            color: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧾 ClientInvoice Pro</h1>
        <p style="text-align: center; color: #666;">Create professional invoices in seconds</p>
        
        <form method="POST">
            <div class="field-group">
                <label>Your Business Name</label>
                <input name="business_name" placeholder="e.g., ABC Consulting" required>
            </div>
            
            <div class="field-group">
                <label>Your Email</label>
                <input name="business_email" type="email" placeholder="you@business.com" required>
            </div>
            
            <div class="field-group">
                <label>Client Name</label>
                <input name="client_name" placeholder="e.g., John Smith" required>
            </div>
            
            <div class="field-group">
                <label>Client Email</label>
                <input name="client_email" type="email" placeholder="client@company.com" required>
            </div>
            
            <div class="field-group">
                <label>Service Description</label>
                <textarea name="service" rows="3" placeholder="e.g., Website Development - 20 hours" required></textarea>
            </div>
            
            <div class="field-group">
                <label>Amount ($)</label>
                <input name="amount" type="number" step="0.01" placeholder="500.00" required>
            </div>
            
            <div class="field-group">
                <label>Due Date</label>
                <input name="due_date" type="date" required>
            </div>
            
            <button type="submit">Generate Invoice PDF</button>
        </form>
    </div>
</body>
</html>
"""

class InvoicePDF(FPDF):
    def header(self):
        # Logo placeholder
        self.set_font('Arial', 'B', 24)
        self.set_text_color(44, 62, 80)
        self.cell(0, 20, 'INVOICE', 0, 1, 'L')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_invoice(data):
    pdf = InvoicePDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Invoice details
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(80, 80, 80)
    
    # Invoice number and date
    invoice_num = f"INV-{datetime.now().strftime('%Y%m%d')}-{hash(data['client_name']) % 1000:03d}"
    pdf.cell(0, 10, f'Invoice Number: {invoice_num}', 0, 1)
    pdf.cell(0, 10, f'Date: {datetime.now().strftime("%B %d, %Y")}', 0, 1)
    pdf.ln(10)
    
    # From/To section
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(95, 10, 'From:', 0, 0)
    pdf.cell(0, 10, 'Bill To:', 0, 1)
    
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(95, 8, data['business_name'], 0, 0)
    pdf.cell(0, 8, data['client_name'], 0, 1)
    pdf.cell(95, 8, data['business_email'], 0, 0)
    pdf.cell(0, 8, data['client_email'], 0, 1)
    pdf.ln(15)
    
    # Service details
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(130, 12, 'Description', 1, 0, 'L', True)
    pdf.cell(0, 12, 'Amount', 1, 1, 'R', True)
    
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(130, 12, data['service'], 1, 0, 'L')
    pdf.cell(0, 12, f"${float(data['amount']):,.2f}", 1, 1, 'R')
    pdf.ln(5)
    
    # Total
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(130, 12, 'Total Due:', 0, 0, 'R')
    pdf.set_text_color(39, 174, 96)
    pdf.cell(0, 12, f"${float(data['amount']):,.2f}", 0, 1, 'R')
    pdf.ln(10)
    
    # Due date
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(231, 76, 60)
    pdf.cell(0, 10, f'Payment Due: {data["due_date"]}', 0, 1, 'R')
    pdf.ln(20)
    
    # Payment instructions
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(0, 6, 
        'Payment Instructions:\n'
        'Please make payment within the due date to avoid late fees.\n'
        'Thank you for your business!', 0, 'C')
    
    # Save file
    filename = f"invoices/Invoice_{data['client_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    pdf.output(filename)
    return filename

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        data = request.form.to_dict()
        pdf_file = create_invoice(data)
        return send_file(pdf_file, as_attachment=True)
    
    return render_template_string(HTML_PAGE)

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 ClientInvoice Pro is running!")
    print("Open your browser and go to: http://localhost:5000")
    print("Press CTRL+C to stop")
    print("=" * 50)
    app.run(debug=True, port=5000)