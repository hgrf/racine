install-ckeditor:
	# clone CKEditor 4.9.2
	rm -rf /tmp/ckeditor4
	git clone -b 4.9.2 --depth 1 https://github.com/ckeditor/ckeditor4.git /tmp/ckeditor4

	# add scayt plugin
	git clone -b release.4.9.2.0 --depth 1 \
		https://github.com/WebSpellChecker/ckeditor-plugin-scayt.git \
		/tmp/ckeditor4/plugins/scayt
	cp patches/scayt.patch /tmp/ckeditor4/plugins/scayt/scayt.patch
	cd /tmp/ckeditor4/plugins/scayt && git apply scayt.patch
	rm /tmp/ckeditor4/plugins/scayt/scayt.patch

	# add wsc plugin
	git clone -b release.4.9.5 --depth 1 \
		https://github.com/WebSpellChecker/ckeditor-plugin-wsc.git \
		/tmp/ckeditor4/plugins/wsc

	# add pastefromexcel plugin
	git clone \
		https://github.com/devlog/pastefromexcel.git \
		/tmp/ckeditor4/plugins/pastefromexcel
	cd /tmp/ckeditor4/plugins/pastefromexcel && \
		git checkout 74c5b19d68c4d0f2a5e781e3d27208c5379d5195

	# add imagerotate plugin
	git clone \
		https://github.com/liias/imagerotate.git \
		/tmp/ckeditor4/plugins/imagerotate
	cd /tmp/ckeditor4/plugins/imagerotate && \
		git checkout f2ba8746bcf0b31df4791008f2bf37ba7e958aca

	# remove BOM from build.sh
	dos2unix /tmp/ckeditor4/dev/builder/build.sh

	# build CKEditor release
	cp patches/build-config.js /tmp/ckeditor4/dev/builder/build-config.js
	cd /tmp/ckeditor4 && \
		bash ./dev/builder/build.sh \
			-s --no-zip --no-tar --build-config build-config.js

	# java -jar /tmp/ckeditor4/dev/builder/ckbuilder/2.3.2/ckbuilder.jar \
	#	--build-skin --overwrite \
	#	/tmp/ckeditor4/skins/moono-lisa \
	#	/tmp/ckeditor4/dev/builder/release/ckeditor/skins/moono-lisa
	
	# apply patch to image plugin
	# c.f. https://github.com/hgrf/racine/commit/0cb962ec38ab3ea627bf2ed9f92d46f3ca2b27d2
	#      https://github.com/hgrf/racine/commit/7bebdfd730a61df0cdcbc04d9711e11ef3b80cbf
	#      https://github.com/hgrf/racine/commit/e98b8fa093778f0a1331f1d4b56619d669f9e8a5
	#      https://github.com/hgrf/racine/commit/cac9cf5bd1cba27551b3335998692a9ba072e29e
	#      https://github.com/hgrf/racine/commit/b2940d7d35fd2a725f88d394e815c1bc57f6d10f
	#      https://github.com/hgrf/racine/commit/276a495413d6654cad1695cd1ef33daa558f3fa7
	#      https://github.com/hgrf/racine/commit/3f33c7f58e41eec70f8749d756aaae5f5755a348
	#      https://github.com/hgrf/racine/commit/7791aa8db771323ed8a1997beb50ddc17583b460
	cp patches/image.patch /tmp/ckeditor4/plugins/image/plugin.patch
	cd /tmp/ckeditor4 && git apply plugins/image/plugin.patch
	rm /tmp/ckeditor4/plugins/image/plugin.patch

	# apply patch to imagerotate plugin
	# c.f. https://github.com/hgrf/racine/commit/627937daf81687278c8d339fa1bfaf0a1e71caa8
	#      https://github.com/hgrf/racine/commit/56471eaf168d4f34e930368f95e8b330b4bb8d90
	#      https://github.com/hgrf/racine/commit/109e8c57fbb0655245160cc42e0bc1d871c9dabd
	#      https://github.com/hgrf/racine/commit/e9af7953866a6f26fd30a96f3293f2be0d192ce3
	cp patches/imagerotate/plugin.patch /tmp/ckeditor4/plugins/imagerotate/plugin.patch
	cd /tmp/ckeditor4/plugins/imagerotate && git apply plugin.patch
	rm /tmp/ckeditor4/plugins/imagerotate/plugin.patch

	# apply patch to link plugin
	# c.f. https://github.com/hgrf/racine/commit/0cb962ec38ab3ea627bf2ed9f92d46f3ca2b27d2
	#      https://github.com/hgrf/racine/commit/7bebdfd730a61df0cdcbc04d9711e11ef3b80cbf
	#      https://github.com/hgrf/racine/commit/22e0ae16e74488dea63e59a69bb3d74aaac3b972
	#      https://github.com/hgrf/racine/commit/cac9cf5bd1cba27551b3335998692a9ba072e29e
	#      https://github.com/hgrf/racine/commit/b2940d7d35fd2a725f88d394e815c1bc57f6d10f
	#      https://github.com/hgrf/racine/commit/7791aa8db771323ed8a1997beb50ddc17583b460
	cp patches/link.patch /tmp/ckeditor4/plugins/link/plugin.patch
	cd /tmp/ckeditor4 && git apply plugins/link/plugin.patch
	rm /tmp/ckeditor4/plugins/link/plugin.patch

	# apply patch to save plugin
	# c.f. https://github.com/hgrf/racine/commit/e98b8fa093778f0a1331f1d4b56619d669f9e8a5
	#      https://github.com/hgrf/racine/commit/cac9cf5bd1cba27551b3335998692a9ba072e29e
	#      https://github.com/hgrf/racine/commit/0f6fe60cd646d7e95b0330b246ad7c7c1b968aae
	cp patches/save/plugin.patch /tmp/ckeditor4/plugins/save/plugin.patch
	cd /tmp/ckeditor4 && git apply plugins/save/plugin.patch
	rm /tmp/ckeditor4/plugins/save/plugin.patch

	# copy build to Racine
	rm -rf app/static/ckeditor
	cp -r /tmp/ckeditor4/dev/builder/release/ckeditor app/static/ckeditor

	# add unminified source of image plugin (dialog)
	cp app/static/ckeditor/plugins/image/dialogs/image.js \
		app/static/ckeditor/plugins/image/dialogs/image.js.old
	cp /tmp/ckeditor4/plugins/image/dialogs/image.js \
		app/static/ckeditor/plugins/image/dialogs/image.js

	# add unminified source of imagerotate plugin
	cp -r /tmp/ckeditor4/plugins/imagerotate \
		app/static/ckeditor/plugins/imagerotate

	# add unminified source of link plugin (dialog)
	cp app/static/ckeditor/plugins/link/dialogs/link.js \
		app/static/ckeditor/plugins/link/dialogs/link.js.old
	cp /tmp/ckeditor4/plugins/link/dialogs/link.js \
		app/static/ckeditor/plugins/link/dialogs/link.js

	# add unminified source of save plugin
	cp -r /tmp/ckeditor4/plugins/save app/static/ckeditor/plugins/save

	# add missing icons
	cp patches/save/icons/hidpi/closebtn.png \
		app/static/ckeditor/plugins/save/icons/hidpi/closebtn.png
	cp patches/save/icons/closebtn.png app/static/ckeditor/plugins/save/icons/closebtn.png
	cp patches/save/icons/loader.gif app/static/ckeditor/plugins/save/icons/loader.gif

	# add (superfluous) files
	cp /tmp/ckeditor4/plugins/pastefromexcel/.editorconfig \
		app/static/ckeditor/plugins/pastefromexcel/.editorconfig
	cp /tmp/ckeditor4/plugins/pastefromexcel/.gitignore \
		app/static/ckeditor/plugins/pastefromexcel/.gitignore
	cp /tmp/ckeditor4/plugins/pastefromexcel/.jscsrc \
		app/static/ckeditor/plugins/pastefromexcel/.jscsrc
	cp /tmp/ckeditor4/plugins/pastefromexcel/.jshintrc \
		app/static/ckeditor/plugins/pastefromexcel/.jshintrc
	mkdir app/static/ckeditor/plugins/pastefromexcel/tests
	cp /tmp/ckeditor4/plugins/pastefromexcel/tests/pastefromexcel.js \
		app/static/ckeditor/plugins/pastefromexcel/tests/pastefromexcel.js

	# install custom plugins
	cp -r patches/fb app/static/ckeditor/plugins/fb

	# apply various patches
	cp patches/README.md app/static/ckeditor/README.md
	cp patches/config.js app/static/ckeditor/config.js
	cp patches/build-config.js app/static/ckeditor/build-config.js
	cp patches/pastefromexcel.js app/static/ckeditor/plugins/pastefromexcel/tests/pastefromexcel.js
	cp patches/imagerotate/NOTES.md app/static/ckeditor/plugins/imagerotate/NOTES.md
	python patches/langorder.py
	python patches/timestamp.py

	# remove unneeded files
	rm -rf app/static/ckeditor/.github
	rm -rf app/static/ckeditor/samples
	rm -rf app/static/ckeditor/skins/kama
	rm -rf app/static/ckeditor/skins/moono
	rm app/static/ckeditor/lang/_translationstatus.txt
	rm app/static/ckeditor/plugins/imagerotate/README.md

	# replace strings
	sed -i 's/px!/px !/g' app/static/ckeditor/skins/moono-lisa/editor.css
	sed -i 's/:url/: url/g' app/static/ckeditor/skins/moono-lisa/editor.css
	sed -i 's/important}/important;}/g' app/static/ckeditor/skins/moono-lisa/editor.css
	sed -i 's/icon{/icon {/g' app/static/ckeditor/skins/moono-lisa/editor.css
	sed -i 's/cke_menubutton_icon {/cke_menubutton_icon{/g' app/static/ckeditor/skins/moono-lisa/editor.css

	# fix line endings
	find app/static/ckeditor -type f \
		\( \
			! -iname "CHANGES.md" \
			! -path "app/static/ckeditor/LICENSE.md" \
			! -iname "contents.css" \
			! -iname "styles.js" \
			! -iname "_translationstatus.txt" \
			! -path "app/static/ckeditor/plugins/scayt/*.md" \
			! -path "app/static/ckeditor/plugins/scayt/dialogs/toolbar.css" \
			! -path "app/static/ckeditor/plugins/wsc/*.md" \
			! -path "app/static/ckeditor/plugins/wsc/dialogs/*.html" \
			! -path "app/static/ckeditor/plugins/wsc/dialogs/wsc.css" \
			! -path "app/static/ckeditor/plugins/wsc/dialogs/wsc.js" \
		\) -print0 | xargs -0 dos2unix --keep-bom

	# clean up git repo
	rm -rf /tmp/ckeditor4
