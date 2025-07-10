# shmetro-traffic-enquiry

By WaterCoFire

本脚本可用于查询上海地铁每日的客流数据。数据来源于官方微博发布的信息。 <br>
This script can be used for querying Shanghai Metro daily traffic data. The data is sourced from official Weibo posts.

## Introduction

上海地铁每日客流数据通常会在次日通过官方微博发布。本项目通过抓取并解析上海地铁官方微博（UID: 1742987497）发布的最新动态，提取出指定日期的客流信息。<br>
Shanghai Metro's daily traffic data is typically released the following day via its official Weibo account. This project scrapes and parses the latest updates from the Official Shanghai Metro Weibo (UID: 1742987497) to extract traffic information for a specified date.

## Features

- 查询昨日客流：获取前一天的上海地铁总客流数据。<br>
Query Yesterday's Traffic: Get the total Shanghai Metro traffic data for the previous day.

- 查询指定日期客流：支持查询任意历史日期的客流数据（只要微博有记录）。<br>
Query Traffic on Specific Date: Supports querying traffic data for any historical date (as long as it's recorded on Weibo).

- API 连接测试：提供测试功能，验证与微博 API 的连接是否正常。<br>
API Connection Test: Provides a test function to verify the connection to the Weibo API.

- 各类错误处理机制以及自动重试机制<br>
- Various error handling mechanisms and automatic retry mechanisms

## Dependency

```
pip install requests pytz
```

## Notes

- 本项目依赖于微博的公开 API。微博 API 可能会有访问限制、结构变化或反爬机制，这可能导致程序在未来某个时间点无法正常工作。<br>
This project relies on Weibo's public API. The Weibo API may have access restrictions, structural changes, or anti-scraping mechanisms, which might cause the program to stop working properly at some point in the future.

- 上海地铁的客流数据通常在次日发布，因此无法查询当日的实时客流。<br>
Shanghai Metro traffic data is usually released the next day, so real-time traffic for the current day cannot be queried.

- 在 headers 中设置 User-Agent 是为了模拟浏览器行为，降低被识别为爬虫的风险。如果遇到访问问题，可以尝试更新 User-Agent 为最新的浏览器信息。<br>
Setting User-Agent in headers is to simulate browser behaviour and reduce the risk of being identified as a crawler. If you encounter access issues, try updating the User-Agent to the latest browser information.

- 已被注释掉的 ```time.sleep()``` 可以用来添加请求间的随机延迟，以进一步避免被微博服务器限制。如果频繁遇到请求失败，可以考虑启用并调整此项。<br>
Random Delay: The commented ```time.sleep()``` can be used to add random delays between requests to further avoid being restricted by the Weibo server. If you frequently encounter request failures, consider enabling and adjusting this.

## Contribution

Contributions of any kind are welcome! If you have suggestions for improvement, find a bug, or want to add a new feature, please feel free to submit a Pull Request or create an Issue.

## License

This project is licensed under the MIT License.