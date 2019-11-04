# Device proxy demo

⚠️ _This project is Work in Progress, please test whether it works for your use case, and if any issue found, feed back to us, e.g. by opening an issue._ ⚠️

There are occasions, when not all your balenaCloud devices on a single network have direct internet connection. This project is aiming to help with that case:

* example how to set up a socks5+DNS proxy service on devices using [glider][glider]
* adding NTP server to provide a time service for the isolated devices with [chrony][chrony]
* the proxy service started on demand, enabled by an environment variable, see below
* the devices connecting to this to be proxied need configuration changes as shown below
* the proxied device running a service (here a simple [Magic 8-ball 🎱][magic-8] web service), that can be used to test proxying.

## Usage

Both the gateway and the proxied devices require some setup.

### Gateway

* To enable the proxy, set `START_PROXY` environment variable for any value. This could be a service env var (in this example for the `proxy` service), or a device env var. See more about the env vars [in our docs][envvar]. Set this on the device level (not the application level)
* You can also use `VERBOSE` (set to any value) to run the proxy with verbose output (default is not being verbose)
* Setting `DEBUG` can allow you to debug the proxy service better if for some reason the proxy stops: it stops the service from restarting, and you can investigate the running container and find any possible issue.

The gateway device will run 3 services (through 3 servers):

* socks5 proxy, for network communication,
* DNS proxy, for domain name resolution,
* NTP server, for network time

Due to the way DNS resolution works, the gateway is currently can be access by the client only by the gateway's IP address (and not possible to use its `.local` address). This requires static IP setting.

For this, the gateway should have either:

* static IP assigned by the DHCP server on the isolated network, or
* set static IP through the NetworkManager. You can either see how it's done [in our documentation][nmstatic], or in the NetworkManager documentation. One simple way to do that in many cases is to expand an existing NetworkManager configuration's `[ipv4]`

```
[ipv4]
method=auto
addresses=x.y.z.w/32
```

## Client

The client side need changes to two files:

* one to set up the socks5 proxy through `redsocks.conf`
* one to point the the DNS and NTP services to the gateway device as well through the `config.json`

### redsocks.conf example

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
 ip = "x.y.z.w";
 port = 1080;
}
```
where the `x.y.z.w` is the static IP set for the connecting devices.

This configuration needs to be added at the `resin-boot` partition's `/system-proxy/redsocks.conf` on an SD card or `/mnt/boot/system-proxy/redsocks.conf` at runtime (the `system-proxy` folder might need to be created), or use the supervisor API to set it ([see our docs][host-config]), but for this latter the device has to be reachable when the setting is applied.


### config.json changes

The `config.json` needs to be ahhandled carefully, as if the file editing results in an invalid `json` file, the client device won't run correctly.

Two entries are needed to be added (in both cases `x.y.z.w` is the gateway's static IP as earlier):

* `"dnsServers": "x.y.z.w#5300"` to set the DNS server to the gateway
* `"ntpServers": "x.y.z.w"` to point the NTP client on the device to the NTP server run on the gateway.

This can be added to the end of the `config.json`, let's say the default file (on `resin-boot` partition, or at `/mnt/boot/` at runtime) looks like this (with the midle snipped for clarity):

```
{
    "applicationName": "applicationname",
...[snip]...
    "apiKey": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```
then after modifications it would e.g. look like this (if the gateway's IP is `10.0.1.7` for example):
```
{
    "applicationName": "applicationname",
...[snip]...
    "apiKey": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "dnsServers": "10.0.1.7#5300",
    "ntpServers": "10.0.1.7"
}
```
Please note the commas after each entry! To check whether your edits are likely connect, run the `config.json` file through [`jq`][jq] such as:
```
# jq '.dnsServers, .ntpServers' config.json
"10.0.1.7#5300"
"10.0.1.7"
```
If it results in two lines and those are as they should be, your modifications should be correct.

## Demoing

To demo this project:

* push this to your test application
* deploy 2 devices to the application as follows:
  * first, for one device, set a static IP (as above), and once the application is running, enable `START_PROXY` (and mayebe `VERBOSE`) as service env vars for the `proxy` service. This will be your gateway, you should see logs of the proxy starting.
  * then for the client device, on the provisioning media (SD card, USB disk, as relevant) add a `redsocks.conf` file as described above, updating the `x.y.z.w` value from the gateway's static up, as well as modify the `config.json` likewise.
* when the second device is then provisioned:
  * the client device should come online and download the application
  * the gateway device should show in the logs that something's connected (if enabled `VERBOSE`)
  * once the `some_server` service is running enable the Public Device URL, and open that link from the dashboard, should be able to see the results
  * on the gateway device, if you stop the `proxy` service, the second device should get disconnected; If the service is started up again, the client should reconnect

[envvar]: https://www.balena.io/docs/learn/manage/serv-vars/#environment-and-service-variables "Environment and service variables"
[glider]: https://github.com/nadoo/glider "glider project page on GitHub"
[chrony]: https://chrony.tuxfamily.org/ "chrony home page"
[host-config]: https://www.balena.io/docs/reference/supervisor/supervisor-api/#patch-v1devicehost-config "host-config supervisor API docs"
[magic-8]: https://en.wikipedia.org/wiki/Magic_8-Ball "Magic 8-Ball on Wikipedia"
[nmstatic]: https://www.balena.io/docs/reference/OS/network/2.x/#setting-a-static-ip "Networking: Setting a Static IP"
[jq]: https://stedolan.github.io/jq/ "jq home page"
