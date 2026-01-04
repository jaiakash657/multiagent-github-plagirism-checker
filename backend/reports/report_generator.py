# backend/reports/report_generator.py

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from xhtml2pdf import pisa


class ReportGenerator:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.templates_dir = self.base_dir / "templates"

        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(["html", "xml"])
        )

    def _cleanup_old_reports(self):
        """
        Delete all previously generated HTML and PDF reports
        """
        # Define the extensions we want to clean
        extensions = ["*.html", "*.pdf"]
        
        for ext in extensions:
            for file in self.base_dir.glob(ext):
                try:
                    # Avoid deleting the template files themselves if they are in base_dir
                    # (Though yours are in /templates, this is a safe check)
                    if "template" not in file.name.lower():
                        file.unlink()
                except Exception as e:
                    print(f"[REPORT] Failed to delete {file.name}: {e}")

    def generate_html(self, data: dict, report_name: str):
        """
        Generates a fresh report after cleaning old ones
        """
        # 1️⃣ Clean old HTML and PDF reports
        self._cleanup_old_reports()

        # 2️⃣ Render template
        template = self.env.get_template("report.html")
        rendered_html = template.render(data=data)

        # 3️⃣ Write new report
        output_path = self.base_dir / f"{report_name}.html"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)

        return str(output_path)

    def generate_pdf(self, html_path: str):
        """
        Convert HTML report to PDF using xhtml2pdf (Windows-safe)
        """
        html_path = Path(html_path)
        pdf_path = html_path.with_suffix(".pdf")

        with open(html_path, "r", encoding="utf-8") as html_file:
            html_content = html_file.read()

        with open(pdf_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(
                html_content,
                dest=pdf_file
            )

        if pisa_status.err:
            raise RuntimeError("PDF generation failed")

        return str(pdf_path)