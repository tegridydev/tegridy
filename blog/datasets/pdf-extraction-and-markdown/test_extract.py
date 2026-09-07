from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
import pytest
from extract import extract, verify


def fixture(path):
    writer = PdfWriter()
    page = writer.add_blank_page(300, 300)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    page[NameObject("/Resources")] = DictionaryObject(
        {
            NameObject("/Font"): DictionaryObject(
                {NameObject("/F1"): writer._add_object(font)}
            )
        }
    )
    content = DecodedStreamObject()
    content.set_data(b"BT /F1 12 Tf 20 250 Td (Price: 12.50) Tj ET")
    page[NameObject("/Contents")] = writer._add_object(content)
    writer.add_blank_page(300, 300)
    writer.write(path)


def test_text_gap_and_integrity(tmp_path):
    p = tmp_path / "fixture.pdf"
    fixture(p)
    out = tmp_path / "out"
    m = extract(p, out)
    assert m["status"] == "partial" and m["page_count"] == 2
    assert "12.50" in m["pages"][0]["blocks"][0]["text"]
    assert m["pages"][1]["status"] == "needs-ocr-or-review"
    assert verify(out)
    (out / "extracted.md").write_text("modified")
    assert not verify(out)
    with pytest.raises(FileExistsError):
        extract(p, out)


def test_optional_ocr_callback_and_review_integrity(tmp_path):
    path=tmp_path/'fixture.pdf';fixture(path);calls=[]
    def ocr(source,page):calls.append(page);return 'Recognised fixture text.'
    output=tmp_path/'review';result=extract(path,output,ocr=ocr,review=True)
    assert calls==[2] and result['status']=='complete-text-extraction-with-ocr'
    assert verify(output)
    (output/'source.pdf').write_bytes(b'changed')
    assert not verify(output)
