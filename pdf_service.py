import io
import uuid
import logging
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from config import COMPANY, BANK, VAT_RATE, DEFAULT_PAYMENT_DAYS, PDF_COLORS, PDF_MARGINS_CM

logger = logging.getLogger(__name__)


def generate_invoice_pdf(client_name: str, amount_ht: float, vat_rate: float = 0.20) -> tuple[io.BytesIO, str]:
    """
    Génère une facture PDF professionnelle au format A4 entièrement en mémoire.
    
    :param client_name: Nom du client ou de l'entreprise cliente
    :param amount_ht: Montant Hors Taxe (doit être > 0)
    :param vat_rate: Taux de TVA (par défaut 20% = 0.20)
    :return: (io.BytesIO buffer prêt à l'envoi HTTP, invoice_number: str)
    """
    # 1. Calculs financiers
    amount_ht = float(amount_ht)
    amount_vat = amount_ht * vat_rate
    amount_ttc = amount_ht + amount_vat
    
    # 2. Métadonnées de la facture
    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    due_date_str = (now + timedelta(days=DEFAULT_PAYMENT_DAYS)).strftime("%d/%m/%Y")
    invoice_number = f"FAC-{now.strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
    
    # 3. Initialisation du buffer mémoire (in-memory BytesIO)
    buffer = io.BytesIO()
    
    # Configuration du document A4 avec marges configurables
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=PDF_MARGINS_CM * cm,
        leftMargin=PDF_MARGINS_CM * cm,
        topMargin=PDF_MARGINS_CM * cm,
        bottomMargin=PDF_MARGINS_CM * cm,
        title=f"Facture {invoice_number}",
        author=COMPANY["name"]
    )
    
    story = []
    
    # Styles typographiques
    styles = getSampleStyleSheet()
    
    # Palette de couleurs modernes & professionnelles (depuis config)
    PRIMARY_COLOR = colors.HexColor(PDF_COLORS["primary"])
    TEXT_DARK = colors.HexColor(PDF_COLORS["text_dark"])
    TEXT_MUTED = colors.HexColor(PDF_COLORS["text_muted"])
    BG_LIGHT = colors.HexColor(PDF_COLORS["bg_light"])
    BORDER_COLOR = colors.HexColor(PDF_COLORS["border"])
    
    # Définition des styles personnalisés
    style_company_name = ParagraphStyle(
        'CompanyName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=PRIMARY_COLOR
    )
    
    style_company_sub = ParagraphStyle(
        'CompanySub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=TEXT_MUTED
    )
    
    style_invoice_title = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        alignment=2,  # Alignement à droite
        textColor=PRIMARY_COLOR
    )
    
    style_invoice_meta = ParagraphStyle(
        'InvoiceMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        alignment=2,
        textColor=TEXT_DARK
    )
    
    style_section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=PRIMARY_COLOR
    )
    
    style_body = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK
    )
    
    style_body_bold = ParagraphStyle(
        'BodyDarkBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK
    )
    
    style_th = ParagraphStyle(
        'TableHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )
    
    # -------------------------------------------------------------
    # 1. EN-TÊTE : Entreprise émettrice (Gauche) vs Infos Facture (Droite)
    # -------------------------------------------------------------
    company_info = [
        Paragraph(f"<b>{COMPANY['name']}</b>", style_company_name),
        Paragraph(COMPANY['address'], style_company_sub),
        Paragraph(f"SIRET : {COMPANY['siret']} — N° TVA : {COMPANY['vat_number']}", style_company_sub),
        Paragraph(f"{COMPANY['email']} | {COMPANY['phone']}", style_company_sub),
    ]
    
    invoice_meta = [
        Paragraph("FACTURE", style_invoice_title),
        Spacer(1, 4),
        Paragraph(f"<b>N° Facture :</b> {invoice_number}", style_invoice_meta),
        Paragraph(f"<b>Date d'émission :</b> {date_str}", style_invoice_meta),
        Paragraph(f"<b>Date d'échéance :</b> {due_date_str}", style_invoice_meta),
    ]
    
    header_table = Table(
        [[company_info, invoice_meta]],
        colWidths=[10 * cm, 8 * cm]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_COLOR, spaceBefore=4, spaceAfter=14))
    
    # -------------------------------------------------------------
    # 2. BLOCS INFORMATIONS CLIENT ET PAIEMENT
    # -------------------------------------------------------------
    client_box = [
        Paragraph("FACTURÉ À", style_section_title),
        Spacer(1, 4),
        Paragraph(f"<b>{client_name}</b>", style_body_bold),
        Paragraph("Client Professionnel / Particulier", style_body),
        Paragraph("Adresse : Service Comptabilité / Facturation", style_body),
        Paragraph("France", style_body),
    ]
    
    payment_terms_box = [
        Paragraph("CONDITIONS DE RÈGLEMENT", style_section_title),
        Spacer(1, 4),
        Paragraph("<b>Mode de paiement :</b> Virement bancaire", style_body),
        Paragraph("<b>Délai :</b> 30 jours net", style_body),
        Paragraph("<b>Statut :</b> En attente de paiement", style_body),
    ]
    
    info_table = Table(
        [[client_box, payment_terms_box]],
        colWidths=[9 * cm, 9 * cm]
    )
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (0, 0), 1, BORDER_COLOR),
        ('BOX', (1, 0), (1, 0), 1, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # -------------------------------------------------------------
    # 3. TABLEAU DES ARTICLES / PRESTATIONS
    # -------------------------------------------------------------
    table_data = [
        [
            Paragraph("Désignation de la prestation / Article", style_th),
            Paragraph("Qté", style_th),
            Paragraph("Prix Unit. HT", style_th),
            Paragraph("TVA", style_th),
            Paragraph("Total HT", style_th),
        ],
        [
            Paragraph(
                "<b>Prestation de services & développement sur-mesure</b><br/>"
                "<font color='#6B7280' size='8'>Accompagnement technique, conception d'API & déploiement logiciel</font>",
                style_body
            ),
            Paragraph("1", style_body),
            Paragraph(f"{amount_ht:,.2f} €".replace(",", " ").replace(".", ","), style_body),
            Paragraph(f"{int(vat_rate*100)} %", style_body),
            Paragraph(f"{amount_ht:,.2f} €".replace(",", " ").replace(".", ","), style_body_bold),
        ]
    ]
    
    items_table = Table(table_data, colWidths=[8.5 * cm, 1.5 * cm, 2.8 * cm, 1.8 * cm, 3.4 * cm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 1), (-1, 1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 12),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 15))
    
    # -------------------------------------------------------------
    # 4. BLOC TOTAL / RÉCAPITULATIF FINANCIER (HT, TVA, TTC)
    # -------------------------------------------------------------
    totals_data = [
        [Paragraph("<b>Total Hors Taxes (HT) :</b>", style_body), Paragraph(f"{amount_ht:,.2f} €".replace(",", " ").replace(".", ","), style_body)],
        [Paragraph(f"<b>TVA ({int(vat_rate*100)}%) :</b>", style_body), Paragraph(f"{amount_vat:,.2f} €".replace(",", " ").replace(".", ","), style_body)],
        [
            Paragraph("<b>TOTAL TTC (Net à payer) :</b>", ParagraphStyle('TotalLabel', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.white)), 
            Paragraph(f"<b>{amount_ttc:,.2f} €</b>".replace(",", " ").replace(".", ","), ParagraphStyle('TotalVal', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.white, alignment=2))
        ],
    ]
    
    totals_table = Table(totals_data, colWidths=[5 * cm, 3.5 * cm], hAlign='RIGHT')
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -2), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -2), 5),
        ('BACKGROUND', (0, -1), (-1, -1), PRIMARY_COLOR),
        ('TOPPADDING', (0, -1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
        ('LINEABOVE', (0, 0), (-1, 0), 1, BORDER_COLOR),
    ]))
    
    story.append(totals_table)
    story.append(Spacer(1, 20))
    
    # -------------------------------------------------------------
    # 5. PIED DE PAGE : COORDONNÉES BANCAIRES & MENTIONS LÉGALES
    # -------------------------------------------------------------
    bank_info = [
        Paragraph("<b>COORDONNÉES BANCAIRES POUR LE RÈGLEMENT</b>", style_section_title),
        Spacer(1, 3),
        Paragraph(f"<b>Banque :</b> {BANK['name']}", style_body),
        Paragraph(f"<b>IBAN :</b> {BANK['iban']} — <b>BIC :</b> {BANK['bic']}", style_body),
        Paragraph(f"<b>Référence du virement :</b> {invoice_number}", style_body),
    ]
    
    bank_table = Table([[bank_info]], colWidths=[18 * cm])
    bank_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(bank_table)
    story.append(Spacer(1, 15))
    
    legal_text = (
        "<i>Mentions légales : En cas de retard de paiement, une indemnité forfaitaire pour frais de recouvrement de 40 € "
        "sera exigible (Art. L441-6 du Code de commerce), ainsi que des pénalités au taux légal en vigueur. "
        "Pas d'escompte pour règlement anticipé.</i><br/><br/>"
        "<b>Nous vous remercions de votre confiance !</b>"
    )
    story.append(Paragraph(legal_text, ParagraphStyle('Legal', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=10, textColor=TEXT_MUTED, alignment=1)))
    
    # Génération du document dans le flux binaire
    doc.build(story)
    
    # Repositionner le curseur au début du buffer pour la lecture
    buffer.seek(0)
    return buffer, invoice_number
