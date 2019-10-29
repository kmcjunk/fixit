# Fix it

A simple python script to manually boot strap networks and install nova-agent. For use with Rackspace Public Cloud. This can be used to easily salvage an image when it does not having a responding nova-agent.
Utilizes base python modules and works with all tested public images.
Tested on CentOS 7, CentOS 6, Ubuntu 18, Ubuntu 16 and Ubuntu 14

## Instructions
You will need to boot the server with a config-drive and supply this script as user data. If you are using supernova you can do the following
```
supernova $ENVIRONMENT boot --image $IMAGE --user-data path/to/fixit.py --config-drive true --flavor $FLAVOR $SEVER_NAME
```
If you opt to use the API directly, the following JSON payload should do it.
```
{
    "server": {
        "name": "$SERVER_NAME",
        "imageRef": "$IMAGE_UUID",
        "flavorRef": "$FLAVOR",
        "user_data": "path/to/fixit.py",
        "networks": [
            {
                "uuid": "00000000-0000-0000-0000-000000000000"
            },
            {
                "uuid": "11111111-1111-1111-1111-111111111111"
            }
        ],
        "config_drive": "true"
    }
}
```
