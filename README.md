# DrivePulse for Home Assistant

Sensors and trip events from your car, sent by the DrivePulse app, with **no YAML to write**.

DrivePulse reads your car through an OBD2 adapter. This integration gives the app a private address (a webhook) in your Home Assistant, and turns what the app sends into a device per vehicle with its sensors. Everything stays between your phone and your Home Assistant: no account, no cloud, no server of ours in the middle.

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

Example: a notification when you arrive with less than a quarter of a tank.

```yaml
automation:
  - alias: "Low fuel on arrival"
    triggers:
      - trigger: event
        event_type: drivepulse_trip_end
    conditions:
      - condition: template
        value_template: "{{ trigger.event.data.fuel_level_pct is number and trigger.event.data.fuel_level_pct < 25 }}"
    actions:
      - action: notify.notify
        data:
          message: "{{ trigger.event.data.vehicle }}: {{ trigger.event.data.fuel_level_pct }} % fuel left"
```

## Install

### 1. With HACS (as a custom repository)

1. In Home Assistant open **HACS**.
2. Menu (three dots, top right) → **Custom repositories**.
3. Repository: `https://github.com/davideguida0093/drivepulse-home-assistant` · Type: **Integration** → **Add**.
4. Find **DrivePulse** in HACS, open it and select **Download**.
5. **Restart Home Assistant.**

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
