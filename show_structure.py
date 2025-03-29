import os

# Define folders and files to ignore
IGNORED = {'.git', '__pycache__', '.DS_Store', '.venv', '.idea', '.vscode', '.ipynb_checkpoints'}


def print_structure(start_path='.', indent=''):
    for item in sorted(os.listdir(start_path)):
        if item.startswith('.') or item in IGNORED:
            continue
        path = os.path.join(start_path, item)
        if os.path.isdir(path):
            print(f"{indent}📁 {item}/")
            print_structure(path, indent + '    ')
        else:
            print(f"{indent}📄 {item}")


if __name__ == "__main__":
    print("📦 Project Directory Structure\n")
    print_structure()
