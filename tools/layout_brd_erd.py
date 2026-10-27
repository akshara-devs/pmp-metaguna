"""Place the combined ERD on its own landscape sheet in the Word BRD."""
from copy import deepcopy
from zipfile import ZipFile

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W, 'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing', 'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}


def layout_erd(path):
    from lxml import etree as ET

    with ZipFile(path) as archive:
        entries = [(item, archive.read(item.filename)) for item in archive.infolist()]

    parts = {item.filename: content for item, content in entries}
    document = ET.fromstring(parts['word/document.xml'])
    body = document.find('w:body', NS)
    image_paragraph = next(p for p in body.findall('w:p', NS) if p.find('.//w:drawing', NS) is not None)
    previous = image_paragraph.getprevious()
    portrait = body.find('w:sectPr', NS)

    def properties(paragraph):
        props = paragraph.find('w:pPr', NS)
        if props is None:
            props = ET.Element(f'{{{W}}}pPr')
            paragraph.insert(0, props)

        return props

    def section_break(section):
        result = deepcopy(section)
        kind = result.find('w:type', NS)
        if kind is None:
            kind = ET.SubElement(result, f'{{{W}}}type')

        kind.set(f'{{{W}}}val', 'nextPage')
        return result

    properties(previous).append(section_break(portrait))
    landscape = section_break(portrait)
    size = landscape.find('w:pgSz', NS)
    # A3 provides room for every attribute and twelve relationships on one sheet.
    size.set(f'{{{W}}}w', '23811')
    size.set(f'{{{W}}}h', '16838')
    size.set(f'{{{W}}}orient', 'landscape')
    margins = landscape.find('w:pgMar', NS)
    for edge in ['top', 'right', 'bottom', 'left']:
        margins.set(f'{{{W}}}{edge}', '720')

    properties(image_paragraph).append(landscape)
    properties(image_paragraph).append(ET.Element(f'{{{W}}}keepNext', {f'{{{W}}}val': '0'}))
    properties(image_paragraph).append(ET.Element(f'{{{W}}}spacing', {f'{{{W}}}before': '0', f'{{{W}}}after': '0'}))
    extent = image_paragraph.find('.//wp:extent', NS)
    width, height = int(extent.get('cx')), int(extent.get('cy'))
    scale = min(14.8 * 914400 / width, 9.8 * 914400 / height)
    dimensions = {'cx': str(round(width * scale)), 'cy': str(round(height * scale))}
    extent.attrib.update(dimensions)
    for transform in image_paragraph.findall('.//a:xfrm/a:ext', NS):
        transform.attrib.update(dimensions)

    parts['word/document.xml'] = ET.tostring(document, xml_declaration=True, encoding='UTF-8', standalone=True)
    with ZipFile(path, 'w') as archive:
        for item, content in entries:
            archive.writestr(item, parts[item.filename])


def restore_pdf_sheet(path):
    """Restore the A3 bounds when Word for macOS exports using A4 paper."""
    from pypdf import PdfReader, PdfWriter, Transformation
    from pypdf.generic import RectangleObject

    reader = PdfReader(path)
    writer = PdfWriter()
    for page in reader.pages:
        if page.images:
            width, height = 23811 / 20, 16838 / 20
            original_height = float(page.mediabox.height)
            if original_height < height - 1:
                page.add_transformation(Transformation().translate(ty=(height - original_height) / 2))
                page.mediabox = RectangleObject([0, 0, width, height])
                page.cropbox = RectangleObject([0, 0, width, height])

        writer.add_page(page)

    if reader.metadata:
        writer.add_metadata(reader.metadata)

    with path.open('wb') as target:
        writer.write(target)


if __name__ == '__main__':
    from pathlib import Path

    restore_pdf_sheet(Path(__file__).resolve().parents[1] / 'docs/BRD-perpus-merah-putih.pdf')
