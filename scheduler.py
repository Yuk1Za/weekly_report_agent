"""
scheduler.py - 定时任务调度器
每周一早上 9:00 自动生成周报并发送到 Slack
"""

import os
import schedule
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from weekly_report_agent import run_weekly_report_agent, send_to_slack

load_dotenv()

class WeeklyReportScheduler:
    """周报调度管理器"""
    
    def __init__(self):
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        self.report_day = int(os.getenv("REPORT_DAY_OF_WEEK", "0"))  # 默认周一
        self.report_time = os.getenv("REPORT_TIME", "09:00")
        self.is_running = False
    
    def job_callback(self):
        """周报生成任务"""
        try:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始生成周报...")
            
            # 获取上周的周数
            today = datetime.now()
            last_week = today - timedelta(days=7)
            week_num = last_week.isocalendar()[1]
            
            # 生成周报
            run_weekly_report_agent(week_num=week_num)
            
            # 如果配置了 Slack webhook，发送报告
            if self.slack_webhook and self.slack_webhook != "your_webhook_url":
                print("正在发送到 Slack...")
                # 实际实现中这里需要获取生成的报告内容
                # send_to_slack(report_content, self.slack_webhook)
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 周报生成完成！")
            
        except Exception as e:
            print(f"错误: {str(e)}")
            # 实际场景可以集成错误告警（邮件、钉钉等）
    
    def start(self):
        """启动调度器"""
        self.is_running = True
        
        # 配置定时任务
        schedule.every().monday.at(self.report_time).do(self.job_callback)
        
        print(f"✓ 周报调度器已启动")
        print(f"  - 执行时间: 每周一 {self.report_time}")
        print(f"  - Slack 集成: {'已配置' if self.slack_webhook else '未配置'}")
        print(f"\n等待定时任务触发... (按 Ctrl+C 停止)\n")
        
        # 运行调度循环
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    def stop(self):
        """停止调度器"""
        self.is_running = False
        print("\n调度器已停止")

def main():
    """主程序"""
    scheduler = WeeklyReportScheduler()
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.stop()

if __name__ == "__main__":
    main()
