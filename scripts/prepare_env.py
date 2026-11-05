from pathlib import Path
import secrets

root = Path(__file__).resolve().parents[1]
template = (root / '.env.example').read_text(encoding='utf-8')
replacements = {
    'CHANGE_ME_WITH_AT_LEAST_64_RANDOM_CHARS': secrets.token_urlsafe(64),
    'CHANGE_ME_WITH_AT_LEAST_48_RANDOM_CHARS': secrets.token_urlsafe(48),
    'CHANGE_ME_POSTGRES_PASSWORD': secrets.token_urlsafe(32),
    'CHANGE_ME_MQTT_PASSWORD': secrets.token_urlsafe(32),
}
for old, new in replacements.items():
    template = template.replace(old, new)
(root / '.env').write_text(template, encoding='utf-8')
print('Created .env with random secrets.')
print('Do not commit or share .env.')
