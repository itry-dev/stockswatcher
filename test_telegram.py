import sys
import asyncio
from datetime import datetime

# Add backend to path for imports
sys.path.insert(0, 'backend')

from backend.app.telegram_notifier import Telegram, TelegramSettings

async def test_telegram_notification():
    """
    Test Telegram notification by sending a fake stock alert.
    Usage: python test_telegram.py <BOT_TOKEN> <CHAT_ID>
    """
    if len(sys.argv) < 3:
        print("Usage: python test_telegram.py <BOT_TOKEN> <CHAT_ID>")
        print("\nExample:")
        print("  python test_telegram.py 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11 -1001234567890")
        print("\nHow to get credentials:")
        print("  1. BOT_TOKEN: Create a bot via @BotFather on Telegram")
        print("  2. CHAT_ID: Send a message to your bot, then visit:")
        print("     https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates")
        sys.exit(1)

    bot_token = sys.argv[1]
    chat_id = sys.argv[2]

    print(f"Testing Telegram notification...")
    print(f"Bot Token: {bot_token[:20]}...")
    print(f"Chat ID: {chat_id}")
    print("=" * 60)

    try:
        # Create Telegram instance with override settings (enabled=True)
        test_settings = TelegramSettings(enabled=True)
        telegram = Telegram(bot_token, chat_id, settings_override=test_settings)
        
        if not telegram.enabled:
            print("❌ Telegram notifier is disabled")
            return

        # Test 1: Simple alert message
        print("\n📤 Test 1: Sending simple alert...")
        message = """
<b>🔔 Stock Alert Test</b>

<b>Ticker:</b> AAPL
<b>Current Price:</b> $268.47 USD
<b>Target Level:</b> $270.00
<b>Distance:</b> 0.57%

Status: ✅ Near target level

<i>Test sent at {}</i>
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        telegram.send(message)
        print("✅ Simple alert sent successfully!")

        # Test 2: Multiple tickers alert
        print("\n📤 Test 2: Sending multi-ticker alert...")
        multi_message = """
<b>🔔 Multiple Stocks Near Target</b>

📊 <b>AAPL</b>
Price: $268.47 → Target: $270.00
Distance: 0.57% ✅

📊 <b>MSFT</b>
Price: $425.15 → Target: $420.00
Distance: 1.23% ⚠️

📊 <b>GOOGL</b>
Price: $178.92 → Target: $180.00
Distance: 0.60% ✅

<i>Test sent at {}</i>
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        telegram.send(multi_message)
        print("✅ Multi-ticker alert sent successfully!")

        # Test 3: Alert with emojis and formatting
        print("\n📤 Test 3: Sending formatted alert...")
        formatted_message = """
⚠️ <b>PRICE ALERT</b> ⚠️

🏢 <b>Company:</b> Apple Inc.
🎫 <b>Ticker:</b> AAPL
💰 <b>Current Price:</b> $268.47 USD
🎯 <b>Target Level:</b> $270.00
📊 <b>Distance:</b> 0.57%
📈 <b>52W High:</b> $277.32
📉 <b>52W Low:</b> $169.21

🔔 <b>Status:</b> Stock is approaching target level!

⏰ {}
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        telegram.send(formatted_message)
        print("✅ Formatted alert sent successfully!")

        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("\nCheck your Telegram to see the messages.")
        print("If you received all 3 messages, integration is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("  1. Verify your bot token is correct")
        print("  2. Make sure you've started a chat with your bot")
        print("  3. Check that the chat ID is correct (use /getUpdates)")
        print("  4. Ensure your bot has permission to send messages")

if __name__ == "__main__":
    # Run without async since telegram.send() is synchronous
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_telegram_notification())
