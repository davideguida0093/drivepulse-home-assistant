# DrivePulse for Home Assistant

Sensors and trip events from your car, sent by the DrivePulse app, with **no YAML to write**.

[![Open your Home Assistant instance and show this repository in the Marketplace.](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=davideguida0093&repository=drivepulse-home-assistant&category=integration)

DrivePulse reads your car through an OBD2 adapter. This integration gives the app a private address (a webhook) in your Home Assistant, and turns what the app sends into a device per vehicle with its sensors. The app sends data only to your Home Assistant, and only if you turn sending on: no account, no cloud, no server of ours in the middle.

> This integration replaces the YAML block the app's help page used to show. If you pasted that block into `configuration.yaml`, remove it before adding the integration, or you will have the same sensors twice.

## What you get

For each vehicle (named as in the app) one device, **without the VIN** (the app never sends it), with:

| Entity | What it is |
|---|---|
| Fuel level / Battery level | Fuel tank percentage, or the high-voltage battery charge of an electric car. Only the one your car reports appears. |
| Range | Estimated range, when the car gives it |
| Odometer | Total distance, ready for maintenance reminders |
| 12 V battery | The car's 12 V battery voltage |
| Coolant temperature | Engine coolant |
| Trouble codes | Number of fault codes; the codes themselves (for example `P0420`) are in the `codes` attribute |
| Last trip | Distance of the last trip. Duration, average and maximum speed, consumption are attributes |
| Trip in progress | On from the start of a trip to its end |
| Adapter connected | Whether the app is talking to the car right now |
| Fuel (litres), Speed, Engine speed | Appear when the car reports them; speed and engine speed are disabled by default (turn them on if you want them) |

When the car does not give a value, the entity shows **Unavailable** instead of a wrong number. The odometer, the range and the trouble codes keep their last known value between messages, because the app only sends them at the end of a trip.

### Events for automations

Two events are fired on the Home Assistant bus, so you can automate "the car left" and "the car arrived":

| Event | When | Data |
|---|---|---|
| `drivepulse_trip_start` | a trip starts | `vehicle`, `device_id`, `fuel_level_pct`, `odometer_km`, `battery_voltage`, ... |
| `drivepulse_trip_end` | a trip ends | the same, plus `trip` (distance, duration, average and maximum speed, consumption) |

Only the numbers above are sent: **no GPS position, no VIN, no addresses**. Home Assistant already knows where your phone is.

## Automation examples

Paste one in **Settings > Automations & scenes > Create automation > Create new automation**, then **⋮ > Edit in YAML**. In these examples the car is called "My car": use your car's name as Home Assistant shows it (a car called Golf has `sensor.golf_trouble_codes`). Replace `notify.notify` with your phone, for example `notify.mobile_app_marks_iphone`.

### Low fuel

At the end of a trip, when less than 20 % is left. On an electric car use `hv_soc_pct`.

```yaml
alias: "DrivePulse: low fuel"
triggers:
  - trigger: event
    event_type: drivepulse_trip_end
conditions:
  - condition: template
    value_template: >
      {{ trigger.event.data.fuel_level_pct is number
         and trigger.event.data.fuel_level_pct < 20 }}
actions:
  - action: notify.notify
    data:
      title: "Low fuel"
      message: >
        {{ trigger.event.data.vehicle }}:
        {{ trigger.event.data.fuel_level_pct | round(0) | int }} % left in the tank.
```

### New trouble code

Only codes that were not there before; the same code does not notify twice.

```yaml
alias: "DrivePulse: new trouble code"
triggers:
  - trigger: state
    entity_id: sensor.my_car_trouble_codes
conditions:
  - condition: template
    value_template: >
      {% set before = trigger.from_state.attributes.codes | default([])
         if trigger.from_state is not none else none %}
      {% set after = trigger.to_state.attributes.codes | default([]) %}
      {{ before is not none
         and trigger.from_state.state not in ['unknown', 'unavailable']
         and after | reject('in', before) | list | count > 0 }}
actions:
  - action: notify.notify
    data:
      title: "New trouble code"
      message: >
        {% set before = trigger.from_state.attributes.codes | default([]) %}
        {{ trigger.to_state.attributes.codes | reject('in', before) | join(', ') }}:
        open DrivePulse to see what it means and whether you can drive.
```

### Low 12 V battery

Below 12 V for more than a minute, so the dip while cranking does not count. The OBD reading is usually 0.2-0.4 V lower than a multimeter's.

```yaml
alias: "DrivePulse: low 12 V battery"
triggers:
  - trigger: numeric_state
    entity_id: sensor.my_car_12_v_battery
    below: 12
    for: "00:01:00"
actions:
  - action: notify.notify
    data:
      title: "Low 12 V battery"
      message: >
        {{ states('sensor.my_car_12_v_battery') }} V. With the engine off the
        battery is low on charge; with the engine running the alternator is not
        charging. Run the battery test in DrivePulse.
```

### Trip summary

```yaml
alias: "DrivePulse: trip summary"
triggers:
  - trigger: event
    event_type: drivepulse_trip_end
conditions:
  - condition: template
    value_template: >
      {{ trigger.event.data.trip is defined
         and trigger.event.data.trip.distance_km is number }}
actions:
  - action: notify.notify
    data:
      title: "{{ trigger.event.data.vehicle }}: trip finished"
      message: >
        {% set t = trigger.event.data.trip %}
        {{ '%.1f' | format(t.distance_km) }} km
        {%- if t.duration_min is number %} in {{ t.duration_min | round(0) | int }} min{% endif %}
        {%- if t.avg_speed_kmh is number %}, average {{ t.avg_speed_kmh | round(0) | int }} km/h{% endif %}
        {%- if t.avg_consumption_l_100km is number %}, {{ '%.1f' | format(t.avg_consumption_l_100km) }} l/100 km{% endif %}.
```

### Inspection reminder

First create a date helper: **Settings > Devices & services > Helpers > Create helper > Date and/or time**, name **Car inspection**, date only. Every time you arrive in the 30 days before that date, you get a reminder with the odometer.

```yaml
alias: "DrivePulse: inspection reminder"
triggers:
  - trigger: event
    event_type: drivepulse_trip_end
conditions:
  - condition: template
    value_template: >
      {% set ts = state_attr('input_datetime.car_inspection', 'timestamp') %}
      {% set days = ((ts - as_timestamp(today_at())) / 86400) | round(0) | int
         if ts is number else -1 %}
      {{ 1 <= days <= 30 }}
actions:
  - action: notify.notify
    data:
      title: "Inspection coming up"
      message: >
        {% set ts = state_attr('input_datetime.car_inspection', 'timestamp') %}
        {% set days = ((ts - as_timestamp(today_at())) / 86400) | round(0) | int %}
        {{ trigger.event.data.vehicle }}: the inspection is due
        in {{ days }} {{ 'day' if days == 1 else 'days' }}.
        {%- if trigger.event.data.odometer_km is number %}
        Odometer: {{ '{:,}'.format(trigger.event.data.odometer_km | round(0) | int) }} km.{% endif %}
```

### Dashboard card

**Edit dashboard > Add card > Manual**, paste:

```yaml
type: vertical-stack
cards:
  - type: tile
    entity: binary_sensor.my_car_trip_in_progress
    name: Driving
  - type: grid
    columns: 2
    square: false
    cards:
      - type: tile
        entity: sensor.my_car_fuel_level
        name: Fuel
      - type: tile
        entity: sensor.my_car_12_v_battery
        name: 12 V battery
      - type: tile
        entity: sensor.my_car_trouble_codes
        name: Trouble codes
      - type: tile
        entity: sensor.my_car_odometer
        name: Odometer
  - type: entities
    title: Last trip
    entities:
      - entity: sensor.my_car_last_trip
        name: Distance
      - type: attribute
        entity: sensor.my_car_last_trip
        attribute: duration_min
        name: Duration
        suffix: min
      - type: attribute
        entity: sensor.my_car_last_trip
        attribute: avg_consumption_l_100km
        name: Average consumption
        suffix: l/100 km
      - type: attribute
        entity: sensor.my_car_trouble_codes
        attribute: codes
        name: Codes
  - type: history-graph
    title: 12 V battery, last 7 days
    hours_to_show: 168
    entities:
      - entity: sensor.my_car_12_v_battery
```

The same examples, in English and Italian: [drivepulse.it/home-assistant_en](https://drivepulse.it/home-assistant_en).

## Install

### 1. With HACS

1. In Home Assistant open **HACS**.
2. Search for **DrivePulse**, open it and select **Download**.
3. **Restart Home Assistant.**

DrivePulse is in the HACS default list, so no custom repository is needed. On Home Assistant 2026.11 or later the same catalog is built in as **Settings > Marketplace**: search for DrivePulse there (or use the badge at the top of this page), the steps are the same. If you added it earlier as a custom repository, nothing changes: the installed integration keeps working and keeps receiving updates.

### 2. Add the integration

1. **Settings → Devices & services → Add integration → DrivePulse.**
2. Select **Submit.** Home Assistant shows the **webhook address**. Copy it.
   (You can see it again at any time: Settings → Devices & services → DrivePulse → **Configure**.)

### 3. Paste the address in the app

1. In the DrivePulse app open **Send to Home Assistant** in the settings, turn on **Send the data**, and paste the address in **Webhook address**.
2. Tap **Test send**: the app says the server answered. 
3. Drive. The device appears in Home Assistant with the first message of the first trip.

That is all. No YAML.

### Away from home

The phone is on mobile data while you drive, so a home address (`http://homeassistant.local:8123/...`) only works on your home Wi-Fi or through a VPN. The start of a trip (in front of the house) and the end (when the phone is back on Wi-Fi) normally arrive; the app retries them for ten minutes. To receive everything on the road:

- use a VPN such as Tailscale and the address with the VPN name or IP, **or**
- use the HTTPS address of your Home Assistant (Nabu Casa or your own domain): `https://<your address>/api/webhook/<id>`, and turn off **Local network only** in **Configure** (by default the webhook accepts only your local network).

The webhook id in the address is the secret: anyone who has it can send data to your Home Assistant. Do not publish it.

## Notes

- One device per vehicle **name**. If you rename a vehicle in the app, a new device appears; delete the old one in Home Assistant (**Settings > Devices & services > DrivePulse**, open the device, **Delete**): the integration forgets that vehicle, so it does not come back after a restart and no longer counts against the limit. A vehicle with a trip in progress cannot be deleted until the trip ends.
- Up to 20 vehicles per webhook; anything beyond that is ignored.
- Messages the integration does not know are accepted and ignored, so a newer app does not show errors.
- Needs Home Assistant 2024.12 or newer.

## Troubleshooting

| What the app shows | What it means |
|---|---|
| "Delivered" | Everything works. |
| "The server answered 404" | The webhook id is wrong, or the integration is not added. |
| "The server answered 400" | The message was not understood: update the integration. |
| "Address not reachable" | The phone cannot reach Home Assistant from where it is (see *Away from home*). |

Logs: `Settings → System → Logs`, filter `drivepulse`; for details add `logger: logs: custom_components.drivepulse: debug` to `configuration.yaml`.

## Development

```
pip install -r requirements_test.txt
pytest
```

## License

MIT, see [LICENSE](LICENSE).
