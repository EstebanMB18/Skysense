# Contratos MQTT SkySense

## Topics
- `skysense/{stationId}/telemetry`
- `skysense/{stationId}/health`
- `skysense/{stationId}/events`
- `skysense/{stationId}/cmd` (reservado)

## telemetry
```json
{
  "schema_version":"1.0",
  "message_id":"uuid",
  "station_id":"SKY-001",
  "timestamp_utc":"2026-11-04T12:00:00Z",
  "temperature_c":22.4,
  "humidity_pct":56.0,
  "pressure_hpa":1016.2,
  "wind_speed_ms":13.2,
  "wind_direction_deg":270,
  "density_altitude_ft":1240,
  "quality_flag":"VALID"
}
```
