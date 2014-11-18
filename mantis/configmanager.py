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


def parse_cmdline_ips(pytest_config):
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
        config = Config(conf_type, user_ext)
    except FileNotFoundError:
        # ignore missing config file if at least one --ip in cmdline args and no --shared or --conf specified
        if not pytest_config.getoption("target_ips", default=[], skip=True):
            raise
        if conf_type == ConfigType.SHARED or user_ext:
            raise
        return None

    # override config with data passed through cmdline arguments
    cmdline_ips = parse_cmdline_ips(pytest_config)
    if cmdline_ips:
        config.targets = cmdline_ips
    cmdline_users = parse_cmdline_users(pytest_config)
    if cmdline_users:
        config.users = cmdline_users

    return config


def create_user_config_file(pytest_config):
    targets = []
    for target in parse_cmdline_ips(pytest_config):
        targets.append({"ID": target.id, "IP": target.ip})

    users = []
    for user in parse_cmdline_users(pytest_config):
        users.append({"psnid": user.psnid, "email": user.email, "password": user.password})

    json.dump({"targets": targets, "users": users, "library_paths": "."}, open("skynet.user.conf",'x'), indent=4)
