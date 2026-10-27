"""Build the complete, editable ERD for the FigCraft page and BRD."""
from build_documents import MODEL, OUT, connector, entity, svg_page

SLUG = '01-erd-lengkap'
TITLE = 'Complete ERD · Perpus Merah Putih'


def build_combined_erd():
    nodes = [
        ('categories', 70, 190),
        ('books', 70, 450),
        ('users', 70, 900),
        ('lending_policies', 710, 190),
        ('loan_requests', 710, 650),
        ('loans', 1350, 190),
        ('fines', 1350, 900),
    ]
    routes = [
        ([(270, 336), (270, 450)], (360, 397)),
        ([(470, 570), (600, 570), (600, 780), (710, 780)], (600, 690)),
        ([(470, 970), (710, 970)], (590, 944)),
        ([(1110, 730), (1240, 730), (1240, 310), (1350, 310)], (1240, 600)),
        ([(1570, 492), (1570, 900)], (1650, 700)),
        ([(210, 900), (210, 820), (550, 820), (550, 310), (710, 310)], (615, 285)),
        ([(820, 440), (820, 650)], (905, 550)),
        ([(1110, 270), (1350, 270)], (1230, 244)),
        ([(470, 1050), (650, 1050), (650, 1080), (800, 1080), (800, 1004)], (760, 1110)),
        ([(470, 1010), (510, 1010), (510, 1250), (1200, 1250), (1200, 390), (1350, 390)], (1060, 1225)),
        ([(470, 1090), (540, 1090), (540, 1300), (1280, 1300), (1280, 430), (1350, 430)], (1060, 1328)),
        ([(270, 1150), (270, 1360), (1550, 1360), (1550, 1202)], (1550, 1400)),
    ]
    content = ''
    labels = []
    for relation, (points, label_at) in zip(MODEL['relations'], routes, strict=True):
        parent, child, fk, parent_kind, child_kind, label = relation
        route = connector(points=points, parent_kind=parent_kind, child_kind=child_kind, label=fk, label_at=label_at)
        strokes, label = route.rsplit('<rect ', 1)
        content += strokes
        labels.append('<rect ' + label)

    content += ''.join(labels)

    for key, x, y in nodes:
        rendered, height = entity(key=key, x=x, y=y, width=400)
        content += rendered

    svg = svg_page(
        slug=SLUG, title=TITLE,
        subtitle="7 tables · 12 relationships · Crow's Foot · PK / FK / UK · ? = nullable",
        width=1820, height=1570, content=content,
        notes='One physical book per ISBN. Policies are versioned. Staff foreign keys reference LIBRARIAN users.',
    )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f'{SLUG}.svg').write_text(svg)
    (OUT / f'{SLUG}.html').write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><title>{TITLE}</title><body style="margin:0"><div style="overflow-x:auto">{svg}</div></body></html>')


if __name__ == '__main__':
    build_combined_erd()
