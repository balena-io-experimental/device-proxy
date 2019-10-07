# Device proxy demo

⚠️ _This project is Work in Progress, please test whether it works for your use case, and if any issue found, feed back to us, e.g. by opening an issue._ ⚠️

There are occasions, when not all your balenaCloud devices on a single network have direct internet connection. This project is aiming to help with that case:

* example how to set up a socks5 proxy service on devices using [glider][glider]
* the proxy service started on demand, enabled by an environment variable, see below
* the devices connecting to this to be proxied need a configuration as shown below
* the proxied device running a service (here a simple [Magic 8-ball 🎱][magic-8] web service), that can be used to test proxying.

## Usage

* To enable the proxy, set `START_PROXY` environment variable for any value. This could be a service env var (in this examplefor the `proxy` service), or a device env var. See more about the env vars [in our docs][envvar]. Set this on the device level (not the application level)
* You can also use `VERBOSE` (set to any value) to run the proxy with verbose output (default is not being verbose)
* Setting `DEBUG` can allow you to debug the proxy service better if for some reason the proxy stops: it stops the service from restarting, and you can investigate the running container and find any possible issue.

## redsocks.conf example

```
base {
 log_debug = off;
 log_info = on;
 log = stderr;
 daemon = off;
 redirector = iptables;
}

redsocks {
 type = socks5;
 ip = "otherdevice.local";
 port = 1080;
}
```
where the `otherdevice.local` can be e.g. your gateway device's `shortUUID.local` address (as default for balenaOS devices; the short UUID is the first 7 digits of the UUID), or the `hostname.local` if e.g. updated the hostname using the supervisor API ([see our docs][host-config]). Or if, the gateway device is set up with a static IP, can set that static IP there for the connecting devices.

This configuration needs to be dropped in `/resin-boot/system-proxy/redsocks.conf` on an SD card or `/mnt/boot/system-proxy/redsocks.conf` at runtime (the `system-proxy` folder might need to be created), or use the supervisor API to set it ([see our docs][host-config]), but for this latter the device has to be reachable when the setting is applied.

## Demoing

To demo this:

* push this to your test application
* deploy 2 devices to the application
* for one device, enable `START_PROXY` (and mayeb `VERBOSE`) as service env vars for the `proxy` service. This will be your gateway, you should see logs of the proxy starting
* on the other device, add a `redsocks.conf` file as described above, updating the `otherdevice.local` to the `abcdef1.local` if e.g. the gateway device has short UUID of `abcdef1`. Reboot that device if it was added in runtime
* after reboot
  * the second device should come back online
  * the gateway device should show in the logs that something's connected (if enabled `VERBOSE`)
  * enable the Public Device URL, and open that link, should be able to see the results
  * on the gateway device, if you stop the `proxy` service, the second device should get disconnected; once the service is restart it should reconnect

[envvar]: https://www.balena.io/docs/learn/manage/serv-vars/#environment-and-service-variables "Environment and service variables"
[glider]: https://github.com/nadoo/glider "glider project page on GitHub"
[host-config]: https://www.balena.io/docs/reference/supervisor/supervisor-api/#patch-v1devicehost-config "host-config supervisor API docs"
[magic-8]: https://en.wikipedia.org/wiki/Magic_8-Ball "Magic 8-Ball on Wikipedia"