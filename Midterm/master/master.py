import redis
import utils

config = utils.get_config()

if __name__ == "__main__":
    r = redis.Redis(**config["message_broker"]["connection"])
    pub = r.publish(
        channel=config["message_broker"]["publisher"]["channel"],
        message="Hello, World!",
    )
