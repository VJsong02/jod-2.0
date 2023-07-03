from bot import client
import json
from csn import calc_debt


if __name__ == "__main__":
    data = json.load(open('config.json',))
    client.run(data['token'])