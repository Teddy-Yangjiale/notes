"""Package the editable pptdraw sources after generating and reviewing figures."""
from pathlib import Path
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'scripts/cs184-course-sources.json').read_text(encoding='utf8'))
    out = ROOT / 'public/cs184/figures'
    out.mkdir(parents=True, exist_ok=True)
    for course in manifest:
        key = course['key']
        folder = ROOT / '.work/cs184/editable' / key
        slides = sorted(folder.glob('*.pptx'))
        assert len(slides) == 24, (key, len(slides))
        with zipfile.ZipFile(out / f'{key}-editable.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
            for slide in slides:
                spec = slide.with_suffix('.json')
                assert spec.is_file(), spec
                archive.write(slide, slide.name)
                archive.write(spec, spec.name)
            archive.writestr('README.txt',
                'CS184 editable teaching diagrams\n'
                'Each PPTX contains native PowerPoint shapes, labels and connectors.\n'
                'The corresponding JSON is the pptdraw operation source.\n'
                'Figure explanations appear in the course notes and slide speaker notes.\n'
                'These are original teaching diagrams, not the Berkeley lecture slides.\n')
        print(key, '24 editable figures packaged')


if __name__ == '__main__':
    main()
