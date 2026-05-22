MAX_QUERY_LENGTH = int(__import__('os').environ.get('MAX_QUERY_LENGTH', '5000'))
MAX_QUERY_ROWS = int(__import__('os').environ.get('MAX_QUERY_ROWS', '500'))
QUERY_TIMEOUT_SECONDS = int(__import__('os').environ.get('QUERY_TIMEOUT_SECONDS', '10'))

BLOCKED_KEYWORDS = {
    'insert', 'update', 'delete', 'drop', 'alter', 'truncate', 'exec', 'merge', 'grant', 'revoke', 'create'
}

ALLOWED_STATEMENTS = {'select', 'with'}
