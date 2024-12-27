import redis
import utils
import time

config = utils.get_config()

if __name__ == "__main__":
    r = redis.Redis(**config["message_broker"]["connection"])
    pub = r.pubsub()
    pub.subscribe(config["message_broker"]["subscriber"]["channel"])

    while True:
        data = pub.get_message()
        if data:
            message = data["data"]
            if message and message != 1:
                print("Message: {}".format(message.decode("utf-8")))

        time.sleep(1)
