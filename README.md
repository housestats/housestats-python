# Housestats

This is a wrapper for fetching metrics from remote APIs and publishing
them to an MQTT service.

## Usage

To fetch a metric and display it locally:

    $ housestats fetch neurio-house
    {
      "topic": "sensor/neurio/1234",
      "sensor_type": "neurio",
      "sensor_id": "1234",
      "tags": {},
      "fields": {
        "consumptionPower": 1343,
        "generationPower": 100
      }
    }

To fetch a single metric and publish it to the mqtt server:

    $ housestats publish neurio-house

To periodically publish metrics:

    $ housestats publish --interval 60 neurio-house

To list available drivers:

    $ housestats drivers

To list configured sources:

    $ housestats sensors

## Configuration

    housestats:
      mqtt:
        host: localhost

      sensors:
        - name: example-1
          driver: example
          config:
            id: "1"
            amplitude: 2
            tags:
              location: outside

        - name: neurio-house
          driver: neurio
          config:
            id: "0x1234"
            client_id: "my_client_id"
            client_secret: "my_client_secret"
            tags:
              location: 'house'
