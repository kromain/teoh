from skynet import Config, ConfigType


def get_skynet_config(pytest_config):
    if pytest_config.getoption("skynet_shared_config", default=False, skip=True):
        conf_type = ConfigType.SHARED
    else:
        conf_type = ConfigType.USER
    user_ext = pytest_config.getoption("skynet_user_config", default='', skip=True)

    try:
        return Config(conf_type, user_ext)
    except FileNotFoundError:
        # ignore missing config file if at least one --ip in cmdline args and no --shared or --conf specified
        if not pytest_config.getoption("target_ip", default=[], skip=True):
            raise
        if conf_type == ConfigType.SHARED or user_ext:
            raise
        pass

    return None
