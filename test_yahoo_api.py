import sys
import yfinance as yf
import json
from datetime import datetime

if len(sys.argv) < 2:
    print("Usage: python test_yahoo_api.py <TICKER>")
    sys.exit(1)

ticker = sys.argv[1]
output_file = f"yahoo_test_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

print(f"Testing Yahoo Finance API for ticker: {ticker}")
print(f"Output will be saved to: {output_file}")

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"Yahoo Finance API Test for {ticker}\n")
    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
    f.write("=" * 80 + "\n\n")
    
    try:
        stock = yf.Ticker(ticker)
        
        # Test 1: Fast Info
        f.write("=" * 80 + "\n")
        f.write("FAST INFO\n")
        f.write("=" * 80 + "\n")
        try:
            fast_info = stock.fast_info
            f.write(f"Type: {type(fast_info)}\n")
            f.write(f"Dir: {dir(fast_info)}\n\n")
            for attr in dir(fast_info):
                if not attr.startswith('_'):
                    try:
                        value = getattr(fast_info, attr)
                        f.write(f"{attr}: {value}\n")
                    except Exception as e:
                        f.write(f"{attr}: ERROR - {str(e)}\n")
        except Exception as e:
            f.write(f"ERROR accessing fast_info: {str(e)}\n")
        
        # Test 2: Full Info
        f.write("\n" + "=" * 80 + "\n")
        f.write("FULL INFO (stock.info)\n")
        f.write("=" * 80 + "\n")
        try:
            info = stock.info
            f.write(f"Number of keys: {len(info)}\n\n")
            for key, value in sorted(info.items()):
                f.write(f"{key}: {value}\n")
        except Exception as e:
            f.write(f"ERROR accessing info: {str(e)}\n")
        
        # Test 3: History
        f.write("\n" + "=" * 80 + "\n")
        f.write("HISTORY (1d period)\n")
        f.write("=" * 80 + "\n")
        try:
            hist = stock.history(period="1d")
            f.write(f"Shape: {hist.shape}\n")
            f.write(f"Columns: {list(hist.columns)}\n")
            f.write(f"Index: {list(hist.index)}\n\n")
            f.write(str(hist))
            f.write("\n")
        except Exception as e:
            f.write(f"ERROR accessing history: {str(e)}\n")
        
        # Test 4: Financial Statements
        f.write("\n" + "=" * 80 + "\n")
        f.write("INCOME STATEMENT\n")
        f.write("=" * 80 + "\n")
        try:
            income = stock.income_stmt
            f.write(f"Shape: {income.shape if hasattr(income, 'shape') else 'N/A'}\n")
            f.write(str(income))
            f.write("\n")
        except Exception as e:
            f.write(f"ERROR accessing income_stmt: {str(e)}\n")
        
        # Test 5: Recommendations
        f.write("\n" + "=" * 80 + "\n")
        f.write("RECOMMENDATIONS\n")
        f.write("=" * 80 + "\n")
        try:
            recs = stock.recommendations
            f.write(str(recs))
            f.write("\n")
        except Exception as e:
            f.write(f"ERROR accessing recommendations: {str(e)}\n")
        
        # Test 6: All available attributes
        f.write("\n" + "=" * 80 + "\n")
        f.write("ALL TICKER ATTRIBUTES\n")
        f.write("=" * 80 + "\n")
        for attr in dir(stock):
            if not attr.startswith('_'):
                f.write(f"{attr}\n")
        
        print(f"\n✓ Test completed successfully!")
        print(f"Results saved to: {output_file}")
        
    except Exception as e:
        error_msg = f"FATAL ERROR: {str(e)}\n"
        f.write(error_msg)
        print(error_msg)
        import traceback
        traceback.print_exc()
        f.write("\n" + traceback.format_exc())

print(f"\nCheck the output file for detailed results: {output_file}")
