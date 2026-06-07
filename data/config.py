from environs import Env


env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS", default=[])
IP = env.str("ip", default="127.0.0.1")
DEFAULT_HEIGHT = env.int("DEFAULT_HEIGHT", default=175)
DEFAULT_WEIGHT = env.float("DEFAULT_WEIGHT", default=89)
DEFAULT_TIMEZONE_OFFSET = env.int("DEFAULT_TIMEZONE_OFFSET", default=5)
