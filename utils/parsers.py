import pdfplumber, docx, extract_msg
from email import policy
from email.parser import BytesParser

def extract_text(path):
    if path.endswith(".pdf"):
        with pdfplumber.open(path) as pdf:
            return "\n".join(p.page.extract_text() or "" for p in pdf.pages)
    elif path.endswith(".docx"):
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    elif path.endswith(".msg"):
        msg = extract_msg.Message(path)
        return msg.body
    elif path.endswith(".eml"):
        with open(path, "rb") as f:
            msg = BytesParser(policy=policy.default).parse(f)
            return msg.get_body().get_content()
    elif path.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError("Unsupported file type")
