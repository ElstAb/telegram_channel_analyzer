def to_markdown(messages):

    blocks = []

    for m in messages:
        reply = m.get("reply")
        reply_block = ""
        if isinstance(reply, dict) and (reply.get("text") or reply.get("author") or reply.get("author_id")):
            reply_block = f"""
Reply to:
- Message id: {reply.get('message_id')}
- Author: {reply.get('author')} (id: {reply.get('author_id')})
- Date: {reply.get('date')}
- Text: {reply.get('text')}
"""

        block = f"""
### {m['date']}

Message id: {m.get('message_id')}
Reply to message id: {m.get('reply_to_id')}

Author: {m['author']} (id: {m.get('author_id')})
{reply_block}

{m['text']}
"""

        blocks.append(block)

    return "\n".join(blocks)