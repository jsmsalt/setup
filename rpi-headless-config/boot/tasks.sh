#!/bin/bash


# [SYSTEM]
SYSTEM_PASS="12345"

# [NETWORK]
WIFI_NAME[0]="WIFI"
WIFI_SSID[0]="WIFI"
WIFY_PASSWORD[0]="12345"
WIFI_STATIC[0]=180

# [TELEGRAM BOT NOTIFICATIONS]
BOT_TOKEN=""
BOT_CHAT_ID=""


# ******************** [STOP EDITING] ********************

CONFIG_FILE=/boot/tasks

STATIC_FILE=/etc/dhcpcd.conf
STATIC_FILE_BK=/etc/dhcpcd.bk

CONFIG_RPI_FILE=/boot/config.txt
CONFIG_RPI_FILE_BK=/boot/config.bk

FSTAB_FILE=/etc/fstab
FSTAB_FILE_BK=/etc/fstab.bk

WPA_FILE=/etc/wpa_supplicant/wpa_supplicant.conf

TASK_REBOOT=1
SYSTEM_USER=$(getent passwd {1000..60000} | cut -d: -f1 | head -1)
WIFI_INTERFACE=$(iw dev | awk '$1=="Interface"{print $2}')

write_config() {
	sed -i "s/\(${1} *= *\).*/\1${2}/" $CONFIG_FILE > /dev/null
}

read_config() {
	value=$(grep ${1} ${CONFIG_FILE} | cut -d '=' -f 2)
	if [ -z $value ]; then
		echo 1
	else
		echo $value
	fi
}

connected() {
	echo -e "GET http://google.com HTTP/1.0\n\n" | nc google.com 80 > /dev/null 2>&1
	if [ $? -eq 0 ]; then
	    echo 1
	else
	    echo 0
	fi
}

notify() {
	if [ $(connected) == 1 ]; then
		curl -X POST -H "Content-Type: application/json" -d '{"chat_id": "'"$BOT_CHAT_ID"'", "text": "'"$1"'", "disable_notification": true}' "https://api.telegram.org/bot$BOT_TOKEN/sendMessage"
    fi
}

reconnect() {
	systemctl restart wpa_supplicant > /dev/null
	sleep 1

	systemctl daemon-reload > /dev/null
	sleep 1

	systemctl restart dhcpcd > /dev/null
	sleep 2
}

config_wifi() {

	# Init
	printf "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1\n\n" > $WPA_FILE

	# Add connection
	for index in ${!WIFI_SSID[@]}; do
		echo -e "\nnetwork={" >> $WPA_FILE

		if [ ! -z "${WIFI_NAME[$index]}" ];then
			echo -e "\tid_str=\"${WIFI_NAME[$index]}\"" >> $WPA_FILE
		fi

		echo -e "\tssid=\"${WIFI_SSID[$index]}\"" >> $WPA_FILE

		if [ ! -z "${WIFY_PASSWORD[$index]}" ];then
			echo -e "\tpsk=\"${WIFY_PASSWORD[$index]}\"" >> $WPA_FILE
		else
			echo -e "\tkey_mgmt=NONE" >> $WPA_FILE
		fi

		if [ ! -z "${WIFY_PRIORITY[$index]}" ];then
			echo -e "\tpriority=\"${WIFY_PRIORITY[$index]}\"" >> $WPA_FILE
		fi

		echo -e "}" >> $WPA_FILE
	done

	reconnect

	# Setup static IP
	if [ ! -f $STATIC_FILE_BK ]; then
		cp $STATIC_FILE $STATIC_FILE_BK
	fi

	DHCPCD=$(cat $STATIC_FILE_BK)
	STATIC_CONNECTIONS=""

	for index in ${!WIFI_STATIC[@]}; do
		if [ ! -z "${WIFI_STATIC[$index]}" ]; then
			net_id=$(wpa_cli -i "$WIFI_INTERFACE" list_network | awk '!/DISABLED|bssid/' | awk "/${WIFI_SSID[$index]}/" | awk '{print $1}')
			
			if [ ! -z "$net_id" ]; then
				wpa_cli -i "$WIFI_INTERFACE" select_network "$net_id"

				COUNTER=0
				while [ -z $GATEWAY ] && [ $COUNTER -lt 7 ]
				do
				     GATEWAY=$(ip route | grep default | awk '{print $3}')
				     COUNTER=$[$COUNTER +1]
				     sleep 1
				done

				if [ ! -z "$GATEWAY" ]; then
					ROUTER_IP=$(printf "$GATEWAY" | cut -d"." -f1-3)
					STATIC_IP="$ROUTER_IP.${WIFI_STATIC[$index]}"
					STATIC_CONNECTIONS="${STATIC_CONNECTIONS}\n\nssid ${WIFI_SSID[$index]}\nstatic ip_address=${STATIC_IP}/24\nstatic routers=${GATEWAY}\nstatic domain_name_servers=${GATEWAY}"
				fi
			fi
		fi
	done

	if [ ! -z "$STATIC_CONNECTIONS" ]; then
		echo -e "${DHCPCD}\n\n${STATIC_CONNECTIONS}" > $STATIC_FILE
	fi

	reconnect
}


# Enable WIFI
if [ $(read_config "TASK_WIFI") == 0 ];then
	config_wifi
	if [ $(connected) == 1 ]; then
		write_config "TASK_WIFI" "1"
		CURRENT_SSID=$(iwgetid -r)
		CURRENT_LOCAL_IP=$(hostname -I)
		notify "Connected to $CURRENT_SSID network. My local IP: $CURRENT_LOCAL_IP"
	fi
fi


# Enable SSH
if [ $(read_config "TASK_SSH") == 0 ];then
	systemctl enable ssh > /dev/null
	sleep 2
	systemctl start ssh > /dev/null
	sleep 2
	write_config "TASK_SSH" "1"
fi


# Change password
if [ $(read_config "TASK_PASS") == 0 ] && [ ! -z "$SYSTEM_PASS" ];then
	printf "$SYSTEM_USER:$SYSTEM_PASS" | chpasswd
	write_config "TASK_PASS" "1"
fi


# NTFS disk support
if [ $(read_config "TASK_NTFS") == 0 ] && [ $(read_config "TASK_WIFI") == 1 ] && [ $(connected) == 1 ];then
	apt-get update -qq > /dev/null
	apt-get install -qq -y exfat-fuse ntfs-3g > /dev/null

	if [ $? == 0 ]; then
		write_config "TASK_NTFS" "1"
	fi
fi


# Mount HDD
if [ $(read_config "TASK_HDD") == 0 ];then
	HDD_UUID=$(ls -l /dev/disk/by-uuid | grep "sda1" | awk '{print $9}')
	if [ ! -z "$HDD_UUID" ]; then
		mkdir -p /media/hdd
		chmod -R -f 777 /media/hdd
		chown -R -f "$SYSTEM_USER" /media/hdd

		if [ ! -f $FSTAB_FILE_BK ]; then
			cp $FSTAB_FILE $FSTAB_FILE_BK
		fi

		FSTAB_CONTENT=$(cat $FSTAB_FILE_BK)

		printf "${FSTAB_CONTENT}\nUUID=$HDD_UUID	/media/hdd	auto	nofail,auto,noatime,rw,user,umask=000,dmask=000    0   0" > $FSTAB_FILE
		mount -a > /dev/null
		write_config "TASK_HDD" "1"
	fi
fi


# Increment USB power
if [ $(read_config "TASK_POWER") == 0 ];then
	if [ ! -f $CONFIG_RPI_FILE_BK ]; then
		cp $CONFIG_RPI_FILE $CONFIG_RPI_FILE_BK
	fi

	CONFIG_CONTENT=$(cat $CONFIG_RPI_FILE_BK)
	printf "${CONFIG_CONTENT}\n\nmax_usb_current=1" > $CONFIG_RPI_FILE
	write_config "TASK_POWER" "1"
fi


# Install docker
if [ $(read_config "TASK_DOCKER") == 0 ] && [ $(read_config "TASK_WIFI") == 1 ] && [ $(connected) == 1 ];then
	curl -sSL https://get.docker.com | sh > /dev/null
	apt install docker-compose | sh > /dev/null

	if [ $? == 0 ]; then
		groupadd docker
		usermod -aG docker "$SYSTEM_USER"
		write_config "TASK_DOCKER" "1"
		TASK_REBOOT=0
	fi
fi

if [ "$TASK_REBOOT" == "0" ]; then
	reboot
fi
