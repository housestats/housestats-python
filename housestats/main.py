import click
import fnmatch
import logging
import paho.mqtt.publish
import stevedore
import time

import ruamel.yaml as yaml

LOG = logging.getLogger(__name__)
CONTEXT_SETTINGS = dict(auto_envvar_prefix='HOUSESTATS')


class SensorApp():
    def __init__(self, config=None):
        self.config = config if config else {}

        self.init_plugins()
        self.init_sensors()

    def init_plugins(self):
        self.ext = stevedore.extension.ExtensionManager(
            'housestats.sensor')

    def init_sensors(self):
        self.sensors = {sensor['name']: sensor
                        for sensor in self.config.get('sensors', [])}

    def fetch(self, name):
        LOG.debug('fetching sensor %s', name)
        sensorcfg = self.sensors[name]
        plugin = self.ext[sensorcfg['driver']].plugin
        sensor = plugin(sensorcfg.get('config', {}))
        return sensor.fetch()


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--verbose', '-v', is_flag=True)
@click.option('--debug', is_flag=True)
@click.option('--config', '-f',
              default='sensors.yml',
              type=click.File())
@click.pass_context
def cli(ctx, config=None, debug=None, verbose=None):
    if debug:
        loglevel = 'DEBUG'
    elif verbose:
        loglevel = 'INFO'
    else:
        loglevel = 'WARNING'

    logging.basicConfig(level=loglevel)

    configdata = yaml.safe_load(config)
    ctx.obj = SensorApp(config=configdata.get('housestats', {}))


def get_sensor_list(ctx, sensors, ignore_missing):
    selected = []

    for pattern in sensors:
        matches = fnmatch.filter(ctx.obj.sensors.keys(), pattern)
        if not matches and not ignore_missing:
            raise click.ClickException(
                'pattern "{}" did not match any defined sensors'.format(
                    pattern))
        selected.extend(matches)

    return selected


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option('--ignore-missing', is_flag=True)
@click.argument('sensors', nargs=-1)
@click.pass_context
def fetch(ctx, sensors, ignore_missing=False):
    selected = get_sensor_list(ctx, sensors, ignore_missing)

    for sensorname in selected:
        res = ctx.obj.fetch(sensorname)
        for result in res:
            print(result.to_json(indent=2))


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option('--ignore-missing', is_flag=True)
@click.option('--mqtt-host')
@click.option('--mqtt-port', type=int)
@click.option('--mqtt-client-id')
@click.option('--namespace')
@click.option('--interval', '-i', type=int)
@click.argument('sensors', nargs=-1)
@click.pass_context
def publish(ctx, sensors,
            mqtt_host=None,
            mqtt_port=None,
            mqtt_client_id=None,
            namespace=None,
            interval=None,
            ignore_missing=False):
    mqtt_config = ctx.obj.config.get('mqtt', {})

    if mqtt_host is None:
        mqtt_host = mqtt_config.get('host', 'localhost')
    if mqtt_port is None:
        mqtt_port = mqtt_config.get('port', 1883)
    if mqtt_client_id is None:
        mqtt_client_id = mqtt_config.get('client_id')
    if namespace is None:
        namespace = mqtt_config.get('namespace', 'sensor')
    if interval is None:
        interval = mqtt_config.get('interval', 0)

    selected = get_sensor_list(ctx, sensors, ignore_missing)
    if not selected:
        raise click.ClickException('no sensors selected')

    LOG.debug('publishing sensors: %s', selected)

    while True:
        t_start = time.time()

        msgs = []
        for sensorname in selected:
            try:
                res = ctx.obj.fetch(sensorname)
            except click.ClickException:
                raise
            except Exception as err:
                LOG.error('failed to fetch value from sensor %s: %s',
                          sensorname, err)

            for result in res:
                topic = '{}/{}/{}'.format(
                    namespace, result.sensor_type, result.sensor_id)
                payload = result.to_json()
                msgs.append(dict(topic=topic, payload=payload))

                LOG.info('collected topic %s', topic)
                LOG.debug('collected payload %s', payload)

        try:
            LOG.info('publishing %d messages', len(msgs))
            paho.mqtt.publish.multiple(
                msgs,
                hostname=mqtt_host,
                port=mqtt_port,
                client_id=mqtt_client_id)
        except Exception as err:
            LOG.error('failed to publish messages: %s', err)

        if interval == 0:
            break

        time.sleep(interval - (time.time() - t_start))


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('sensors', nargs=-1)
@click.pass_context
def sensors(ctx, sensors):
    if not sensors:
        sensors = ['*']

    selected = get_sensor_list(ctx, sensors, True)
    print('\n'.join(selected))


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def drivers(ctx):
    print('\n'.join(ctx.obj.ext.names()))
