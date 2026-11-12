from io import BytesIO
import PyPDF2


def extraer_texto_pdf(archivo_pdf) -> str:
    """Extrae el texto de un archivo PDF en memoria usando PyPDF2."""
    try:
        contenido = (
            BytesIO(archivo_pdf.getvalue())
            if hasattr(archivo_pdf, "getvalue")
            else archivo_pdf
        )
        pdf_reader = PyPDF2.PdfReader(contenido)
        texto_completo = ""

        for numero_pagina, pagina in enumerate(pdf_reader.pages, start=1):
            texto_pagina = pagina.extract_text()
            if texto_pagina and texto_pagina.strip():
                texto_completo += f"\n--- Página {numero_pagina} ---\n"
                texto_completo += texto_pagina + "\n"

        texto_limpio = texto_completo.strip()
        if not texto_limpio:
            return (
                "Error: El PDF no contiene texto extraíble o está compuesto "
                "únicamente por imágenes."
            )

        return texto_limpio

    except Exception as exc:
        return f"Error al procesar el archivo PDF: {str(exc)}"
