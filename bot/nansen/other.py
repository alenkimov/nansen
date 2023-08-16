import re
from email.message import Message


PATTERN = re.compile(r'https://getlaunchlist\.com/s/verify/[^\s]*')


def search_verification_link(message: Message) -> str | None:
    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if "attachment" not in content_disposition and content_type == 'text/plain':
                body = part.get_payload(decode=True).decode()
                match = PATTERN.search(body)
                if match:
                    return match.group()
    else:
        # If email is not multipart
        body = message.get_payload(decode=True).decode()
        match = PATTERN.search(body)
        if match:
            return match.group()

    return None
