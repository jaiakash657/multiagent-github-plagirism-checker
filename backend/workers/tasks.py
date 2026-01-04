import os
import sys
import shutil
import stat
import time
import logging

# ------------------------------------------------------
# Make backend/ the project root
# ------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from celery import shared_task
from config.logger import logger
from agents.fingerprint_agent import FingerprintAgent
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
        force_delete_folder(temp_dir)
        return None

    return temp_dir


# ------------------------------------------------------
# MAIN CELERY TASK
# ------------------------------------------------------
@shared_task(bind=True)
def analyze_repository_task(self, repo_url: str, depth: int = 1):

    logger.info(f"\n===== [TASK START] {repo_url} =====")

    repo_paths = {}

    try:
        # --------------------------------------------------
        # 1️⃣ Clone INPUT repo
        # --------------------------------------------------
        input_dir = clone_repo(repo_url, depth)
        if not input_dir:
            return {"error": "Failed to clone input repository"}

        repo_paths[repo_url] = input_dir

        # --------------------------------------------------
        # 2️⃣ INGEST input repo into DB
        # --------------------------------------------------
        fingerprint_agent = FingerprintAgent()
        input_fp = fingerprint_agent.ingest_repo(repo_url, input_dir)

        logger.info(
            f"[INGEST] repo={repo_url} "
            f"tokens={input_fp.get('token_count', 0)}"
        )

        # --------------------------------------------------
        # 3️⃣ Fetch DB candidates
        # --------------------------------------------------
        db_candidates = get_simhash_candidates(limit=50)

        db_candidates = [
            c for c in db_candidates if c["repo_url"] != repo_url
        ]

        if not db_candidates:
            logger.info("[INFO] No DB candidates found")

        # --------------------------------------------------
        # 3️⃣.1 Rank DB candidates using fingerprint (TOP-K)
        # --------------------------------------------------
        ranked = []

        for cand in db_candidates:
            try:
                fp_score = fingerprint_agent.compare_with_db(input_fp, cand)
                ranked.append({
                    "repo_url": cand["repo_url"],
                    "score": (
                        fp_score.get("simhash_score", 0.0)
                        + fp_score.get("winnowing_score", 0.0)
                    ),
                })
            except Exception:
                logger.exception(f"[FP COMPARE FAILED] {cand.get('repo_url')}")
                continue

        ranked.sort(key=lambda x: x["score"], reverse=True)
        top_k_repos = [r["repo_url"] for r in ranked[:3]]  # TOP-K = 3

        logger.info(f"[TOP-K] Selected repos: {top_k_repos}")

        # --------------------------------------------------
        # 3️⃣.2 Clone ONLY TOP-K candidate repos
        # --------------------------------------------------
        for cand_url in top_k_repos:
            cand_dir = clone_repo(cand_url, depth=1)
            if cand_dir:
                repo_paths[cand_url] = cand_dir

        # --------------------------------------------------
        # 4️⃣ Run orchestrator (FORCED heavy agents)
        # --------------------------------------------------
        orchestrator = Orchestrator()

        result = orchestrator.run_multiple(
            input_repo_url=repo_url,
            input_path=input_dir,
            repo_paths=repo_paths,
            db_candidates=db_candidates,
            top_k=3,
            force_heavy=False,   
        )

        # --------------------------------------------------
        # 5️⃣ Generate report + PDF
        # --------------------------------------------------
        reporter = ReportGenerator()

        report_name = repo_url.split("/")[-1]

        report_path = reporter.generate_html(
            data={
                "input_repo": repo_url,
                "top_3_repos": result["top_3_repos"],
                "all_repo_scores": result["all_repo_scores"],
            },
            report_name=report_name,
        )

        pdf_path = reporter.generate_pdf(report_path)

        logger.info(f"===== [TASK DONE] {repo_url} =====")

        return {
            "input_repo": repo_url,
            "top_3_repos": result["top_3_repos"],
            "all_repo_scores": result["all_repo_scores"],
            "report_path": report_path,
            "pdf_path": pdf_path,
            "status": "completed",
        }

    finally:
        # --------------------------------------------------
        # 6️⃣ Cleanup temp repos
        # --------------------------------------------------
        time.sleep(0.3)
        for path in repo_paths.values():
            force_delete_folder(path)

        logger.info("[CLEAN UP] Temp repos deleted")
