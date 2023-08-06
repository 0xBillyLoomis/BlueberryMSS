# Blueberry Modded Server Script

BlueberryMSS is a modded minecraft server python script for easier server management, currently it relies on reading a .toml file for a version number, comparing it to the current server version then pulling a compiled server pack .zip to the server, removes old versions of mods, then copies all the mods over. Removing old versions of mods first is currently necessary as most mod developers modify the version number in the file name and as such it wouldn't overwrite by default. This is just the start, eventually this script will pull mods directly from CurseForge using the API and gracefully handle the updating of mods.




## Roadmap

- Add support for handling the entire server start and stop process from start to finish.

- Add support for updating modpacks via the CuseForge and Modrinth API(s)

- Add additional python script to support downloading and configuring new modded minecraft servers.

- Better, easier to modify configuration file for non-tech savy users


## License

[Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/)

