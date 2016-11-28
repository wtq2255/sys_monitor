import time
import psutil
from config import get_monitor, get_mongo
from models import MongoCfg, CPUModel, RAMModel


class BaseMonitor(object):

    def __init__(self):
        cfg = get_mongo()
        self.mcfg = MongoCfg(host=cfg['host'], port=int(cfg['port']), db=cfg['db'])

    def _save(self, **msg):
        self.model.save(**msg)

    def get(self, ts=None):
        if ts is None:
            return self.model.get_all()
        else:
            return self.model.get(ts=ts)


class CPUMonitor(BaseMonitor):

    def __init__(self):
        super(CPUMonitor, self).__init__()
        self.model = CPUModel(self.mcfg)

    def save(self):
        cpu_info = psutil.cpu_times_percent()
        msg = {'user': cpu_info.user,
               'nice': cpu_info.nice,
               'system': cpu_info.system,
               'idle': cpu_info.idle,
               'iowait': cpu_info.iowait,
               'irq': cpu_info.irq,
               'softirq': cpu_info.softirq,
               'steal': cpu_info.steal,
               'guest': cpu_info.guest,
               'guest_nice': cpu_info.guest_nice}
        self._save(**msg)

    def count(self):
        return psutil.cpu_count()


class RAMMonitor(BaseMonitor):
    def __init__(self):
        super(RAMMonitor, self).__init__()
        self.model = RAMModel(self.mcfg)

    def save(self):
        mem_info = psutil.virtual_memory()
        msg = {'total': mem_info.total,
               'available': mem_info.available,
               'used': mem_info.used,
               'free': mem_info.free,
               'active': mem_info.active,
               'inactive': mem_info.inactive,
               'buffers': mem_info.buffers,
               'cached': mem_info.cached,
               'shared': mem_info.shared,}
        self._save(**msg)


def main():
    interval = int(get_monitor('interval'))
    cpu = CPUMonitor()
    ram = RAMMonitor()
    while 1:
        cpu.save()
        ram.save()
        time.sleep(interval)


if __name__ == '__main__':
    main()
