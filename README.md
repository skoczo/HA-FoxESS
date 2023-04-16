[![Release](https://github.com/skoczo/HA-FoxESS/actions/workflows/release.yaml/badge.svg)](https://github.com/skoczo/HA-FoxESS/actions/workflows/release.yaml)


Example config

sensor:
  - platform: sfoxess
    username: %put you username here%
    password: %password%
    device_id: %device id%
    import: true %if you want to import old data put true here%
    import_start_date: 01-01-2023 %put start import date here, you don't need to import all data%
