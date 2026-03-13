from __future__ import annotations
from typing import List
import datetime

from backend.prolog_engine import ResultadoDiagnostico


#Aqui se generan los PDF con los resultados 
# Colores del sistema
COLOR_PRIMARY = (26/255, 115/255, 232/255)   # Azul
COLOR_ALTA    = (234/255, 67/255, 53/255)    # Rojo
COLOR_MEDIA   = (251/255, 188/255, 4/255)    # Amarillo
COLOR_BAJA    = (52/255, 168/255, 83/255)    # Verde
COLOR_GRIS    = (95/255, 99/255, 104/255)

URGENCIA_TEXTO = {
    "alta":  "⚠ Consulta médica inmediata sugerida",
    "media": "Observación recomendada",
    "baja":  "Posible automanejo",
}
URGENCIA_COLOR = {
    "alta":  COLOR_ALTA,
    "media": COLOR_MEDIA,
    "baja":  COLOR_BAJA,
}

#Aqui se genera el informe PDF con los resultados
def generar_informe_pdf(resultados: List[ResultadoDiagnostico], ruta_salida: str) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    story = []

    #encabezado para el PDF 
    estilo_titulo = ParagraphStyle(
        "titulo",
        parent=styles["Title"],
        textColor=colors.HexColor("#1A73E8"),
        fontSize=22,
        spaceAfter=4,
    )
    estilo_sub = ParagraphStyle(
        "sub",
        parent=styles["Normal"],
        textColor=colors.HexColor("#5F6368"),
        fontSize=10,
        spaceAfter=2,
    )
    estilo_h2 = ParagraphStyle(
        "h2",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#202124"),
        fontSize=13,
        spaceBefore=14,
        spaceAfter=4,
    )
    estilo_body = ParagraphStyle(
        "body",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
    )
    estilo_label = ParagraphStyle(
        "label",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#5F6368"),
    )

    story.append(Paragraph("MediLogic", estilo_titulo))
    story.append(Paragraph(
        "Sistema Experto de Diagnóstico Médico Preliminar · USAC Ingeniería IA1",
        estilo_sub))
    story.append(Paragraph(
        f"Informe generado el {datetime.datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}",
        estilo_sub))
    story.append(HRFlowable(width="100%", thickness=2,
                              color=colors.HexColor("#1A73E8"), spaceAfter=10))

    # Disclaimer
    story.append(Paragraph(
        "⚕ <b>AVISO IMPORTANTE:</b> Este informe es de orientación preliminar y NO sustituye "
        "la consulta con un médico profesional. Ante cualquier síntoma grave, acude "
        "inmediatamente a un centro de salud.",
        ParagraphStyle("disclaimer", parent=styles["Normal"], fontSize=8,
                       textColor=colors.HexColor("#EA4335"),
                       backColor=colors.HexColor("#FFF3F2"),
                       borderPad=6, leftIndent=6, rightIndent=6,
                       spaceAfter=12)))

    # Resumen del diagnostico
    story.append(Paragraph("Diagnósticos ordenados por afinidad", estilo_h2))

    resumen_data = [["#", "Enfermedad", "% Afinidad", "Urgencia"]]
    for i, r in enumerate(resultados):
        resumen_data.append([
            str(i + 1),
            r.enfermedad.replace("_", " ").title(),
            f"{r.afinidad}%",
            URGENCIA_TEXTO.get(r.urgencia, r.urgencia),
        ])

    t = Table(resumen_data, colWidths=[1*cm, 5.5*cm, 2.5*cm, 7*cm])
    urg_colors_map = {"alta": colors.HexColor("#FDECEC"),
                      "media": colors.HexColor("#FFF8E1"),
                      "baja": colors.HexColor("#E8F5E9")}
    table_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A73E8")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("ALIGN",      (2, 0), (2, -1), "CENTER"),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#DADCE0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    # Color de fila según urgencia
    for i, r in enumerate(resultados):
        bg = urg_colors_map.get(r.urgencia, colors.white)
        table_style.append(("BACKGROUND", (0, i+1), (-1, i+1), bg))

    t.setStyle(TableStyle(table_style))
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    # Detalle por la enfermedad
    story.append(Paragraph("Detalle de cada diagnóstico", estilo_h2))

    for i, r in enumerate(resultados):
        # Título de la enfermedad
        urg_color_hex = {
            "alta":  "#EA4335", "media": "#FBBC04", "baja": "#34A853"
        }.get(r.urgencia, "#5F6368")

        story.append(Paragraph(
            f'<font color="{urg_color_hex}">●</font> '
            f'<b>{r.enfermedad.replace("_", " ").upper()}</b> — '
            f'{r.afinidad}% de afinidad',
            ParagraphStyle("enf_header", parent=styles["Normal"],
                           fontSize=11, spaceBefore=10, spaceAfter=3)))

        # Urgencia
        story.append(Paragraph(
            f'<b>Nivel de urgencia:</b> {URGENCIA_TEXTO.get(r.urgencia, r.urgencia)}',
            estilo_body))

        # Medicamentos
        meds = ", ".join(r.medicamentos) if r.medicamentos else "Ninguno disponible (verifique contraindicaciones)"
        story.append(Paragraph(f'<b>Medicamentos seguros sugeridos:</b> {meds}', estilo_body))

        # Síntomas coincidentes
        sint = ", ".join(r.sintomas_coincidentes) if r.sintomas_coincidentes else "—"
        story.append(Paragraph(f'<b>Síntomas que coincidieron:</b> {sint}', estilo_body))

        # Reglas Prolog activadas
        reglas = (
            f"sintomas_coincidentes/2 → [{sint}]  |  "
            f"porcentaje_afinidad/2 → {r.afinidad}%  |  "
            f"nivel_urgencia/2 → {r.urgencia}  |  "
            f"medicamento_seguro_para/2 → [{meds}]"
        )
        story.append(Paragraph(
            f'<font color="#5F6368"><i><b>Reglas Prolog activadas:</b> {reglas}</i></font>',
            estilo_body))

        story.append(HRFlowable(width="100%", thickness=0.5,
                                  color=colors.HexColor("#DADCE0"), spaceAfter=4))

    # pie de pagina
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "MediLogic · Universidad San Carlos de Guatemala · Facultad de Ingeniería · IA1 2026",
        ParagraphStyle("footer", parent=styles["Normal"], fontSize=7,
                       textColor=colors.HexColor("#5F6368"), alignment=TA_CENTER)))

    doc.build(story)
