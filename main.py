import docker
import time

client = docker.from_env()


def get_all_containers_dict():
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
        if old_container is None and new_container is not None:
            print(f'{new_container.name} created.')
            return
        if old_container is not None and new_container is None:
            print(f'{old_container.name} deleted.')
            return
        if old_container.status != new_container.status:
            print(f'{old_container.name} changed status from {old_container.status} to {new_container.status}.')


starttime = time.time()
periodicity = 10
old_containers_dict = get_all_containers_dict()

"""Проверяет состояние контейнера каждые 10 секунд."""
while True:
    containers_dict = get_all_containers_dict()
    container_pairs = get_containers_changed_status(old_containers_dict, containers_dict)
    notify_containers_changed_status(container_pairs)
    old_containers_dict = containers_dict
    time.sleep(periodicity - ((time.time() - starttime) % periodicity))
    print('sleeping')