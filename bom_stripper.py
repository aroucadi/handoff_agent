import os

# Binary sequence for UTF-8 BOM
BOM = b'\xef\xbb\xbf'
# Extensions to check
EXTS = ('.py', '.sh', '.ps1', '.md', '.html', '.tsx', '.ts', '.yaml', '.yml', '.tf', '.json', '.txt', '.css')

def clean_bom(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        if BOM in data:
            print(f"Cleaning BOM from {filepath}")
            cleaned_data = data.replace(BOM, b'')
            with open(filepath, 'wb') as f:
                f.write(cleaned_data)
            return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return False

print("Starting deep BOM cleanup...")
count = 0
for root, dirs, files in os.walk('.'):
    # Skip noisy/large directories
    if any(p in root for p in ['.git', 'node_modules', '__pycache__', 'dist', '.terraform', '.firebase']):
        continue
        
    for f in files:
        if f.endswith(EXTS):
            if clean_bom(os.path.join(root, f)):
                count += 1

print(f"Cleanup complete. Total files cleaned: {count}")
