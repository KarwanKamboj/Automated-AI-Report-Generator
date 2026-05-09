import asyncio
from services.data_processing import process_file
from services.visualization import generate_charts
from services.ai_insights import get_ai_insights
from services.pdf_generator import generate_pdf_report
import pandas as pd
import numpy as np

async def test():
    # Create dummy data with NaNs and single values
    df = pd.DataFrame({
        'num1': [1, np.nan, 3, 4, 5],
        'num2': [1, 1, 1, 1, 1], # Constant
        'cat1': ['A', 'B', np.nan, 'A', 'B']
    })
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    
    try:
        print("1. process_file")
        summary_dict, df_processed = process_file(csv_bytes, "test.csv")
        if summary_dict["status"] == "error":
            print("process_file error:", summary_dict["message"])
            return
            
        print("2. generate_charts")
        charts = generate_charts(df_processed)
        
        print("3. get_ai_insights")
        # Just test serialization
        import json
        json.dumps(summary_dict)
        
        print("SUCCESS")
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(test())
