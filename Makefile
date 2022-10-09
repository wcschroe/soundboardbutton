install:
	sudo systemctl stop soundboardbutton.service || true
	sudo cp ./soundboardbutton.service /etc/systemd/system/
	sudo chmod 640 /etc/systemd/system/soundboardbutton.service
	sudo systemctl daemon-reload
	sudo systemctl enable soundboardbutton.service
	sudo systemctl start soundboardbutton.service
