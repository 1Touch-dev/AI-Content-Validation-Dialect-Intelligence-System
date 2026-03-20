import os
import pandas as pd
from datetime import datetime, timedelta

def generate_weekly_report():
    base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
    logs_file = os.path.join(base_dir, "logs", "inference_metrics.csv")
    report_file = os.path.join(base_dir, "reports", "model_health_weekly.md")
    
    if not os.path.exists(logs_file):
        print("No telemetry metrics exist to generate weekly health.")
        return
        
    df = pd.read_csv(logs_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Filter 7 days
    week_ago = datetime.now() - timedelta(days=7)
    weekly_df = df[df['timestamp'] >= week_ago]
    
    if len(weekly_df) == 0:
        print("No inferences occurred in the past 7 days.")
        return
        
    total_validations = len(weekly_df)
    pass_rate = (weekly_df['validation_status'] == 'PASS').mean() * 100
    
    # Grab worst 3 failures
    failures = weekly_df[weekly_df['validation_status'] == 'FAIL'].sort_values('validation_score').head(3)
    
    report = [
        f"# AI Video Validation - Weekly Health Report (W{datetime.now().strftime('%W')}, {datetime.now().year})",
        "",
        "## Weekly Summary",
        f"- **Period**: {week_ago.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}",
        f"- **Total Videos Validated**: {total_validations}",
        f"- **Rolling Pass Rate**: {pass_rate:.1f}%",
        "",
        "## Worst Edge Cases (Failures)",
    ]
    
    if len(failures) > 0:
        for idx, row in failures.iterrows():
            report.append(f"1. **{row['video_name']}** -> Score: {row['validation_score']:.2f} | Dialect: {row['dialect_prediction']} | Conf: {row['dialect_confidence']:.2f} | Visual: {row['content_match_score']:.2f}")
    else:
        report.append("- *No systemic failures detected this week.*")
        
    report.append("")
    report.append("## System Status")
    
    drift_detected = (pass_rate < 50.0 or weekly_df['dialect_confidence'].mean() < 0.85)
    flag = "**CRITICAL DRIFT: MODEL_RETRAINING_RECOMMENDED = TRUE**" if drift_detected else "**SYSTEM_MONITORING_ACTIVE = TRUE. Validation Engine Stable.**"
    report.append(flag)
    
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
        
    print(f"Weekly Health Report securely aggregated to {report_file}")

if __name__ == "__main__":
    generate_weekly_report()
