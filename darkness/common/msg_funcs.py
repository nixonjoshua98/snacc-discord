
def get_message_text(ctx):
    msg = ctx.message.content
    prefix_used = ctx.prefix
    alias_used = ctx.invoked_with

    return msg[len(prefix_used) + len(alias_used):]
