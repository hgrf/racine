.PHONY: desktop
desktop:
	cd desktop && npm install
	cd desktop && npm run start

.PHONY: desktop-dist-win
desktop-dist-win:
	cd desktop && npm install
	# #--env-file <(env | grep -iE 'DEBUG|NODE_|ELECTRON_|YARN_|NPM_|CI|CIRCLE|TRAVIS_TAG|TRAVIS|TRAVIS_REPO_|TRAVIS_BUILD_|TRAVIS_BRANCH|TRAVIS_PULL_REQUEST_|APPVEYOR_|CSC_|GH_|GITHUB_|BT_|AWS_|STRIP|BUILD_') \
	docker run --rm -ti \
		--env ELECTRON_CACHE="/root/.cache/electron" \
		--env ELECTRON_BUILDER_CACHE="/root/.cache/electron-builder" \
		-v ${PWD}:/project \
		-v ${PWD}/desktop/node-modules:/project/node_modules \
		-v ~/.cache/electron:/root/.cache/electron \
		-v ~/.cache/electron-builder:/root/.cache/electron-builder \
		electronuserland/builder:wine

.PHONY: desktop-dist
desktop-dist:
	cd desktop && npm install
	cd desktop && npm run package

.PHONY: desktop-run-dist
desktop-run-dist:
	cd desktop && ./dist/RacineDesktop-0.1.0.AppImage
