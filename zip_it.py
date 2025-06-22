import zipfile
import os

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        # Skip undesired directories
        if any(ignored in root for ignored in [".git", "venv", "__pycache__"]):
            continue
        for file in files:
            filepath = os.path.join(root, file)
            arcname = os.path.relpath(filepath, path)
            ziph.write(filepath, arcname)

with zipfile.ZipFile("medimind.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
    zipdir(".", zipf)

print("✅ Zip archive created: medimind.zip")
