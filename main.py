import requests
import re
import json
from datetime import datetime, timedelta
import pytz

# 获取目标日期客流数据
# Get traffic data on the target date
def get_traffic(target_date):
    try:
        target_datetime = datetime.strptime(target_date, "%Y-%m-%d")
        post_date = target_datetime + timedelta(days=1)
        beijing_tz = pytz.timezone('Asia/Shanghai')
        post_date = beijing_tz.localize(post_date)
        print(f"目标日期 Target date: {target_date}")
        print(f"预期微博发布日期 Expected Weibo post date: {post_date.strftime('%Y-%m-%d')}")
    except ValueError:
        return "❌ 日期格式错误\n❌ Wrong date format"

    base_url = "https://m.weibo.cn/api/container/getIndex"
    params = {
        "uid": "1742987497",
        "type": "uid",
        "containerid": "1076031742987497",
        "page": 0
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Referer": "https://m.weibo.cn/u/1742987497",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        page = 0
        beijing_tz = pytz.timezone('Asia/Shanghai')

        while True:
            params["page"] = page
            print(f"\n🔧 请求数据 Requesting data: Page {page + 1}...")

            # 重试机制
            # Retry mechanism
            max_retries = 3
            data = None
            for attempt in range(max_retries):
                try:
                    # 可以在此添加随机延迟避免被限制
                    # You may add random delays to avoid being restricted
                    # time.sleep(1.5 + attempt * 1.0)

                    response = requests.get(base_url, params=params, headers=headers, timeout=15)
                    response.raise_for_status()

                    # 检查响应内容
                    # Check response
                    if not response.text.strip():
                        print("⚠️ 收到空响应内容\n⚠️ Empty response received")
                        if attempt < max_retries - 1:
                            continue
                        else:
                            return "❌ 服务器返回空响应\n❌ Server returned empty response"

                    data = response.json()

                    # 检查 API 状态
                    # Check API status
                    if data.get("ok") == 1:
                        print(f"✅ API 响应正常，保存到: weibo_response_page_{page}.json\n✅ API response is normal, saved to: weibo_response_page_{page}.json")
                        break
                    else:
                        print(f"⚠️ API 返回错误状态: ok={data.get('ok')}, msg={data.get('msg', '无消息')}\n⚠️ API returns error status: ok={data.get('ok')}, msg={data.get('msg', '无消息')}")
                        if attempt < max_retries - 1:
                            print(f"♻️ 重试中 Retrying... ({attempt + 1}/{max_retries})")
                        else:
                            print("❌ API 连续失败，跳过此页\n❌ API failed repeatedly, skipping this page")
                            return f"❌ 微博 API 错误: ok={data.get('ok')}, msg={data.get('msg')}\n❌ Weibo API error: ok={data.get('ok')}, msg={data.get('msg')}"

                except requests.exceptions.RequestException as e:
                    print(f"❌ 请求异常 Request exception: {str(e)}")
                    if attempt < max_retries - 1:
                        print(f"♻️ 重试中 Retrying... ({attempt + 1}/{max_retries})")
                    else:
                        return f"❌ 网络请求失败 Network request failed: {str(e)}"
                except json.JSONDecodeError:
                    print(f"❌ JSON 解析失败，原始响应如下:\n❌ JSON parsing failed. Original response:\n{response.text[:500]}...")
                    if attempt < max_retries - 1:
                        print(f"♻️ 重试中 Retrying... ({attempt + 1}/{max_retries})")
                    else:
                        return "❌ 服务器返回非 JSON 响应\n❌ Server returns a non-JSON response"

            # 如果没有获取到数据，跳过此页
            # Skip this page if no data is obtained
            if not data or data.get("ok") != 1:
                page += 1
                continue

            # 解析微博数据
            # Analysing Weibo data
            cards = data.get("data", {}).get("cards", [])
            if not cards:
                print("❌ 没有找到任何微博卡片数据，可能原因: 微博 API 限制或结构变化\n❌ No Weibo card data found, possible reasons: Weibo API restrictions or structural changes")
                page += 1
                continue

            print(f"📄 Page {page + 1} - 找到微博数量 Weibo posts found: {len(cards)}")

            # 处理当前页的所有微博
            # Process all Weibo posts on the current page
            for i, card in enumerate(cards):
                if card.get("card_type") != 9:
                    continue

                mblog = card.get("mblog", {})
                created_at = mblog.get("created_at", "")
                text = mblog.get("text", "")
                bid = mblog.get("bid", "")

                if not text:
                    continue

                try:
                    weibo_datetime = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
                    weibo_datetime = weibo_datetime.astimezone(beijing_tz)
                    weibo_date_str = weibo_datetime.strftime("%Y-%m-%d")
                except ValueError:
                    continue

                print(f"\n⏰ 帖子 Post {i + 1} [ID:{bid}]")
                print(f"   发布日期 Date: {weibo_date_str}")
                print(f"   内容摘要 Summary: {text[:60]}...")

                if weibo_datetime.date() < post_date.date():
                    print(f"⚠️ 已超过发布日期\n⚠️ Release date exceeded")
                    return f"❌ 未找到 {target_date} 的客流数据\n❌ Traffic for {target_date} not found"

                pattern = r"(\d{1,2})月\s?(\d{1,2})日上海地铁总客流为(\d+)万人次"
                match = re.search(pattern, text)

                if match:
                    month, day, count = match.groups()
                    data_date_str = f"{month}/{day}"
                    print(f"✅ 找到客流数据 Found traffic data - 日期 Date: {data_date_str}, 客流 Traffic: {count} 万 / × 10k")

                    if int(month) == target_datetime.month and int(day) == target_datetime.day:
                        return int(count)

            page += 1
            print(f"\n前往 Going to: Page {page + 1}...")

        return f"❌ 未找到 {target_date} 的客流数据\nTraffic for {target_date} not found"

    except Exception as e:
        return f"❌ 查询失败 Query failed: {str(e)}"


# 用户交互界面
# User interface
def main_menu():
    print("\n" + "=" * 60)
    print("上海地铁客流查询系统 Shanghai Metro Traffic Enquiry System")
    print("=" * 60)
    print("1. 查询昨日客流\n   Traffic yesterday")
    print("2. 查询指定日期客流\n   Traffic on a specific date")
    print("3. 退出系统\n   Quit the system")
    print("4. 测试 API 连接\n   Test API connection")

    choice = input("\n请选择操作 Select operation (1-4): ")
    return choice

# 测试微博 API 连接
# Test Weibo API connection
def test_api_connection():
    print("\n=== 微博 API 连接测试 Weibo API connection test ===")
    url = "https://m.weibo.cn/api/container/getIndex"
    params = {
        "uid": "1742987497",
        "type": "uid",
        "containerid": "1076031742987497",
        "page": 0
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Referer": "https://m.weibo.cn/u/1742987497"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        # 保存响应内容
        # Save response
        with open("api_test_response.json", "w", encoding="utf-8") as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=2)

        print("✅ API 测试成功，响应已保存到 api_test_response.json\n✅ API test success, response saved to api_test_response.json")
        print(f"HTTP 状态码 Status code: {response.status_code}")
        print("请检查该文件以确定 API 是否返回有效数据\nCheck this file to determine whether the API returns valid data")

    except Exception as e:
        print(f"❌ API 测试失败 Test failed: {str(e)}")


if __name__ == "__main__":
    while True:
        choice = main_menu()

        if choice == "1":
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            print(f"\n=== 开始查询昨日客流数据 Querying traffic yesterday ({yesterday}) ===")
            result = get_traffic(yesterday)

            if isinstance(result, int):
                print(f"\n🎉 查询成功 Query success: {yesterday}\n上海地铁总客流为: {result} 万人次\nTraffic in Shanghai Metro: {result} × 10k")
            else:
                print(f"\n{result}")

        elif choice == "2":
            while True:
                query_date = input("\n请输入查询日期 Enter the date (YYYY-MM-DD): ").strip()
                try:
                    # 验证日期格式
                    # Validate date format
                    query_datetime = datetime.strptime(query_date, "%Y-%m-%d")

                    # 确保不是未来日期
                    # Make sure it's not future date
                    if query_datetime > datetime.now():
                        print("❌ 不能查询未来日期的数据\n❌ Unable to query data for future dates")
                        continue

                    # 确保不是今天
                    # Make sure it's not today
                    if query_datetime.date() == datetime.now().date():
                        print("❌ 不能查询今日数据\n❌ Unable to query data for today")
                        continue

                    break
                except ValueError:
                    print("❌ 日期格式错误，请使用 YYYY-MM-DD 格式\n❌ Wrong date format, use the format YYYY-MM-DD")

            print(f"\n=== 开始查询客流数据 Querying traffic data ({query_date}) ===")
            result = get_traffic(query_date)

            if isinstance(result, int):
                print(f"\n🎉 查询成功 Query success: {query_date}\n上海地铁总客流为: {result} 万人次\nTraffic in Shanghai Metro: {result} × 10k")
            else:
                print(f"\n{result}")

        elif choice == "3":
            print("\n感谢使用，再见！\nThank you for using, goodbye!")
            break

        elif choice == "4":
            test_api_connection()

        else:
            print("\n❌ 无效选择\n❌ Invalid choice")

        input("\n按回车键继续 Press Enter to continue")