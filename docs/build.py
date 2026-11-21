import subprocess, sys, weasyprint, pdfplumber
for f in sys.argv[1:]:
    subprocess.run(["pandoc", f + ".md", "-f", "markdown", "-t", "html", "-s", "--metadata", "pagetitle=" + f, "-c", "style.css", "-o", f + ".html"], check=True)
    d = weasyprint.HTML(f + ".html").render(stylesheets=[weasyprint.CSS(string="@page{size:A4;margin:13mm 14mm 12mm 14mm}")])
    d.write_pdf(f + ".pdf")
    with pdfplumber.open(f + ".pdf") as p:
        last = p.pages[-1]
        used = max((c["bottom"] for c in last.chars), default=0) / last.height
    print(f, "pages:", len(d.pages), f"last page used: {used:.0%}")
