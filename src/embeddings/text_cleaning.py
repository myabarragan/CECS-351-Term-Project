import re
import html
from typing import Optional

def strip_html(raw_text: Optional[str]) -> str:
    #remov HTML tags and decode HTML entities

    if not raw_text:
        return ""

    text = html.unescape(raw_text)

    #remove script/style blocks

    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", text)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)

    #replace HTML tags with spaces

    text = re.sub(r"(?s)<[^>]+>", " ", text)

    return normalize_whitespace(text)


def remove_reply_chain(text: Optional[str]) -> str:

    #remove common email rply/forward chains to keep only the main message

    if not text:
        return ""

    patterns = [
        r"(?im)^On .* wrote:$",
        r"(?im)^From: .*$",
        r"(?im)^Sent: .*$",
        r"(?im)^To: .*$",
        r"(?im)^Subject: .*$",
        r"(?im)^-+\s*Original Message\s*-+$",
        r"(?im)^Begin forwarded message:$",
    ]

    lines = text.splitlines()
    cutoff_index = len(lines)

    for i, line in enumerate(lines):
        for pattern in patterns:
            if re.match(pattern, line.strip()):
                cutoff_index = min(cutoff_index, i)
                break

    cleaned = "\n".join(lines[:cutoff_index])
    return cleaned.strip()


def remove_signature(text: Optional[str]) -> str:
    #remove common email signatures

    if not text:
        return ""

    signature_markers = [
        r"(?im)^best,\s*$",
        r"(?im)^best regards,\s*$",
        r"(?im)^regards,\s*$",
        r"(?im)^thanks,\s*$",
        r"(?im)^thank you,\s*$",
        r"(?im)^sincerely,\s*$",
        r"(?im)^cheers,\s*$",
    ]

    lines = text.splitlines()
    cutoff_index = len(lines)

    for i, line in enumerate(lines):
        for marker in signature_markers:
            if re.match(marker, line.strip()):
                cutoff_index = min(cutoff_index, i)
                break

    cleaned = "\n".join(lines[:cutoff_index])
    return cleaned.strip()


def normalize_whitespace(text: Optional[str]) -> str:
    #collapse repeated whitespace/newlines into clean text

    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_email_body(body: Optional[str]) -> str:
    #full email cleaning pipeline

    text = strip_html(body)
    text = remove_reply_chain(text)
    text = remove_signature(text)
    text = normalize_whitespace(text)
    return text


def build_email_document(email: dict) -> str:
    #convert one email record into a single searchable doc string

    subject = normalize_whitespace(email.get("subject", ""))
    sender = normalize_whitespace(email.get("sender", ""))
    date = normalize_whitespace(email.get("date", ""))
    body = clean_email_body(email.get("body", ""))

    parts = [
        f"Subject: {subject}",
        f"From: {sender}",
        f"Date: {date}",
        f"Body: {body}",
    ]

    return "\n".join(parts).strip()


def create_snippet(text: Optional[str], max_length: int = 220) -> str:

    #create a short preview snippet for UI/API responses

    text = normalize_whitespace(text or "")
    if len(text) <= max_length:
        return text
    return text[: max_length - 3].rstrip() + "..."