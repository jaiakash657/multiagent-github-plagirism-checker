import os
import sys
import shutil
import tempfile
import stat

# Make backend/ the project root
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from celery import shared_task
from config.logger import logger
from core.orchestrator import Orchestrator
from storage.file_manager import save_repo_temp, delete_repo_temp
from storage.db import init_db, get_all_repos
from fingerprinting.manager import compute_fingerprints_for_repo
from reports.report_generator import ReportGenerator


# ------------------------------------------------------
# WINDOWS-SAFE DELETE FUNCTION (fixes Access Denied)
# ------------------------------------------------------
def remove_readonly(func, path, _):
    """Make read-only files writable before deleting."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def force_delete_folder(path: str):
    """Delete folder safely on Windows, even when .git files are locked."""
    if os.path.exists(path):
        try:
            shutil.rmtree(path, onerror=remove_readonly)
            return True
        except Exception as e:
            logger.error(f"[HARD DELETE FAILED] {e}")
            return False
    return True


# ------------------------------------------------------
# Helper: Clone repo (with AUTO DELETE)
# ------------------------------------------------------
def clone_repo(repo_url: str, depth: int = 1) -> str:
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    temp_dir = save_repo_temp(repo_name)

    # -----------------------------------
    # AUTO-DELETE OLD REPO safely
    # -----------------------------------
    if os.path.exists(temp_dir):
        logger.info(f"[CLEANUP] Removing old directory: {temp_dir}")

        success = force_delete_folder(temp_dir)
        if not success:
            logger.error(f"[CLEANUP FAILED] Could not delete: {temp_dir}")
            return None

        os.makedirs(temp_dir, exist_ok=True)

    # -----------------------------------
    # CLONE FRESH
    # -----------------------------------
    cmd = f"git clone {repo_url} {temp_dir} --depth {depth}"
    result = os.system(cmd)

    if result != 0:
        logger.error(f"[CLONE] Failed to clone: {repo_url}")
        return None

    return temp_dir


# ------------------------------------------------------
# Get list of candidate repos from DB
# ------------------------------------------------------
def get_github_candidates(limit=10):
    rows = get_all_repos()
    urls = [r["repo_url"] for r in rows]
    return urls[:limit]


# ------------------------------------------------------
# MAIN TASK
# ------------------------------------------------------
@shared_task(bind=True)
def analyze_repository_task(self, repo_url: str, depth: int = 1):

    logger.info(f"\n\n===== [TASK START] Analyzing: {repo_url} =====")

    init_db()  # safe multi-call

    # --------------------------------------------------
    # 1️⃣ Clone input repo
    # --------------------------------------------------
    input_dir = clone_repo(repo_url, depth=depth)
    if not input_dir:
        return {"error": "Failed to clone input repository"}

    logger.info(f"[TASK] Input repo cloned at: {input_dir}")

    # --------------------------------------------------
    # 2️⃣ Compute fingerprints (SimHash + Winnowing)
    # --------------------------------------------------
    logger.info("[TASK] Computing fingerprints for input repo...")
    compute_fingerprints_for_repo(input_dir)

    # --------------------------------------------------
    # 3️⃣ Fetch candidates
    # --------------------------------------------------
    logger.info("[TASK] Selecting candidate repos...")
    candidates = get_github_candidates(limit=10)
    candidates = [c for c in candidates if c != repo_url]

    logger.info(f"[TASK] Found {len(candidates)} candidate repos in DB.")

    # --------------------------------------------------
    # 4️⃣ Clone candidates
    # --------------------------------------------------
    repo_paths = {repo_url: input_dir}

    for cand_url in candidates:
        logger.info(f"[TASK] Cloning candidate: {cand_url}")
        cand_dir = clone_repo(cand_url, depth=1)

        if cand_dir:
            repo_paths[cand_url] = cand_dir

    logger.info(f"[TASK] Total repos being analyzed: {len(repo_paths)}")

    # --------------------------------------------------
    # 5️⃣ Orchestrator
    # --------------------------------------------------
    logger.info("[TASK] Running orchestrator...")
    orchestrator = Orchestrator()
    result = orchestrator.run_multiple(repo_paths)

    logger.info("[TASK] Orchestrator completed successfully.")

    # --------------------------------------------------
    # 6️⃣ Generate Report
    # --------------------------------------------------
    report_path = os.path.join(input_dir, "report.html")

    ReportGenerator().generate(
        report_data={
            "input_repo": repo_url,
            "top_3_repos": result["top_3_repos"],
            "all_repo_scores": result["all_repo_scores"]
        },
        output_path=report_path
    )

    logger.info(f"[TASK] Report generated at: {report_path}")

    # --------------------------------------------------
    # 7️⃣ Cleanup
    # --------------------------------------------------
    force_delete_folder(input_dir)

    # --------------------------------------------------
    # 8️⃣ Return output
    # --------------------------------------------------
    logger.info(f"===== [TASK DONE] {repo_url} =====\n")

    return {
        "input_repo": repo_url,
        "top_3_repos": result["top_3_repos"],
        "all_repo_scores": result["all_repo_scores"],
        "report_path": report_path,
        "status": "completed"
    }
