import time
import json
import os
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from scrapers.logger import log_info, log_error
from core.collectors.market_collector import fetch_all_trends
from core.processing.recommender import ai_recommendation
from publishers.mail_sender import send_email
from core.ai.evolution_engine import analyze_logs_with_gpt
from core.ai.auto_patch import generate_autopatch

load_dotenv()

CONFIG_PATH = "config/config.json"

def load_cfg():
    if os.path.exists(CONFIG_PATH):
        try:
            return json.load(open(CONFIG_PATH, "r", encoding="utf-8"))
        except Exception:
            pass
    return {"report_time": "08:00", "poll_interval_minutes": 60, "evolution_check_interval_hours": 2, "self_learn_hours": [0, 12]}

cfg = load_cfg()

def job_collect():
    log_info("[Job] 采集市场权威数据")
    try:
        trends = fetch_all_trends()
        log_info(f"[Job] Trends count={len(trends)}")
        # 可拓展：写入 DB
    except Exception as e:
        log_error(f"[Job] collect failed: {e}")

def job_daily_report():
    log_info("[Job] 生成每日报告")
    summary = "示例摘要：北美 GMV 上升，欧洲轻微下滑"
    if os.getenv("OPENAI_API_KEY"):
        ai_text = ai_recommendation(summary)
    else:
        ai_text = "未配置 OPENAI_API_KEY"
    html = f"<h3>每日报告</h3><p>{summary}</p><h4>AI建议</h4><pre>{ai_text}</pre>"
    try:
        send_email("企业版智能体 每日报告", html)
    except Exception as e:
        log_error(f"[Job] 邮件发送失败: {e}")

def job_evolution_check():
    log_info("[Job] 自我演化检查")
    try:
        suggestion = analyze_logs_with_gpt()
        patch_path, _ = generate_autopatch()
        log_info(f"[Job] 演化建议已生成，补丁: {patch_path}")
    except Exception as e:
        log_error(f"[Job] 自我演化失败: {e}")

def job_self_learn():
    log_info("[Job] 自学习任务启动（占位）")
    # 这里实际应调用 ai_self_learn（如需保留旧 scheduler 逻辑）
    # try:
    #     ai_self_learn()
    # except Exception as e:
    #     log_error(f"[Job] 自学习失败: {e}")

def start_scheduler():
    sched = BackgroundScheduler()
    sched.add_job(job_collect, 'interval', minutes=cfg.get("poll_interval_minutes", 60))
    hh, mm = cfg.get("report_time", "08:00").split(":")
    sched.add_job(job_daily_report, 'cron', hour=int(hh), minute=int(mm))
    sched.add_job(job_evolution_check, 'interval', hours=cfg.get("evolution_check_interval_hours", 2))
    for hour in cfg.get("self_learn_hours", []):
        sched.add_job(job_self_learn, 'cron', hour=hour, minute=0)
    sched.start()
    log_info("[Scheduler] 已启动")
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        sched.shutdown()
        log_info("[Scheduler] 已关闭")

if __name__ == "__main__":
    start_scheduler()