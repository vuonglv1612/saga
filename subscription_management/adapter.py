import json
import os

from .repo import Subscription, SubscriptionRepository


class JsonSubscriptionAdapter(SubscriptionRepository):
    def __init__(self, folder):
        self.folder = folder

    def _get_file_name(self, sub_id):
        return self.folder + f"/{sub_id}.json"

    def save(self, subscription: Subscription):
        with open(self._get_file_name(subscription.id), "w") as f:
            json.dump(subscription.dict(), f)

    def update(self, subscription: Subscription):
        with open(self._get_file_name(subscription.id), "w") as f:
            json.dump(subscription.dict(), f)

    def find(self, sub_id):
        # check if not exist file
        if not os.path.exists(self._get_file_name(sub_id)):
            return None

        with open(self._get_file_name(sub_id), "r") as f:
            data = json.load(f)
            return Subscription(**data)
