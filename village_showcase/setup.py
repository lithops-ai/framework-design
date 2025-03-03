
import kopf
from village import Village

def init_system():
    village = Village()
    village.load_existing_villagers()
    village.ensure_minimum_villagers()

    village.bind_villagers_to_queues()


if __name__ == "__main__":
    init_system()
    kopf.run()
