# Configuration manager

"""
yaml
k: v
"""
import yaml
import os
from utils.path_handler import get_abs_path
from infrastructure.exceptions.handler import ConfigError


def load_config(config_path: str = get_abs_path("configs/config.yaml"), encoding: str = "utf-8"):
    if not os.path.exists(config_path):
        raise ConfigError(f"配置文件不存在: {config_path}", context={"path": config_path})
        
    try:
        with open(config_path, "r", encoding=encoding) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            if config is None:
                raise ConfigError("配置文件为空", context={"path": config_path})
            return config
    except yaml.YAMLError as e:
        raise ConfigError(f"YAML 解析失败: {str(e)}", context={"path": config_path})
    except Exception as e:
        raise ConfigError(f"读取配置失败: {str(e)}", context={"path": config_path})

# 懒加载配置，避免导入时直接抛异常
conf_loader = None
try:
    conf_loader = load_config()
except ConfigError:
    # 这里可以根据需要选择是否在模块级别抛出，或者留给调用者处理
    pass
