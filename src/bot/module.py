from handlers import common


def mount(bot):
    """
    Mounting entry point for the project
    """
    common.mount(bot)

    print('Bot started!\n')
