import ipaddress
import json
from skynet import Config, ConfigType, TargetConfig, UserConfig

def parse_cmdline_users(pytest_config):
    users = []
    for userarg in pytest_config.getoption("users", default=[], skip=True):
        for user in userarg.split(","):
            psnid, _, user = user.partition("!")
            email, _, password = user.partition(":")
            if not (user and email and password):
                raise ValueError("Invalid format for --user option! needs to be psnid!email:password")
            users.append(UserConfig(psnid, email, password))
    return users


def parse_cmdline_ip_list(pytest_config):
    cmdline_iplist = []
    for iparg in pytest_config.getoption("target_ips", default=[], skip=True):
        for ip in iparg.split(","):
            try:
                ipaddress.ip_address(ip)
            except ValueError:
                raise  # just pass the exception over if the ip address is invalid
            cmdline_iplist.append(TargetConfig(ip, "Devkit {}".format(ip)))
    return cmdline_iplist


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
        if not pytest_config.getoption("target_ips", default=[], skip=True):
            raise
        if conf_type == ConfigType.SHARED or user_ext:
            raise
        pass

    return None

def create_user_config_file(targets, users, future_args=None):
    conf_targets = []
    for target in targets:
        conf_targets.append({"ID": target.id, "IP": target.ip})

    conf_users = []
    for user in users:
        conf_users.append({"psnid": user.psnid, "email": user.email, "password": user.password})

    json.dump({"targets": conf_targets, "users": conf_users}, open("skynet.user.conf",'x'), indent=4)
