#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from threading import Thread


def start_bot():
    bot_script_path = os.path.join(os.path.dirname(__file__), 'telegram_bot', 'telegram_bot.py')
    os.system(f'python {bot_script_path}')


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_exchange.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    if sys.argv[1] == 'runserver' and os.environ.get('RUN_MAIN') == 'true':
        Thread(target=start_bot).start()

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
