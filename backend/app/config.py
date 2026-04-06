"""应用配置

使用pydantic-settings管理环境变量和配置
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 应用配置
    app_name: str = "龙泉驿环卫智能体"
    app_version: str = "0.1.0"
    debug: bool = False

    # 数据库配置
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/lqy_db"

    # Redis配置
    redis_url: str = "redis://localhost:6379/0"

    # 日志配置
    log_level: str = "INFO"


# 全局配置实例
settings = Settings()
