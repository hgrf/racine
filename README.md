# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/HolgerGraef/MSM/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                               |    Stmts |     Miss |   Cover |   Missing |
|----------------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| app/\_\_init\_\_.py                                                                |       63 |       14 |     78% |61-71, 82-86 |
| app/auth/\_\_init\_\_.py                                                           |        3 |        0 |    100% |           |
| app/auth/forms.py                                                                  |       15 |        0 |    100% |           |
| app/auth/views.py                                                                  |       75 |       59 |     21% |12-67, 72-94, 99-109, 116-120 |
| app/browser/\_\_init\_\_.py                                                        |        3 |        0 |    100% |           |
| app/browser/views.py                                                               |      300 |      247 |     18% |58-78, 99-125, 129-142, 146-162, 184-240, 260, 284-331, 349-374, 391-418, 426-486, 495-520, 528-569, 577-584, 591-626, 630-634 |
| app/config.py                                                                      |       28 |        0 |    100% |           |
| app/decorators.py                                                                  |       12 |        3 |     75% |     10-12 |
| app/emailing.py                                                                    |       17 |       11 |     35% |9-19, 26-29 |
| app/main/\_\_init\_\_.py                                                           |        3 |        0 |    100% |           |
| app/main/errors.py                                                                 |       19 |        7 |     63% |9, 14, 19, 24-28 |
| app/main/forms.py                                                                  |       21 |        3 |     86% |     26-28 |
| app/main/views.py                                                                  |      433 |      346 |     20% |31-46, 59-144, 163-176, 188-220, 234-235, 241-281, 294-345, 351-360, 366-373, 379-386, 392-423, 429-436, 442-449, 455-481, 487-536, 542-563, 569-599, 605-629, 635-662, 668-674, 681, 685-690, 694-699, 749-774, 780-839 |
| app/models.py                                                                      |      268 |      125 |     53% |15-63, 67-92, 103-109, 136, 140, 144, 147, 150-151, 155-165, 172, 183, 215-232, 235, 248-266, 272, 287-297, 316, 319-325, 328, 354-379, 383-391, 416, 427, 440, 453, 469, 473-488 |
| app/printdata/\_\_init\_\_.py                                                      |        3 |        0 |    100% |           |
| app/printdata/forms.py                                                             |        8 |        0 |    100% |           |
| app/printdata/views.py                                                             |       43 |       34 |     21% |     12-52 |
| app/profile/\_\_init\_\_.py                                                        |        3 |        0 |    100% |           |
| app/profile/forms.py                                                               |       24 |        6 |     75% |37-38, 41-45, 48-49 |
| app/profile/views.py                                                               |       55 |       40 |     27% |12-23, 29-38, 44-70 |
| app/settings/\_\_init\_\_.py                                                       |        3 |        0 |    100% |           |
| app/settings/forms.py                                                              |       29 |        0 |    100% |           |
| app/settings/views.py                                                              |      176 |      132 |     25% |21, 28-54, 63-79, 86-135, 142-174, 185-193, 197-210, 219-269, 282-285 |
| app/smbinterface.py                                                                |       83 |       67 |     19% |29-51, 57-71, 92-107, 111-143, 147, 152-169 |
| app/tests/\_\_init\_\_.py                                                          |        0 |        0 |    100% |           |
| app/tests/test\_main.py                                                            |       16 |        0 |    100% |           |
| app/usagestats.py                                                                  |       55 |       17 |     69% |21-22, 47, 57-85, 97-99 |
| app/validators.py                                                                  |       14 |        9 |     36% |6-7, 11-12, 16-21 |
| migrations/env.py                                                                  |       33 |       10 |     70% |43-47, 62-66, 88 |
| migrations/versions/1de13fd625b1\_added\_archived\_flag.py                         |        9 |        1 |     89% |        26 |
| migrations/versions/2fcf420c6c0c\_added\_path\_column\_to\_smbres.py               |        8 |        1 |     88% |        25 |
| migrations/versions/3d9e4225ecbd\_remove\_unique\_constraint\_from\_sample\_.py    |       12 |        1 |     92% |        50 |
| migrations/versions/4ca6d5b7b966\_initial\_migration.py                            |       28 |       10 |     64% |   126-135 |
| migrations/versions/5ae6e19e0a7b\_added\_column\_for\_inheriting\_data.py          |       12 |        3 |     75% |     27-29 |
| migrations/versions/9c070b1a9f8b\_add\_news.py                                     |       15 |        3 |     80% |     86-88 |
| migrations/versions/17c32bd785e3\_added\_size\_column\_to\_uploads\_table.py       |        8 |        1 |     88% |        25 |
| migrations/versions/31fd4405fcd2\_removed\_unused\_columns\_and\_tables.py         |       16 |        1 |     94% |        75 |
| migrations/versions/50d1a487c7ab\_added\_ordnum\_and\_datecreated\_to\_action\_.py |       12 |        2 |     83% |     28-29 |
| migrations/versions/70dd6f0306c4\_added\_last\_modified\_field\_to\_sample\_.py    |        8 |        1 |     88% |        25 |
| migrations/versions/86ec305ceaa7\_add\_collaborative\_sample\_flag.py              |        9 |        1 |     89% |        26 |
| migrations/versions/365a26270961\_added\_extension\_column\_to\_uploads\_table.py  |        8 |        1 |     88% |        25 |
| migrations/versions/506bb8a29f4d\_add\_mountpoint\_column.py                       |       12 |        1 |     92% |        40 |
| migrations/versions/3180b28651e3\_added\_isdeleted\_flag\_to\_sample.py            |        8 |        1 |     88% |        25 |
| migrations/versions/362505d00f1a\_repair\_broken\_heir\_column.py                  |       15 |        1 |     93% |        47 |
| migrations/versions/449283d5217f\_added\_sample\_description\_column.py            |        8 |        1 |     88% |        25 |
| migrations/versions/591022583d54\_added\_hash\_column\_to\_uploads\_table.py       |        8 |        1 |     88% |        25 |
| migrations/versions/578518528886\_added\_ownership\_to\_actions.py                 |       13 |        3 |     77% |     28-30 |
| migrations/versions/a45942d815f\_added\_upload\_table.py                           |        8 |        1 |     88% |        35 |
| migrations/versions/cb354c75d49\_added\_activity\_table.py                         |       10 |        2 |     80% |     52-53 |
|                                                                          **TOTAL** | **2032** | **1167** | **43%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/HolgerGraef/MSM/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/HolgerGraef/MSM/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/HolgerGraef/MSM/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/HolgerGraef/MSM/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2FHolgerGraef%2FMSM%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/HolgerGraef/MSM/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.