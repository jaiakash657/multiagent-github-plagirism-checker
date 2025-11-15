import os
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


class ReportGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    def generate(self, report_data: dict, output_path: str):
        """
        report_data expected:
        {
           "repo_url": "...",
           "results": [
               {"agent": "...", "score": 0.82},
               ...
           ],
           "aggregated_score": 0.78
        }
        """
        template = self.env.get_template("report.html")
        rendered_html = template.render(data=report_data)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)

        return output_path
