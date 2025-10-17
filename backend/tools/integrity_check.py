#!/usr/bin/env python3
"""Quick repository integrity check for the Driver Logbook project.

This script performs a subset of the manual checks in the audit: env presence/keys, migrations folder,
Django settings sanity, frontend API usage and a simple cross-check.

Run from repository root: python tools/integrity_check.py --quick
"""
import re
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent.parent

def read_env(path):
    if not path.exists():
        return None
    lines = path.read_text().splitlines()
    pairs = {}
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        if '=' in ln:
            k, v = ln.split('=', 1)
            pairs[k.strip()] = v.strip()
    return pairs


def find_keys(env_dict):
    if not env_dict:
        return []
    return list(env_dict.keys())


def secrets_in_env(env_dict):
    if not env_dict:
        return []
    secret_keys = []
    for k, v in env_dict.items():
        if any(tok in k.upper() for tok in ['KEY','SECRET','PASSWORD','TOKEN','SECRET_KEY']):
            if v and v != '':
                secret_keys.append((k, v))
    return secret_keys


def main():
    results = { 'errors': [], 'warnings': [], 'info': [] }

    # 1. env files
    backend_env = read_env(ROOT / 'backend' / '.env')
    root_env = read_env(ROOT / '.env')
    backend_env_example = read_env(ROOT / 'backend' / '.env.example')
    root_env_example = read_env(ROOT / '.env.example')

    results['info'].append(('backend_env_present', bool(backend_env)))
    results['info'].append(('root_env_present', bool(root_env)))

    # required backend keys
    required_backend_keys = ['DEBUG','DJANGO_SECRET_KEY','ALLOWED_HOSTS','DB_NAME','DB_USER','DB_PASSWORD','DB_HOST','DB_PORT','CORS_ALLOWED_ORIGINS']
    missing = [k for k in required_backend_keys if not (backend_env and k in backend_env)]
    if missing:
        results['errors'].append(('missing_backend_env_keys', missing))

    # root vite key
    if not (root_env and 'VITE_API_BASE_URL' in root_env):
        results['warnings'].append(('missing_root_vite_key', True))

    # secrets exposed
    be_secrets = secrets_in_env(backend_env)
    root_secrets = secrets_in_env(root_env)
    if be_secrets:
        results['errors'].append(('backend_secrets_exposed', [k for k,_ in be_secrets]))
    if root_secrets:
        results['errors'].append(('root_secrets_exposed', [k for k,_ in root_secrets]))

    # 2. check migrations
    migrations_dir = ROOT / 'backend' / 'logbook' / 'migrations'
    if not migrations_dir.exists() or not any(migrations_dir.glob('*.py')):
        results['errors'].append(('missing_migrations', str(migrations_dir)))

    # 3. settings
    settings_path = ROOT / 'backend' / 'config' / 'settings.py'
    if settings_path.exists():
        settings_text = settings_path.read_text()
        installed_apps = re.search(r"INSTALLED_APPS\s*=\s*\[(.*?)\]", settings_text, re.S)
        if installed_apps:
            apps_list = re.findall(r"'([^']+)'", installed_apps.group(1))
            results['info'].append(('installed_apps', apps_list))
            if 'logbook' not in apps_list:
                results['errors'].append(('logbook_not_in_installed_apps', True))
        db_config = re.search(r"'default'\s*:\s*\{(.*?)\}\n\s*\}", settings_text, re.S)
        if db_config:
            engine = re.search(r"'ENGINE'\s*:\s*'([^']+)'", db_config.group(1))
            if engine:
                results['info'].append(('db_engine', engine.group(1)))

    # 4. backend urls and router
    logbook_urls = ROOT / 'backend' / 'logbook' / 'urls.py'
    backend_urls = ROOT / 'backend' / 'config' / 'urls.py'
    api_paths = []
    custom_paths = []
    if logbook_urls.exists():
        txt = logbook_urls.read_text()
        # router.register(r'drivers', DriverViewSet, ...)
        regs = re.findall(r"router\.register\(r?'([^']+)'", txt)
        api_paths.extend(regs)
        # explicit paths
        eps = re.findall(r"path\('\s*([^']+)'\s*,", txt)
        custom_paths.extend(eps)
        results['info'].append(('logbook_registered_routers', regs))
        results['info'].append(('logbook_custom_paths', eps))

    # 5. frontend API usage
    client = ROOT / 'src' / 'api' / 'client.ts'
    frontend_paths = set()
    api_base = None
    if client.exists():
        ctext = client.read_text()
        m = re.search(r"VITE_API_BASE_URL\s*=\s*import\.meta\.env\.VITE_API_BASE_URL\s*\|\|\s*'([^']+)'", ctext)
        if m:
            api_base = m.group(1)
        endpoints = re.findall(r"get<[^>]*>\('\s*([^']+)'\s*\)|post\('\s*([^']+)'\s*|post\(`/([^`]+)`", ctext)
        # simpler: search across src for apiClient.get/post with strings
    from glob import glob
    for p in glob(str(ROOT / 'src' / '**' / '*.tsx'), recursive=True):
        text = Path(p).read_text()
        for m in re.findall(r"apiClient\.(?:get|post|put|patch|delete)\(\s*`?\'?(\/[^'`\"]+)\'?'?", text):
            frontend_paths.add(m)
    # also look for template literals
    for p in glob(str(ROOT / 'src' / '**' / '*.tsx'), recursive=True):
        text = Path(p).read_text()
        for m in re.findall(r"apiClient\.(?:get|post|put|patch|delete)\(\s*`(/[^`]+)`", text):
            frontend_paths.add(m)

    results['info'].append(('frontend_api_base_default', api_base))
    results['info'].append(('frontend_paths_sample', list(frontend_paths)[:20]))

    # cross-check naive
    missing_routes = []
    for p in frontend_paths:
        seg = p.split('/')[1] if p.startswith('/') and len(p.split('/'))>1 else None
        if seg and seg not in api_paths and seg not in ['auth','dashboard']:
            missing_routes.append(p)
    if missing_routes:
        results['warnings'].append(('frontend_paths_without_matching_router', missing_routes))

    # print a JSON-ish summary
    print('\n=== Quick integrity check summary ===\n')
    print(json.dumps(results, indent=2))

    # exit non-zero if critical errors found
    critical = [e for e in results['errors'] if e[0] in ('backend_secrets_exposed','root_secrets_exposed','missing_migrations','missing_backend_env_keys')]
    if critical:
        print('\nFound critical issues. Please address the errors above.')
        sys.exit(2)
    print('\nNo critical issues detected by quick script. Review warnings and info.')
    sys.exit(0)

if __name__ == '__main__':
    main()
