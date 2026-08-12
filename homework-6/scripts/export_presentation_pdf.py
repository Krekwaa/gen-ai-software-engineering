"""Export the visually verified artifact-tool slide renders to one PDF."""

from pathlib import Path

from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

root = Path(__file__).resolve().parents[1]
renders = root / ".tmp" / "presentation" / "renders"
output = root / "docs" / "presentation.pdf"
slides = [renders / f"slide-{index}.png" for index in range(1, 7)]
missing = [path for path in slides if not path.exists()]
if missing:
    raise FileNotFoundError(f"Missing slide renders: {missing}")

canvas = Canvas(str(output), pagesize=(1280, 720), pageCompression=1)
canvas.setTitle("AI-Powered Transaction Processing Pipeline")
canvas.setAuthor("Vladyslav Shmygelskyy")
for slide in slides:
    canvas.drawImage(ImageReader(str(slide)), 0, 0, width=1280, height=720)
    canvas.showPage()
canvas.save()
print("Created docs/presentation.pdf")
