import docker
import schedule
import time

from config import TELEGRAM_API_TOKEN, TELEGRAM_CHAT_ID
from telegram import send_telegram_message

def get_all_containers_dict(client):
    containers = client.containers.list(all=True)
    containers_dict = {}
    for container in containers:
        containers_dict[container.id] = container
    return containers_dict

def check_container_changed_state(old_container, new_container):
    if old_container is None and new_container is not None:
        return True
    if old_container is not None and new_container is None:
        return True
    if old_container is None and new_container is None:
        return False
    if old_container.status != new_container.status:
        return True
    return False

def get_containers_changed_status(old_containers_dict, new_containers_dict):
    if old_containers_dict == {} and new_containers_dict == {}:
        return []
    containers = []
    all_ids = set(old_containers_dict.keys()).union(set(new_containers_dict.keys()))
    for container_id in all_ids:
        old_container = old_containers_dict.get(container_id)
        new_container = new_containers_dict.get(container_id)
        if check_container_changed_state(old_container, new_container):
            containers.append((old_container, new_container))
    return containers

def notify_containers_changed_status(container_pairs):
    for old_container, new_container in container_pairs:
        message = None
        if old_container is None and new_container is not None:
            message = f'{new_container.name} created.'
        elif old_container is not None and new_container is None:
            message = f'{old_container.name} deleted.'
        elif old_container.status != new_container.status:
            message = f'{old_container.name} changed status from {old_container.status.upper()} to {new_container.status.upper()}.'
        
        if not message:
            return 
        
        print(message)
        send_telegram_message(TELEGRAM_API_TOKEN, TELEGRAM_CHAT_ID, message)






if __name__ == '__main__':
    client = docker.from_env()

    old_containers_dict = get_all_containers_dict(client)

    def job():
        global old_containers_dict
        containers_dict = get_all_containers_dict(client)
        container_pairs = get_containers_changed_status(old_containers_dict, containers_dict)
        notify_containers_changed_status(container_pairs)
        old_containers_dict = containers_dict
        print('sleeping')
    
    schedule.every(3).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
