import os
import pandas as pd
from datetime import datetime

class ModelMetricsAnalyzer:
    def __init__(self):
        self.base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
        self.logs_file = os.path.join(self.base_dir, "logs", "inference_metrics.csv")
        self.reports_dir = os.path.join(self.base_dir, "reports")
        os.makedirs(self.reports_dir, exist_ok=True)
        
    def analyze_performance(self):
        if not os.path.exists(self.logs_file):
            print("No inference metrics found to analyze.")
            return False
            
        try:
            df = pd.read_csv(self.logs_file)
            
            total_validations = len(df)
            if total_validations == 0:
                print("Inference log is empty.")
                return False
                
            pass_rate = (df['validation_status'] == 'PASS').mean() * 100
            failed_count = (df['validation_status'] == 'FAIL').sum()
            avg_dialect_conf = df['dialect_confidence'].mean()
            avg_visual_score = df['content_match_score'].mean()
            avg_runtime = df['processing_time_s'].mean()
            max_runtime = df['processing_time_s'].max()
            
            # Predictor proportions
            dialect_counts = df['dialect_prediction'].value_counts()
            honduras_pct = (dialect_counts.get('Honduras', 0) / total_validations) * 100
            other_pct = (dialect_counts.get('Other', 0) / total_validations) * 100
            
            report = [
                "# AI Video Validation - Model Performance Report",
                f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "## Global Metrics",
                f"- **Total Validations Tracked**: {total_validations}",
                f"- **Global Pass Rate**: {pass_rate:.1f}%",
                f"- **Total Failures**: {failed_count}",
                "",
                "## AI Confidence Benchmarks",
                f"- **Average Dialect Confidence (ML)**: {avg_dialect_conf:.4f}",
                f"- **Average Visual Semantics Score (CLIP)**: {avg_visual_score:.4f}",
                "",
                "## System Performance",
                f"- **Average Runtime Pipeline**: {avg_runtime:.2f}s",
                f"- **Maximum Pipeline Spike**: {max_runtime:.2f}s",
                "",
                "## Inference Distribution",
                f"- **Honduras**: {honduras_pct:.1f}%",
                f"- **Other Spanish**: {other_pct:.1f}%"
            ]
            
            out_file = os.path.join(self.reports_dir, "model_performance_report.md")
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(report))
                
            print(f"✅ Performance Analytics generated at {out_file}")
            return True
            
        except Exception as e:
            print(f"Failed to generate performance analytics: {e}")
            return False

if __name__ == "__main__":
    analyzer = ModelMetricsAnalyzer()
    analyzer.analyze_performance()
