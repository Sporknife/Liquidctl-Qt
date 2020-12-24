# Device support
- Describes which devices have been added to\ the JSON file and have to add a new device IF its supported by `liquidctl`
- Every device dictionary must contain info written below
* Template
```
{
  "description":  str,  # device.description  
  "vendor_id":    str,  # device.vendor_id
  "product_id":   str,  # device.product_id
  "bus":          str,  # device.bus
}
```

## Fan/Led controllers

* Template
```
{
  "description":  str,    # device.description  
  "vendor_id":    int,    # device.vendor_id
  "product_id":   int,    # device.product_id
  "bus":          str,    # device.bus,
  
  "fan_control":  bool,   # if device supports controlling fans
  "max_fans":     int,    # maximum amount of connected fans
  "led_control":  bool,   # if device supports controlling fans
  "max_leds":     int,    # maximum amount of connected leds
  "microphone":   bool    # if device has a microphone for noise level
}
```


## Liquidcoolers
## Ram sticks
## GPU's
