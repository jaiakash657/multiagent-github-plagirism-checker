# workers/tasks.py

import os
import sys
import shutil
import stat

# ------------------------------------------------------
# Make backend/ the project root
# ------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from celery import shared_task
from config.logger import logger
from core.orchestrator import Orchestrator
from storage.file_manager import save_repo_temp
from storage.db import get_simhash_candidates
from reports.report_generator import ReportGenerator


# ------------------------------------------------------
# WINDOWS-SAFE DELETE FUNCTION
# ------------------------------------------------------
def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def force_delete_folder(path: str):
    if os.path.exists(path):
        try:
            shutil.rmtree(path, onerror=remove_readonly)
            return True
        except Exception as e:
            logger.error(f"[HARD DELETE FAILED] {e}")
            return False
    return True


# ------------------------------------------------------
# Clone repo helper
# ------------------------------------------------------
def clone_repo(repo_url: str, depth: int = 1) -> str:
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    temp_dir = save_repo_temp(repo_name)

    if os.path.exists(temp_dir):
        force_delete_folder(temp_dir)

    os.makedirs(temp_dir, exist_ok=True)

    cmd = f"git clone {repo_url} {temp_dir} --depth {depth}"
    if os.system(cmd) != 0:
        logger.error(f"[CLONE FAILED] {repo_url}")
        return None

    return temp_dir


# ------------------------------------------------------
# Candidate repos (PostgreSQL)
# ------------------------------------------------------
def get_github_candidates(limit=10):
    """
    Fetch candidate repos based on stored fingerprints
    """
    rows = get_simhash_candidates(limit=limit)
    return [r["repo_url"] for r in rows]


# ------------------------------------------------------
# MAIN CELERY TASK
# ------------------------------------------------------
@shared_task(bind=True)
def analyze_repository_task(self, repo_url: str, depth: int = 1):

    logger.info(f"\n===== [TASK START] {repo_url} =====")

    # 1️⃣ Clone input repo
    input_dir = clone_repo(repo_url, depth)
    if not input_dir:
        return {"error": "Failed to clone input repository"}

    # 2️⃣ Fetch candidates from PostgreSQL
    candidates = get_github_candidates(limit=10)
    candidates = [c for c in candidates if c != repo_url]

    # ✅ BOOTSTRAP: if DB empty, compare repo with itself once
    if not candidates:
        logger.info("[BOOTSTRAP] No candidates found, seeding with input repo")
        candidates = [repo_url]

    repo_paths = {repo_url: input_dir}

    # 3️⃣ Clone candidate repos
    for cand_url in candidates:
        cand_dir = clone_repo(cand_url, depth=1)
        if cand_dir:
            repo_paths[cand_url] = cand_dir

    logger.info(f"[TASK] Total repos analyzed: {len(repo_paths)}")

    # 4️⃣ Run orchestrator
    orchestrator = Orchestrator()
    result = orchestrator.run_multiple(repo_paths)

    # 5️⃣ Generate report
    report_path = os.path.join(input_dir, "report.html")

    ReportGenerator().generate(
        report_data={
            "input_repo": repo_url,
            "top_3_repos": result["top_3_repos"],
            "all_repo_scores": result["all_repo_scores"],
        },
        output_path=report_path,
    )

    # 6️⃣ Cleanup input repo
    force_delete_folder(input_dir)

    logger.info(f"===== [TASK DONE] {repo_url} =====")

    return {
        "input_repo": repo_url,
        "top_3_repos": result["top_3_repos"],
        "all_repo_scores": result["all_repo_scores"],
        "report_path": report_path,
        "status": "completed",
    }
