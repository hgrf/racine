flake8-badge:
	printf " \
		\rimport os\n \
		\rfrom genbadge.utils_flake8 import get_flake8_badge, get_flake8_stats\n \
		\rbadge = get_flake8_badge(get_flake8_stats('./reports/flake8/flake8stats.txt'))\n \
		\rprint(f'{badge.right_txt}@{badge.color}')\n \
		\r\n" | python

eslint-badge:
	OUTPUT=`cd js && npx eslint --max-warnings 0 .`; \
		if [ "$$?" -eq 0 ]; then \
			echo "pass@green"; \
		else \
			echo "$$OUTPUT" | \
				grep -E "problems? \(" | \
				(IFS='()' read _ SUMMARY; echo $$SUMMARY) | \
				(read ERRORS _ WARNINGS _; echo $$ERRORS C, $$WARNINGS W@\
					`if [ $$ERRORS -eq 0 ]; then echo orange; else echo red; fi`\
				); \
		fi

