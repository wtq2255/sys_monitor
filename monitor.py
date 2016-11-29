import time
import psutil
from config import get_monitor, get_mongo
from models import MongoCfg, CPUModel, RAMModel


class BaseMonitor(object):

    def __init__(self):
        cfg = get_mongo()
        self.mcfg = MongoCfg(host=cfg['host'], port=int(cfg['port']), db=cfg['db'],
                             expire=get_monitor('expire'), tz=get_monitor('tz'))

    def _save(self, **msg):
        self.model.save(**msg)

    def get(self, utc_ts=None):
        if utc_ts is None:
            return self.model.get_all()
        else:
            return self.model.get(utc_ts=utc_ts)

    def div(self, num1, num2):
        if num2 == 0:
            return 0.0
        else:
            return num1 / num2 * 1.0

    def percent(self, num1, num2):
        return round(self.div(num1, num2) * 100, 2)


class CPUMonitor(BaseMonitor):

    def __init__(self):
        super(CPUMonitor, self).__init__()
        self.model = CPUModel(self.mcfg)

    def save(self):
        cpu_info = psutil.cpu_times_percent()
        msg = {'user': cpu_info.user,
               'nice': cpu_info.nice,
               'system': cpu_info.system,
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
        msg = {'available': self.percent(mem_info.available, mem_info.total),
               'used': self.percent(mem_info.used, mem_info.total),
               'free': self.percent(mem_info.free, mem_info.total),
               'active': self.percent(mem_info.active, mem_info.total),
               'inactive': self.percent(mem_info.inactive, mem_info.total),
               'buffers': self.percent(mem_info.buffers, mem_info.total),
               'cached': self.percent(mem_info.cached, mem_info.total),
               'shared': self.percent(mem_info.shared, mem_info.total)}
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
