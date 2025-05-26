#!/usr/bin/env python3
import sys
import pandas as pd
import yfinance as yf
import os
import time

def update_csv_bulk(csv_file, symbols, batch_size=30):
    """Update CSV with multiple symbols at once"""
    try:
        df_existing = pd.read_csv(csv_file, index_col=0, parse_dates=True)
        # Ensure the index is DateTimeIndex if the file is not empty
        if not df_existing.empty and not isinstance(df_existing.index, pd.DatetimeIndex):
            df_existing.index = pd.to_datetime(df_existing.index)
    except (pd.errors.EmptyDataError, FileNotFoundError):
        df_existing = pd.DataFrame()
    
    initial_columns = list(df_existing.columns)
    processed_new_columns_ordered = [] 
    symbols_to_download = [sym for sym in symbols if sym not in initial_columns]
    
    overall_success_status = True # Initialize the true overall success flag

    if not symbols_to_download:
        print("All requested symbols already exist in CSV or no new symbols requested.")
        if not df_existing.empty:
            try:
                # Even if no new symbols, resave to ensure consistent index/format
                df_existing.to_csv(csv_file) 
                print(f"CSV file {csv_file} resaved (no new symbols to add).")
            except Exception as e:
                print(f"Error resaving existing CSV file: {e}", file=sys.stderr)
                overall_success_status = False # Set the overall flag
        else:
            # Create an empty CSV with Date index if it doesn't exist and no symbols
            try:
                pd.DataFrame(index=pd.to_datetime([])).to_csv(csv_file, index_label="Date")
                print(f"Created empty CSV {csv_file} with Date index.")
            except Exception as e:
                print(f"Error creating empty CSV file: {e}", file=sys.stderr)
                overall_success_status = False
        return overall_success_status
    
    current_df_state = df_existing.copy()
    wait_time_between_batches = 45 # Increased from 2 or other previous values

    failed_symbols_master_list = set() # To keep track of all symbols that ultimately failed

    for i in range(0, len(symbols_to_download), batch_size):
        current_batch_symbols = symbols_to_download[i:i + batch_size]
        if not current_batch_symbols:
            continue

        print(f"Downloading batch of {len(current_batch_symbols)} symbols (e.g., {', '.join(current_batch_symbols[:3])}...)...")
        
        batch_download_successful = False
        batch_df = pd.DataFrame()
        retries = 0
        max_retries = 3 # Max retries for a batch
        timeout_seconds = 30 # Timeout for yf.download itself
        start_date = "2022-01-01"
        end_date = "2024-01-01" # Go up to the start of 2024

        while retries < max_retries:
            try:
                batch_df = yf.download(
                    current_batch_symbols, 
                    start=start_date,
                    end=end_date,
                    auto_adjust=True, # Gets 'Close' as adjusted close
                    timeout=timeout_seconds
                )
                
                # yfinance might return an empty DataFrame or a DataFrame with all NaNs 
                # for failed symbols within a batch, rather than raising an exception for the whole batch.
                # It also might print "X Failed downloads" to stderr.
                # We consider a batch download problematic if the resulting DataFrame is entirely empty.
                if isinstance(batch_df, pd.DataFrame) and batch_df.empty and current_batch_symbols:
                    print(f"Warning: yf.download returned an empty DataFrame for non-empty batch: {current_batch_symbols}. Retry {retries + 1}/{max_retries}...", file=sys.stderr)
                    time.sleep(20 * (retries + 1)) # Wait longer for this generic failure
                    retries += 1
                    overall_success_status = False 
                    continue 
                
                # If yfinance returns a tuple, it usually indicates errors for specific tickers.
                # For simplicity, we'll treat this as a batch failure needing retry.
                if isinstance(batch_df, tuple):
                    print(f"Warning: yf.download returned a tuple (indicates errors) for batch: {current_batch_symbols}. Errors: {batch_df[1]}. Retry {retries + 1}/{max_retries}...", file=sys.stderr)
                    time.sleep(20 * (retries + 1))
                    retries += 1
                    overall_success_status = False
                    continue

                batch_download_successful = True # If we got a DataFrame (even with NaNs)
                break 
            
            except Exception as e:
                # Check for YFRateLimitError by its string representation in type or message
                is_rate_limit_error = "YFRateLimitError" in str(type(e)) or \
                                      "Too Many Request" in str(e) or \
                                      "rate limit" in str(e).lower()

                if is_rate_limit_error:
                    wait_for = 60 * (2**retries) # Exponential backoff: 60s, 120s, 240s
                    print(f"RATE LIMIT ERROR for batch {current_batch_symbols}: {e}. Waiting for {wait_for}s. Retry {retries + 1}/{max_retries}...", file=sys.stderr)
                    time.sleep(wait_for)
                else:
                    print(f"Error downloading batch {current_batch_symbols}: {e}. Retry {retries + 1}/{max_retries}...", file=sys.stderr)
                    time.sleep(15 * (retries + 1)) # General error retry wait
                
                retries += 1
                overall_success_status = False

        if not batch_download_successful:
            print(f"yf.download FAILED for batch: {current_batch_symbols} after all retries. Skipping batch processing.", file=sys.stderr)
            failed_symbols_master_list.update(current_batch_symbols)
            overall_success_status = False
            if i + batch_size < len(symbols_to_download): # If not the last batch
                print(f"Waiting {wait_time_between_batches} seconds before next batch due to previous failure...")
                time.sleep(wait_time_between_batches)
            continue # Move to the next batch

        # --- Batch download attempted, process what we got (batch_df) ---
        temp_batch_data = {}
        batch_symbols_actually_processed_this_batch = []

        # When auto_adjust=True, yf.download typically returns 'Close' prices (adjusted).
        # For multiple tickers, batch_df.columns will be a MultiIndex:
        # Level 0: e.g., 'Close', 'High', 'Low', 'Open', 'Volume'
        # Level 1: Ticker symbols like 'AAPL', 'MSFT'
        # So, batch_df['Close'] would give a DataFrame of close prices with tickers as columns.

        if not isinstance(batch_df.columns, pd.MultiIndex) or 'Close' not in batch_df.columns.get_level_values(0):
            # This case handles if yf.download returns a flat DataFrame (e.g. single symbol)
            # or if 'Close' is not a top-level column name (unexpected for batch with auto_adjust)
            if 'Close' in batch_df.columns and len(current_batch_symbols) == 1: # Single symbol in batch
                symbol_in_batch = current_batch_symbols[0]
                close_prices = batch_df['Close']
                if not close_prices.empty and not close_prices.isnull().all():
                    temp_batch_data[symbol_in_batch] = close_prices.rename(symbol_in_batch)
                    print(f"✓ Symbol {symbol_in_batch} data extracted (single symbol batch).")
                    batch_symbols_actually_processed_this_batch.append(symbol_in_batch)
                else:
                    print(f"✗ No valid 'Close' data for single symbol {symbol_in_batch} in batch. Skipping.", file=sys.stderr)
                    failed_symbols_master_list.add(symbol_in_batch)
                    overall_success_status = False
            else:
                print(f"Warning: 'Close' data not found in expected MultiIndex structure for batch {current_batch_symbols}. Columns: {batch_df.columns}. Skipping processing of this batch's symbols.", file=sys.stderr)
                failed_symbols_master_list.update(current_batch_symbols)
                overall_success_status = False
        else: # Expected MultiIndex structure
            for symbol_in_batch in current_batch_symbols:
                try:
                    if symbol_in_batch in batch_df['Close'].columns:
                        close_prices = batch_df['Close'][symbol_in_batch]
                        if not close_prices.empty and not close_prices.isnull().all():
                            temp_batch_data[symbol_in_batch] = close_prices.rename(symbol_in_batch)
                            print(f"✓ Symbol {symbol_in_batch} data extracted from batch.")
                            batch_symbols_actually_processed_this_batch.append(symbol_in_batch)
                        else:
                            print(f"✗ No valid 'Close' data (empty/all NaN) for {symbol_in_batch} in downloaded batch. Skipping.", file=sys.stderr)
                            failed_symbols_master_list.add(symbol_in_batch)
                            # overall_success_status = False # Don't set to false if other symbols in batch are fine
                except KeyError:
                    print(f"✗ KeyError processing {symbol_in_batch} (likely not in batch_df['Close']). Skipping.", file=sys.stderr)
                    failed_symbols_master_list.add(symbol_in_batch)
                    # overall_success_status = False
                except Exception as e_proc:
                    print(f"✗ Error processing {symbol_in_batch} from batch: {e_proc}. Skipping.", file=sys.stderr)
                    failed_symbols_master_list.add(symbol_in_batch)
                    # overall_success_status = False
        
        if not temp_batch_data:
            print(f"No valid data extracted from any symbol in the batch: {current_batch_symbols}. Batch processing yielded nothing.", file=sys.stderr)
            # If no symbols were processed from this batch, it's a form of failure for these symbols.
            # failed_symbols_master_list should already contain them if individual extractions failed.
            # If overall_success_status is still True, but this batch yielded nothing, mark it.
            if not batch_symbols_actually_processed_this_batch and current_batch_symbols:
                 overall_success_status = False
        else:
            df_batch_processed = pd.DataFrame(temp_batch_data)
            if current_df_state.empty:
                current_df_state = df_batch_processed
            else:
                # Align indexes before joining to handle non-overlapping date ranges smoothly
                current_df_state, df_batch_processed = current_df_state.align(df_batch_processed, join='outer', axis=0)
                current_df_state = current_df_state.combine_first(df_batch_processed) # Fill NaNs from existing with new data
            
            processed_new_columns_ordered.extend(s for s in batch_symbols_actually_processed_this_batch if s not in processed_new_columns_ordered)
            print(f"Batch data for {len(batch_symbols_actually_processed_this_batch)} symbols merged.")

        # Save CSV after each batch processing attempt (even if some symbols in it failed extraction)
        columns_for_saving_intermediate = [col for col in initial_columns if col in current_df_state.columns]
        new_cols_in_df_intermediate = [col for col in processed_new_columns_ordered if col in current_df_state.columns and col not in columns_for_saving_intermediate]
        columns_for_saving_intermediate.extend(new_cols_in_df_intermediate)
        
        # Failsafe: add any other columns present in current_df_state
        for col in current_df_state.columns:
            if col not in columns_for_saving_intermediate:
                columns_for_saving_intermediate.append(col)
        
        if not current_df_state.empty and columns_for_saving_intermediate:
            try:
                current_df_state[columns_for_saving_intermediate].to_csv(csv_file)
                print(f"Intermediate save to {csv_file} successful after processing batch.")
            except Exception as e_intermediate_save:
                print(f"Error during intermediate save to {csv_file}: {e_intermediate_save}", file=sys.stderr)
                overall_success_status = False 
        elif not current_df_state.empty:
            print(f"Warning: DataFrame not empty but no columns identified for intermediate save. State: {len(current_df_state.columns)} cols.", file=sys.stderr)
            overall_success_status = False


        if i + batch_size < len(symbols_to_download): # If there are more batches
            print(f"Waiting {wait_time_between_batches} seconds before next batch...")
            time.sleep(wait_time_between_batches)
    
    # --- Final processing and saving ---
    if failed_symbols_master_list:
         print(f"SUMMARY OF FAILED/SKIPPED SYMBOLS (not downloaded or no data extracted): {sorted(list(failed_symbols_master_list))}", file=sys.stderr)
         if failed_symbols_master_list: # If any symbol failed at any point
             overall_success_status = False


    final_columns_for_dataframe_subset = [col for col in initial_columns if col in current_df_state.columns]
    new_cols_in_df_final = [col for col in processed_new_columns_ordered if col in current_df_state.columns and col not in final_columns_for_dataframe_subset]
    final_columns_for_dataframe_subset.extend(new_cols_in_df_final)
    for col in current_df_state.columns: 
        if col not in final_columns_for_dataframe_subset:
            final_columns_for_dataframe_subset.append(col)

    if not current_df_state.empty and final_columns_for_dataframe_subset:
        try:
            current_df_state[final_columns_for_dataframe_subset].to_csv(csv_file)
            # Check if all *requested new* symbols were actually added to processed_new_columns_ordered
            # and are not in the master failed list.
            all_requested_new_symbols_processed = True
            for sym_req in symbols_to_download:
                if sym_req not in processed_new_columns_ordered or sym_req in failed_symbols_master_list:
                    all_requested_new_symbols_processed = False
                    break
            
            if overall_success_status and all_requested_new_symbols_processed:
                 print(f"✅ All data processed. Final data saved successfully to {csv_file}")
            else:
                # If overall_success_status was true but not all new symbols are there, it's a partial success.
                print(f"⚠️  Data saved to {csv_file}, but some symbols may have failed or not all requested new symbols were added. Check logs and failed symbols list.")
                overall_success_status = False # Ensure it's false for partial success
        except Exception as e_final_save:
            print(f"CRITICAL Error saving final CSV file: {e_final_save}", file=sys.stderr)
            overall_success_status = False
    elif not final_columns_for_dataframe_subset and not current_df_state.empty :
        print(f"Final save SKIPPED: DataFrame is not empty but no columns were identified for saving. This indicates an issue. CSV not updated.", file=sys.stderr)
        overall_success_status = False 
    elif current_df_state.empty and initial_columns: 
        print(f"Warning: Final DataFrame is empty, but the CSV initially contained data. {csv_file} might now be empty or reflect only failed attempts.", file=sys.stderr)
        if overall_success_status: 
            overall_success_status = False 
        try:
            pd.DataFrame(index=pd.to_datetime([])).to_csv(csv_file, index_label="Date")
            print(f"Saved an empty DataFrame to {csv_file} as current state is empty (original data lost).")
        except Exception as e_save_empty:
            print(f"Error saving empty DataFrame after data loss: {e_save_empty}", file=sys.stderr)
            overall_success_status = False
    elif current_df_state.empty and not initial_columns: 
        print(f"Final DataFrame is empty, and the CSV was initially empty or did not exist.")
        if not overall_success_status: # If errors occurred despite ending up empty
             print(f"⚠️  Errors occurred during processing, and the resulting dataset is empty. {csv_file} may be empty or reflect the last state before full failure.")
        # Ensure an empty CSV with Date index exists if it was supposed to be created
        # and no other error has occurred that would make this undesirable.
        if not os.path.exists(csv_file) or (os.path.exists(csv_file) and os.path.getsize(csv_file) == 0):
            try:
                pd.DataFrame(index=pd.to_datetime([])).to_csv(csv_file, index_label="Date")
                print(f"Ensured empty CSV {csv_file} with Date index exists.")
            except Exception as e_create_empty:
                 print(f"Error ensuring empty CSV exists: {e_create_empty}", file=sys.stderr)
                 overall_success_status = False # If creating the placeholder fails, it's an error
    
    return overall_success_status

def update_csv(csv_file, symbol):
    """Single symbol update for backward compatibility"""
    return update_csv_bulk(csv_file, [symbol])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: update_csv.py <csv_file> <symbol>", file=sys.stderr)
        sys.exit(1)
    
    csv_file = sys.argv[1]
    symbol = sys.argv[2]
    success = update_csv(csv_file, symbol)
    sys.exit(0 if success else 1)