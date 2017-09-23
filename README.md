# analyticord

[![Supported Python versions](https://img.shields.io/pypi/pyversions/analyticord.svg)](https://pypi.org/project/analyticord)
[![License](https://img.shields.io/pypi/l/analyticord.svg)](https://choosealicense.com/licenses)
[![Documentation Status](https://readthedocs.org/projects/discordanalytics-python/badge/?version=latest)](http://discordanalytics-python.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/nitros12/module-python.svg?branch=master)](https://travis-ci.org/nitros12/module-python)

-----

**Table of Contents**

* [Installation](#installation)
* [Getting Started](#getting-started)
* [License](#license)

## Installation

analyticord is distributed on [PyPI](https://pypi.org) as a universal
wheel and is available on Linux/macOS and Windows and supports
Python 3.5+ and PyPy.

```bash
$ pip install analyticord
```

## Getting Started
```python
import asyncio
from analyticord import AnalytiCord

loop = asyncio.get_event_loop()

# The most basic usage, with a single bot token
analytics = AnalytiCord("token")

# start up the analytics
# this could be done inside the on_ready event, etc of a d.py bot
loop.run_until_complete(analytics.start())

# hook the on_message event of a d.py bot
# this will send message count events to analyticord for you
analytics.messages.hook_bot(bot)
```

## License

analyticord is distributed under the terms of the
[MIT License](https://choosealicense.com/licenses/mit).
