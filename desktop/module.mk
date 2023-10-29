.PHONY: desktop
desktop:
	cd desktop && npm install
	cd desktop && npm run start

.PHONY: desktop-dist
desktop-dist:
	cd desktop && npm install
	cd desktop && npm run package

.PHONY: desktop-run-dist
desktop-run-dist:
	desktop/dist/RacineDesktop-0.1.0.AppImage
