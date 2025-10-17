"""
打包爬虫组件并生成 manifest.json
运行：python tools/tools_build_scraper_bundle.py
"""
import os
import json
import zipfile
from datetime import datetime

FILES = [
    "scrapers/__init__.py",
    "scrapers/amazon_scraper.py",
    "scrapers/proxy_manager.py",
    "scrapers/storage_manager.py",
    "scrapers/logger.py",
    "core/data_fetcher.py",
    "ui/amazon_crawl_options.py",
    "run_launcher.py",
]

def build_zip(output="scraper_bundle.zip"):
    missing = []
    manifest = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "files": [],
        "missing": []
    }
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
        for f in FILES:
            if os.path.exists(f):
                z.write(f)
                manifest["files"].append(f)
            else:
                print(f"[WARN] 缺失文件: {f}")
                missing.append(f)
        manifest["missing"] = missing
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"[OK] 打包完成: {output} 有效={len(manifest['files'])} 缺失={len(missing)}")

if __name__ == "__main__":
    build_zip()