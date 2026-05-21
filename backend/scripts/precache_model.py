"""Pre-cache sentence-transformers model at build time (best-effort).

This script is called from the Dockerfile to avoid long inline `python -c` lines
that can show as red or cause quoting issues in some editors/linters.
"""

def main():
    try:
        import importlib
        importlib.import_module('sentence_transformers')
        from sentence_transformers import SentenceTransformer
        # Attempt to load model (best-effort); failures are non-fatal
        SentenceTransformer('all-MiniLM-L6-v2')
        print('SentenceTransformer model cached')
    except Exception as exc:
        print(f'Precache model skipped: {exc}')


if __name__ == '__main__':
    main()
