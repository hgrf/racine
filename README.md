# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/hgrf/racine/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                               |    Stmts |     Miss |   Cover |   Missing |
|----------------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| app/\_\_init\_\_.py                                                                |       46 |        3 |     93% | 25-26, 43 |
| app/api/\_\_init\_\_.py                                                            |        9 |        0 |    100% |           |
| app/api/actions.py                                                                 |       92 |       45 |     51% |89-90, 115-122, 144-150, 171-202, 225-248 |
| app/api/common.py                                                                  |        4 |        0 |    100% |           |
| app/api/emailing.py                                                                |       46 |       23 |     50% |29-51, 76-102 |
| app/api/errors.py                                                                  |       11 |        0 |    100% |           |
| app/api/fields.py                                                                  |      103 |       56 |     46% |31-36, 40-45, 155-177, 182-207, 231-263 |
| app/api/samples.py                                                                 |      117 |       58 |     50% |31, 38, 47-52, 99-109, 129-132, 159-161, 188-190, 194-200, 224-258 |
| app/api/shares.py                                                                  |       65 |       24 |     63% |53-54, 56, 60, 73, 100-125 |
| app/api/users.py                                                                   |       73 |       29 |     60% |55, 69-71, 76, 99-103, 138-189 |
| app/auth/\_\_init\_\_.py                                                           |        3 |        0 |    100% |           |
| app/auth/forms.py                                                                  |       15 |        0 |    100% |           |
| app/auth/views.py                                                                  |       71 |       34 |     52% |28, 34-36, 45, 66-88, 93-103, 110-114 |
| app/browser/\_\_init\_\_.py                                                        |        3 |        0 |    100% |           |
| app/browser/views.py                                                               |      308 |      252 |     18% |58-78, 100-125, 133-151, 155-168, 172-188, 211-245, 266, 275-278, 282-293, 314-343, 360-385, 403-431, 439-500, 509-534, 542-583, 591-598, 605-641, 645-649 |
| app/common.py                                                                      |        8 |        0 |    100% |           |
| app/config.py                                                                      |       40 |        0 |    100% |           |
| app/decorators.py                                                                  |       12 |        3 |     75% |     10-12 |
| app/emailing.py                                                                    |       19 |       12 |     37% |21-22, 27-34, 38-39 |
| app/main/\_\_init\_\_.py                                                           |        5 |        0 |    100% |           |
| app/main/ajaxviews/\_\_init\_\_.py                                                 |        3 |        0 |    100% |           |
| app/main/ajaxviews/sample.py                                                       |       27 |       18 |     33% |     13-35 |
| app/main/ajaxviews/search.py                                                       |       13 |        7 |     46% |     10-31 |
| app/main/ajaxviews/tree.py                                                         |       14 |        7 |     50% |     11-19 |
| app/main/ajaxviews/welcome.py                                                      |       51 |       37 |     27% |    20-103 |
| app/main/errors.py                                                                 |       19 |        6 |     68% |9, 19, 24-28 |
| app/main/forms.py                                                                  |       34 |        1 |     97% |        48 |
| app/main/views.py                                                                  |       40 |       16 |     60% |30-33, 39-43, 49-50, 56-65 |
| app/models/\_\_init\_\_.py                                                         |       13 |        0 |    100% |           |
| app/models/action.py                                                               |       18 |        3 |     83% |20, 24, 27 |
| app/models/activity.py                                                             |       30 |        3 |     90% |16, 32, 39 |
| app/models/handlers.py                                                             |       38 |       28 |     26% |8-59, 63-90, 103, 106-107 |
| app/models/news.py                                                                 |       46 |       24 |     48% |28-53, 57-65 |
| app/models/sample.py                                                               |       33 |        3 |     91% |40, 49, 53 |
| app/models/share.py                                                                |        9 |        1 |     89% |        12 |
| app/models/smbresource.py                                                          |       15 |        1 |     93% |        18 |
| app/models/tree.py                                                                 |       54 |       37 |     31% |24, 33-43, 47-76, 80-93, 97-102 |
| app/models/upload.py                                                               |       11 |        1 |     91% |        14 |
| app/models/user.py                                                                 |       82 |       20 |     76% |25, 60, 64, 74-75, 81-92, 97, 104, 110 |
| app/printdata/\_\_init\_\_.py                                                      |        3 |        0 |    100% |           |
| app/printdata/forms.py                                                             |        8 |        0 |    100% |           |
| app/printdata/views.py                                                             |       25 |       17 |     32% |     11-29 |
| app/profile/\_\_init\_\_.py                                                        |        3 |        0 |    100% |           |
| app/profile/forms.py                                                               |       24 |        6 |     75% |37-38, 41-45, 48-49 |
| app/profile/views.py                                                               |       59 |       41 |     31% |12, 18-29, 35-44, 50-77 |
| app/settings/\_\_init\_\_.py                                                       |        3 |        0 |    100% |           |
| app/settings/forms.py                                                              |       36 |        0 |    100% |           |
| app/settings/views.py                                                              |      144 |      108 |     25% |19-49, 61, 73-94, 106-124, 129-137, 141-154, 163-213, 226-229 |
| app/smbinterface.py                                                                |       84 |       67 |     20% |29-51, 57-71, 94-110, 114-145, 149, 154-173 |
| app/tests/\_\_init\_\_.py                                                          |        0 |        0 |    100% |           |
| app/tests/test\_api.py                                                             |       60 |        2 |     97% |     61-62 |
| app/tests/test\_main.py                                                            |       26 |        0 |    100% |           |
| app/usagestats.py                                                                  |       55 |       35 |     36% |27-85, 90-100 |
| app/validators.py                                                                  |       14 |        5 |     64% |     16-21 |
| app/version.py                                                                     |       12 |        1 |     92% |        15 |
| migrations/env.py                                                                  |       33 |       10 |     70% |43-47, 62-66, 88 |
| migrations/versions/1de13fd625b1\_added\_archived\_flag.py                         |        9 |        1 |     89% |        26 |
| migrations/versions/2fcf420c6c0c\_added\_path\_column\_to\_smbres.py               |        8 |        1 |     88% |        25 |
| migrations/versions/3d9e4225ecbd\_remove\_unique\_constraint\_from\_sample\_.py    |       12 |        1 |     92% |        51 |
| migrations/versions/4ca6d5b7b966\_initial\_migration.py                            |       28 |       10 |     64% |   129-138 |
| migrations/versions/5ae6e19e0a7b\_added\_column\_for\_inheriting\_data.py          |       12 |        3 |     75% |     27-29 |
| migrations/versions/9c070b1a9f8b\_add\_news.py                                     |       15 |        3 |     80% |     91-93 |
| migrations/versions/17c32bd785e3\_added\_size\_column\_to\_uploads\_table.py       |        8 |        1 |     88% |        25 |
| migrations/versions/31fd4405fcd2\_removed\_unused\_columns\_and\_tables.py         |       16 |        1 |     94% |        77 |
| migrations/versions/50d1a487c7ab\_added\_ordnum\_and\_datecreated\_to\_action\_.py |       12 |        2 |     83% |     28-29 |
| migrations/versions/70dd6f0306c4\_added\_last\_modified\_field\_to\_sample\_.py    |        8 |        1 |     88% |        25 |
| migrations/versions/71c1f7625171\_add\_user\_tokens.py                             |       12 |        3 |     75% |     27-29 |
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
| migrations/versions/e5dcaf21bbf0\_smb\_port\_and\_domain.py                        |       14 |        3 |     79% |     30-32 |
|                                                                          **TOTAL** | **2442** | **1087** | **55%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/hgrf/racine/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/hgrf/racine/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/hgrf/racine/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/hgrf/racine/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fhgrf%2Fracine%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/hgrf/racine/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.