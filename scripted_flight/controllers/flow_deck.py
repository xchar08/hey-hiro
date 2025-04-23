import time
from cflib.crazyflie.log import LogConfig

def start_flow_logging(cf):
    log_config = LogConfig(name='Flow', period_in_ms=100)
    log_config.add_variable('range.zrange', 'float')
    zrange = [0.0]
    def callback(timestamp, data, config):
        zrange[0] = data['range.zrange']
    log_config.data_received_cb.add_callback(callback)
    cf.log.add_config(log_config)
    log_config.start()
    time.sleep(1)
    return log_config, zrange
