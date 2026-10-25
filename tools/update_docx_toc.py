"""Replace the handwritten contents with a native, three-level Word TOC."""
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

WORD_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': WORD_NS}
ET.register_namespace('w', WORD_NS)


def word_element(name, **attributes):
    return ET.Element(f'{{{WORD_NS}}}{name}', {f'{{{WORD_NS}}}{key}': value for key, value in attributes.items()})


def paragraph_properties(paragraph):
    properties = paragraph.find('w:pPr', NS)
    if properties is None:
        properties = word_element('pPr')
        paragraph.insert(0, properties)

    return properties


def set_style(*, paragraph, name):
    properties = paragraph_properties(paragraph)
    style = properties.find('w:pStyle', NS)
    if style is None:
        style = ET.SubElement(properties, f'{{{WORD_NS}}}pStyle')

    style.set(f'{{{WORD_NS}}}val', name)


def update_toc(path):
    with ZipFile(path) as archive:
        entries = [(item, archive.read(item.filename)) for item in archive.infolist()]

    parts = {item.filename: content for item, content in entries}
    document = ET.fromstring(parts['word/document.xml'])
    body = document.find('w:body', NS)
    existing = document.findall('.//w:instrText', NS)
    if any('TOC ' in (element.text or '') for element in existing):
        return False

    paragraphs = body.findall('w:p', NS)
    contents_heading = next(paragraph for paragraph in paragraphs if ''.join(paragraph.itertext()).casefold() in ['daftar isi', 'table of contents'])
    heading_index = list(body).index(contents_heading)
    for paragraph in paragraphs:
        style = paragraph.find('w:pPr/w:pStyle', NS)
        if style is None:
            continue

        old_name = style.get(f'{{{WORD_NS}}}val')
        replacements = {'Heading1': 'Title', 'Heading2': 'Heading1', 'Heading3': 'Heading2', 'Heading4': 'Heading3'}
        if old_name in replacements:
            set_style(paragraph=paragraph, name=replacements[old_name])

    set_style(paragraph=contents_heading, name='TOCHeading')
    ET.SubElement(paragraph_properties(contents_heading), f'{{{WORD_NS}}}pageBreakBefore')
    removed = 0
    for element in list(body)[heading_index+1:]:
        style = element.find('w:pPr/w:pStyle', NS)
        is_section_heading = style is not None and style.get(f'{{{WORD_NS}}}val') == 'Heading1'
        if is_section_heading:
            ET.SubElement(paragraph_properties(element), f'{{{WORD_NS}}}pageBreakBefore')
            break

        if element.tag == f'{{{WORD_NS}}}p':
            body.remove(element)
            removed += 1

    assert removed > 0, 'Expected manual contents entries to replace.'
    for table in document.findall('.//w:tbl', NS):
        table_properties = table.find('w:tblPr', NS)
        if table_properties is None:
            table_properties = word_element('tblPr')
            table.insert(0, table_properties)

        old_borders = table_properties.find('w:tblBorders', NS)
        if old_borders is not None:
            table_properties.remove(old_borders)

        borders = ET.SubElement(table_properties, f'{{{WORD_NS}}}tblBorders')
        for edge in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
            borders.append(word_element(edge, val='single', sz='6', space='0', color='000000'))

        for cell in table.findall('.//w:tc', NS):
            cell_properties = cell.find('w:tcPr', NS)
            if cell_properties is None:
                cell_properties = word_element('tcPr')
                cell.insert(0, cell_properties)

            old_borders = cell_properties.find('w:tcBorders', NS)
            if old_borders is not None:
                cell_properties.remove(old_borders)

            borders = ET.SubElement(cell_properties, f'{{{WORD_NS}}}tcBorders')
            for edge in ['top', 'left', 'bottom', 'right']:
                borders.append(word_element(edge, val='single', sz='6', space='0', color='000000'))

    toc = word_element('sdt')
    properties = ET.SubElement(toc, f'{{{WORD_NS}}}sdtPr')
    part = ET.SubElement(properties, f'{{{WORD_NS}}}docPartObj')
    part.append(word_element('docPartGallery', val='Table of Contents'))
    part.append(word_element('docPartUnique'))
    content = ET.SubElement(toc, f'{{{WORD_NS}}}sdtContent')
    paragraph = ET.SubElement(content, f'{{{WORD_NS}}}p')
    set_style(paragraph=paragraph, name='TOC1')
    run = ET.SubElement(paragraph, f'{{{WORD_NS}}}r')
    run.append(word_element('fldChar', fldCharType='begin', dirty='true'))
    instruction = ET.SubElement(ET.SubElement(paragraph, f'{{{WORD_NS}}}r'), f'{{{WORD_NS}}}instrText')
    instruction.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    instruction.text = ' TOC \\o "1-3" \\h \\z \\u '
    ET.SubElement(paragraph, f'{{{WORD_NS}}}r').append(word_element('fldChar', fldCharType='separate'))
    ET.SubElement(ET.SubElement(paragraph, f'{{{WORD_NS}}}r'), f'{{{WORD_NS}}}t').text = 'Perbarui daftar isi di Microsoft Word untuk menampilkan nomor halaman.'
    ET.SubElement(paragraph, f'{{{WORD_NS}}}r').append(word_element('fldChar', fldCharType='end'))
    body.insert(heading_index+1, toc)

    styles = ET.fromstring(parts['word/styles.xml'])
    for name, level in [('TOCHeading', 0), ('TOC1', 0), ('TOC2', 1), ('TOC3', 2)]:
        style = styles.find(f'w:style[@w:styleId="{name}"]', NS)
        if style is None:
            style = word_element('style', type='paragraph', styleId=name)
            style.append(word_element('name', val='TOC Heading' if name == 'TOCHeading' else f'toc {level+1}'))
            style.append(word_element('basedOn', val='Normal'))
            styles.append(style)

        props = style.find('w:pPr', NS)
        if props is None:
            props = ET.SubElement(style, f'{{{WORD_NS}}}pPr')

        if name == 'TOCHeading':
            props.append(word_element('outlineLvl', val='9'))
            continue

        for child in list(props):
            if child.tag in [f'{{{WORD_NS}}}tabs', f'{{{WORD_NS}}}ind']:
                props.remove(child)

        section = body.find('w:sectPr', NS)
        page_size, margins = section.find('w:pgSz', NS), section.find('w:pgMar', NS)
        if page_size is None:
            page_size = word_element('pgSz', w='11906', h='16838')
            section.append(page_size)

        if margins is None:
            margins = word_element('pgMar', top='1440', bottom='1440', left='1440', right='1440', header='720', footer='720', gutter='0')
            section.append(margins)

        content_width = int(page_size.get(f'{{{WORD_NS}}}w')) - int(margins.get(f'{{{WORD_NS}}}left')) - int(margins.get(f'{{{WORD_NS}}}right'))
        tabs = ET.SubElement(props, f'{{{WORD_NS}}}tabs')
        tabs.append(word_element('tab', val='right', leader='dot', pos=str(content_width)))
        props.append(word_element('ind', left=str(level*240)))

    settings = ET.fromstring(parts['word/settings.xml'])
    update = settings.find('w:updateFields', NS)
    if update is None:
        update = ET.SubElement(settings, f'{{{WORD_NS}}}updateFields')

    update.set(f'{{{WORD_NS}}}val', 'true')
    for name, root in [('document', document), ('styles', styles), ('settings', settings)]:
        parts[f'word/{name}.xml'] = ET.tostring(root, encoding='utf-8', xml_declaration=True)

    temporary = path.with_suffix('.toc.docx')
    with ZipFile(temporary, 'w') as archive:
        for item, original in entries:
            archive.writestr(item, parts[item.filename])

    temporary.replace(path)
    return True


if __name__ == '__main__':
    import sys
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'docs/BRD-perpus-merah-putih.docx'
    print('Native Word TOC inserted.' if update_toc(path) else 'Native Word TOC already present.')
