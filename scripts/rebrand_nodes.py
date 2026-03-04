import os
from pathlib import Path

def rebrand_dir(dir_path: Path):
    if not dir_path.exists():
        return
        
    for f in dir_path.glob("*.md"):
        with open(f, "r", encoding="utf-8") as file:
            content = file.read()
            
        content = content.replace("Planview", "ClawdView")
        content = content.replace("planview", "clawdview")
        
        with open(f, "w", encoding="utf-8") as file:
            file.write(content)
            
        if "planview" in f.name:
            new_name = f.name.replace("planview", "clawdview")
            f.rename(dir_path / new_name)
            print(f"Renamed and updated {f.name} -> {new_name}")
        else:
            print(f"Updated content in {f.name}")

if __name__ == "__main__":
    base = Path(r"d:\rouca\DVM\workPlace\handoff\skill-graphs")
    rebrand_dir(base / "product")
    rebrand_dir(base / "industry")
    print("Rebranding complete.")
