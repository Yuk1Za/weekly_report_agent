"""
advanced_data_sources.py - 生产环境的真实数据源集成示例
包含 Google Analytics、Facebook Ads、Salesforce 的实际 API 调用
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import os
from datetime import datetime, timedelta

# ============================================================================
# 抽象数据源基类
# ============================================================================

class DataSource(ABC):
    """所有数据源的抽象基类"""
    
    @abstractmethod
    def fetch_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取数据"""
        pass
    
    @abstractmethod
    def validate_credentials(self) -> bool:
        """验证凭证"""
        pass

# ============================================================================
# Google Analytics 4 集成
# ============================================================================

class GoogleAnalyticsDataSource(DataSource):
    """Google Analytics 4 数据源
    
    需要：
    - service account JSON key
    - GA property ID
    """
    
    def __init__(self, credentials_path: str, property_id: str):
        self.credentials_path = credentials_path
        self.property_id = property_id
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化 GA4 客户端"""
        try:
            from google.analytics.data_v1beta import BetaAnalyticsDataClient
            from google.oauth2 import service_account
            
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
            self.client = BetaAnalyticsDataClient(credentials=credentials)
        except ImportError:
            print("请安装: pip install google-analytics-data")
    
    def validate_credentials(self) -> bool:
        """验证 GA4 凭证"""
        try:
            if not os.path.exists(self.credentials_path):
                return False
            return self.client is not None
        except Exception as e:
            print(f"GA4 验证失败: {str(e)}")
            return False
    
    def fetch_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取 GA4 数据"""
        if not self.client:
            return {}
        
        try:
            from google.analytics.data_v1beta.types import (
                RunReportRequest, DateRange, Metric, Dimension
            )
            
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                metrics=[
                    Metric(name="activeUsers"),
                    Metric(name="newUsers"),
                    Metric(name="sessions"),
                    Metric(name="bounceRate"),
                    Metric(name="conversions"),
                    Metric(name="totalRevenue"),
                ],
                dimensions=[
                    Dimension(name="date"),
                    Dimension(name="sessionSource"),
                ]
            )
            
            response = self.client.run_report(request)
            
            # 解析响应
            data = {
                "source": "Google Analytics 4",
                "period": f"{start_date} to {end_date}",
                "metrics": {}
            }
            
            for row in response.rows:
                date = row.dimension_values[0].value
                source = row.dimension_values[1].value
                metrics = row.metric_values
                
                if date not in data["metrics"]:
                    data["metrics"][date] = {}
                
                data["metrics"][date][source] = {
                    "active_users": int(metrics[0].value),
                    "new_users": int(metrics[1].value),
                    "sessions": int(metrics[2].value),
                    "bounce_rate": float(metrics[3].value),
                    "conversions": int(metrics[4].value),
                    "revenue": float(metrics[5].value),
                }
            
            return data
        
        except Exception as e:
            print(f"获取 GA4 数据失败: {str(e)}")
            return {}

# ============================================================================
# Facebook Ads 集成
# ============================================================================

class FacebookAdsDataSource(DataSource):
    """Facebook Ads Manager 数据源
    
    需要：
    - Access Token
    - Ad Account ID
    """
    
    def __init__(self, access_token: str, ad_account_id: str):
        self.access_token = access_token
        self.ad_account_id = ad_account_id
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化 Facebook Ads 客户端"""
        try:
            from facebook_business.api import FacebookAdsApi
            from facebook_business.adobjects.adaccount import AdAccount
            
            FacebookAdsApi.init(access_token=self.access_token)
            self.client = AdAccount(f"act_{self.ad_account_id}")
        except ImportError:
            print("请安装: pip install facebook-business")
    
    def validate_credentials(self) -> bool:
        """验证 Facebook Ads 凭证"""
        try:
            if self.client:
                # 尝试获取账户信息
                self.client.get_insights()
                return True
            return False
        except Exception as e:
            print(f"Facebook Ads 验证失败: {str(e)}")
            return False
    
    def fetch_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取 Facebook Ads 数据"""
        if not self.client:
            return {}
        
        try:
            from facebook_business.adobjects.insights import AdsInsights
            
            insights = self.client.get_insights(
                fields=[
                    AdsInsights.Field.date_start,
                    AdsInsights.Field.campaign_name,
                    AdsInsights.Field.spend,
                    AdsInsights.Field.impressions,
                    AdsInsights.Field.clicks,
                    AdsInsights.Field.actions,
                    AdsInsights.Field.action_values,
                ],
                params={
                    "time_range": {
                        "since": start_date,
                        "until": end_date
                    },
                    "time_increment": 1  # 按天统计
                }
            )
            
            data = {
                "source": "Facebook Ads",
                "period": f"{start_date} to {end_date}",
                "campaigns": {}
            }
            
            for record in insights:
                campaign_name = record.get(AdsInsights.Field.campaign_name)
                date = record.get(AdsInsights.Field.date_start)
                
                if campaign_name not in data["campaigns"]:
                    data["campaigns"][campaign_name] = []
                
                data["campaigns"][campaign_name].append({
                    "date": date,
                    "spend": float(record.get(AdsInsights.Field.spend, 0)),
                    "impressions": int(record.get(AdsInsights.Field.impressions, 0)),
                    "clicks": int(record.get(AdsInsights.Field.clicks, 0)),
                    "conversions": len(record.get(AdsInsights.Field.actions, [])),
                    "ctr": (
                        int(record.get(AdsInsights.Field.clicks, 0)) /
                        int(record.get(AdsInsights.Field.impressions, 1)) * 100
                    ) if int(record.get(AdsInsights.Field.impressions, 1)) > 0 else 0,
                })
            
            return data
        
        except Exception as e:
            print(f"获取 Facebook Ads 数据失败: {str(e)}")
            return {}

# ============================================================================
# Salesforce CRM 集成
# ============================================================================

class SalesforceDataSource(DataSource):
    """Salesforce CRM 数据源
    
    需要：
    - Username
    - Password
    - Security Token
    - Instance URL
    """
    
    def __init__(self, username: str, password: str, security_token: str, 
                 instance_url: str):
        self.username = username
        self.password = password
        self.security_token = security_token
        self.instance_url = instance_url
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化 Salesforce 客户端"""
        try:
            from simple_salesforce import Salesforce
            
            self.client = Salesforce(
                username=self.username,
                password=self.password,
                security_token=self.security_token,
                instance_url=self.instance_url
            )
        except ImportError:
            print("请安装: pip install simple-salesforce")
    
    def validate_credentials(self) -> bool:
        """验证 Salesforce 凭证"""
        try:
            if self.client:
                # 尝试查询一条记录
                self.client.query("SELECT Id FROM Account LIMIT 1")
                return True
            return False
        except Exception as e:
            print(f"Salesforce 验证失败: {str(e)}")
            return False
    
    def fetch_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取 Salesforce CRM 数据"""
        if not self.client:
            return {}
        
        try:
            # 获取新增线索
            leads_query = f"""
                SELECT Id, Name, Phone, Email, LeadSource, Status, CreatedDate
                FROM Lead
                WHERE CreatedDate >= {start_date}T00:00:00Z
                AND CreatedDate <= {end_date}T23:59:59Z
            """
            leads = self.client.query_all(leads_query)
            
            # 获取成交机会
            opportunities_query = f"""
                SELECT Id, Name, Amount, StageName, CloseDate, CreatedDate
                FROM Opportunity
                WHERE CreatedDate >= {start_date}T00:00:00Z
                AND CreatedDate <= {end_date}T23:59:59Z
                AND IsClosed = true
            """
            opportunities = self.client.query_all(opportunities_query)
            
            data = {
                "source": "Salesforce CRM",
                "period": f"{start_date} to {end_date}",
                "leads": {
                    "total": leads["totalSize"],
                    "by_source": {}
                },
                "opportunities": {
                    "closed_deals": opportunities["totalSize"],
                    "total_revenue": 0,
                    "deals": []
                }
            }
            
            # 统计线索来源
            for lead in leads["records"]:
                source = lead.get("LeadSource", "Unknown")
                if source not in data["leads"]["by_source"]:
                    data["leads"]["by_source"][source] = 0
                data["leads"]["by_source"][source] += 1
            
            # 统计成交额
            for opp in opportunities["records"]:
                amount = float(opp.get("Amount", 0))
                data["opportunities"]["total_revenue"] += amount
                data["opportunities"]["deals"].append({
                    "name": opp["Name"],
                    "amount": amount,
                    "stage": opp["StageName"],
                    "close_date": opp["CloseDate"]
                })
            
            return data
        
        except Exception as e:
            print(f"获取 Salesforce 数据失败: {str(e)}")
            return {}

# ============================================================================
# 集成示例
# ============================================================================

def create_data_sources() -> Dict[str, DataSource]:
    """创建所有数据源"""
    
    sources = {}
    
    # Google Analytics
    if os.getenv("GA4_CREDENTIALS"):
        sources["analytics"] = GoogleAnalyticsDataSource(
            credentials_path=os.getenv("GA4_CREDENTIALS"),
            property_id=os.getenv("GA4_PROPERTY_ID")
        )
    
    # Facebook Ads
    if os.getenv("FB_ACCESS_TOKEN"):
        sources["ads"] = FacebookAdsDataSource(
            access_token=os.getenv("FB_ACCESS_TOKEN"),
            ad_account_id=os.getenv("FB_AD_ACCOUNT_ID")
        )
    
    # Salesforce
    if os.getenv("SF_USERNAME"):
        sources["crm"] = SalesforceDataSource(
            username=os.getenv("SF_USERNAME"),
            password=os.getenv("SF_PASSWORD"),
            security_token=os.getenv("SF_SECURITY_TOKEN"),
            instance_url=os.getenv("SF_INSTANCE_URL")
        )
    
    return sources

def validate_all_sources(sources: Dict[str, DataSource]) -> bool:
    """验证所有数据源连接"""
    
    print("验证数据源连接...")
    all_valid = True
    
    for name, source in sources.items():
        is_valid = source.validate_credentials()
        status = "✓" if is_valid else "✗"
        print(f"  {status} {name.capitalize()}")
        all_valid = all_valid and is_valid
    
    return all_valid

def fetch_all_data(sources: Dict[str, DataSource], 
                   start_date: str = None, 
                   end_date: str = None) -> Dict[str, Any]:
    """并行获取所有数据源的数据"""
    
    if not start_date:
        end_date = datetime.now().date()
        start_date = (end_date - timedelta(days=7)).isoformat()
        end_date = end_date.isoformat()
    
    data = {}
    
    for name, source in sources.items():
        print(f"获取 {name} 数据...")
        data[name] = source.fetch_data(start_date, end_date)
    
    return data

if __name__ == "__main__":
    # 示例：验证并获取数据
    sources = create_data_sources()
    
    if validate_all_sources(sources):
        all_data = fetch_all_data(sources)
        print("\n✓ 数据获取成功")
        print(f"数据摘要: {list(all_data.keys())}")
    else:
        print("\n✗ 某些数据源连接失败")
