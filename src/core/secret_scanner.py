import os
from detect_secrets.core.secrets_collection import SecretsCollection
from detect_secrets.settings import transient_settings

def scan_for_secrets(base_dir, files_to_scan):
    """
    Scans a list of files for secrets and returns a formatted report string
    if any are found, otherwise returns None.
    """
    secrets = SecretsCollection()
    # Explicitly configure and enable all default plugins to ensure they run
    # in the packaged environment.
    with transient_settings({
        'plugins_used': [
            {'name': 'ArtifactoryDetector'}, {'name': 'AWSKeyDetector'},
            {'name': 'AzureStorageKeyDetector'}, {'name': 'BasicAuthDetector'},
            {'name': 'CloudantDetector'}, {'name': 'DiscordBotTokenDetector'},
            {'name': 'GitHubTokenDetector'}, {'name': 'GitLabTokenDetector'},
            {'name': 'Base64HighEntropyString', 'limit': 4.5},
            {'name': 'HexHighEntropyString', 'limit': 3.0},
            {'name': 'IbmCloudIamDetector'}, {'name': 'IbmCosHmacDetector'},
            {'name': 'IPPublicDetector'}, {'name': 'JwtTokenDetector'},
            {'name': 'KeywordDetector'}, {'name': 'MailchimpDetector'},
            {'name': 'NpmDetector'}, {'name': 'OpenAIDetector'},
            {'name': 'PrivateKeyDetector'}, {'name': 'PypiTokenDetector'},
            {'name': 'SendGridDetector'}, {'name': 'SlackDetector'},
            {'name': 'SoftlayerDetector'}, {'name': 'SquareOAuthDetector'},
            {'name': 'StripeDetector'}, {'name': 'TelegramBotTokenDetector'},
            {'name': 'TwilioKeyDetector'},
        ]
    }):
        for rel_path in files_to_scan:
            full_path = os.path.join(base_dir, rel_path)
            if os.path.isfile(full_path):
                secrets.scan_file(full_path)

    if not secrets:
        return None

    report_lines = []
    # The collection's .data attribute is a dict we can safely iterate over
    for filename, file_secrets in secrets.data.items():
        if not file_secrets:
            continue

        lines = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception:
            pass # File might be unreadable, but we can still report the finding

        for secret in file_secrets:
            # Use the relative path for cleaner display
            rel_filename = os.path.relpath(secret.filename, base_dir).replace('\\', '/')
            report_line = f"- {rel_filename}:{secret.line_number} ({secret.type})"

            # Get the line content for context
            if lines and 0 < secret.line_number <= len(lines):
                line_content = lines[secret.line_number - 1].strip()
                report_line += f"\n  > {line_content}"
            
            report_lines.append(report_line)

    if not report_lines:
        return None

    # Limit the report to a reasonable number of lines to avoid a giant messagebox
    MAX_LINES_IN_REPORT = 10
    report_string = "\n".join(report_lines[:MAX_LINES_IN_REPORT])
    if len(report_lines) > MAX_LINES_IN_REPORT:
        report_string += f"\n... and {len(report_lines) - MAX_LINES_IN_REPORT} more."

    return report_string