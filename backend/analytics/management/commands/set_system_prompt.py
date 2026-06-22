from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from analytics.services.report_prompt_registry import get_report_prompt_registry


class Command(BaseCommand):
    help = "View or update the persisted system prompt template"

    def add_arguments(self, parser):
        parser.add_argument('--show', action='store_true', help='Print the current persisted template')
        parser.add_argument('--file', '-f', help='Path to a file containing the new template')
        parser.add_argument('--text', '-t', help='Template text (use quotes)')

    def handle(self, *args, **options):
        registry = get_report_prompt_registry()
        config = registry.load()
        current = config.get('system_prompt_template')

        if options.get('show') and not (options.get('file') or options.get('text')):
            if current:
                self.stdout.write(current)
                return
            self.stdout.write('<no template persisted>')
            return

        if not options.get('file') and not options.get('text'):
            raise CommandError('Provide --file or --text to update, or --show to view.')

        if options.get('file'):
            path = Path(options.get('file'))
            if not path.exists():
                raise CommandError(f'File not found: {path}')
            new_template = path.read_text(encoding='utf-8')
        else:
            new_template = options.get('text')

        config['system_prompt_template'] = new_template
        registry.save(config)
        self.stdout.write(self.style.SUCCESS(f'Saved system_prompt_template to {registry.config_path}'))
